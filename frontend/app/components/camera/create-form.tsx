import React, { useEffect, type ReactElement, useState } from "react";
import { useForm } from "@mantine/form";
import { Stack, Button, Group, NativeSelect } from "@mantine/core";
import { getCamsHardware } from "@/app/services/api";
import { notifications } from "@mantine/notifications";
import {
    type CamSchema,
    type CamCreateSchema,
    type CamHardwareSchema,
} from "@/app/types/schemas";

/**
 * Create function props which is called on submit
 */
export type CamCreateFunction = (values: CamCreateSchema) => void;

/**
 * Properties for CreateCamForm
 */
interface CreateCamFormProps {
    submit: CamCreateFunction;
    existingCams: CamSchema[];
}

/**
 * Form to create a new camera
 * @param param0 submit function
 * @returns React form
 */
export function CreateCamForm({
    submit,
    existingCams,
}: CreateCamFormProps): ReactElement {
    // create mantine form
    const form = useForm({
        initialValues: {
            name: "",
            source: -1,
            type: "USBCam",
        },
    });

    // retrieve available hardware cams
    const [hardwareCams, setHardwareCams] = useState<CamHardwareSchema[]>([]);
    useEffect(() => {
        getCamsHardware()
            .then((response) => {
                let newHardwareCams = response.data;
                // remove all hardware cams with same hardware id as in existing cams
                const existingHardwareIds = existingCams.map(
                    (cam) => cam.source,
                );
                newHardwareCams = newHardwareCams.filter((hardwareCam) => {
                    return !existingHardwareIds.includes(hardwareCam.source);
                });
                console.log(newHardwareCams);
                // check if cams are not undefined and more than 0
                if (
                    newHardwareCams !== undefined &&
                    newHardwareCams.length > 0
                ) {
                    // set cams
                    setHardwareCams(newHardwareCams);
                    // set initial value
                    form.setValues({
                        name:
                            newHardwareCams[0].name +
                            " " +
                            newHardwareCams[0].source,
                        source: newHardwareCams[0].source,
                    });
                }
            })
            .catch((error) => {
                notifications.show({
                    title: "Connection error",
                    message: "Could not retrieve hardware cams: " + error,
                    color: "red",
                });
            });
    }, []);

    // submit wrapper to add other values into data
    // based on selected cam
    const submitWrapper = (values: CamCreateSchema): void => {
        // find hardware cam from native select value
        const chosenCam = hardwareCams.find(
            (hardwareCam) =>
                hardwareCam.name + " " + hardwareCam.source === values.name,
        );
        if (chosenCam === undefined) {
            notifications.show({
                title: "Something went wrong",
                message: `The chosen hardware camera ${values.name} is not in the initial list`,
                color: "red",
            });
            return;
        }
        // update values with hardware cam
        values.name = chosenCam.name;
        values.source = chosenCam.source;
        submit(values);
    };

    return (
        <Stack>
            <form onSubmit={form.onSubmit(submitWrapper)}>
                <NativeSelect
                    label="Camera"
                    data={hardwareCams.map((hardwareCam) => {
                        // use card name + hardware id as value
                        return hardwareCam.name + " " + hardwareCam.source;
                    })}
                    {...form.getInputProps("name")}
                />

                <Group justify="flex-end" mt="md">
                    <Button type="submit">Create</Button>
                </Group>
            </form>
        </Stack>
    );
}
