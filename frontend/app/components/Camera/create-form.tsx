import React, { useEffect, type ReactElement, useState } from "react";
import { useForm } from "@mantine/form";
import { Stack, Button, Group, NativeSelect } from "@mantine/core";
import { getCamsHardware } from "@/app/services/api";
import { notifications } from "@mantine/notifications";
import {
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
}

/**
 * Form to create a new camera
 * @param param0 submit function
 * @returns React form
 */
export function CreateCamForm({ submit }: CreateCamFormProps): ReactElement {
    // create mantine form
    const form = useForm({
        initialValues: {
            card_name: "",
            hardware_id: -1,
        },
    });

    // retrieve available hardware cams
    const [hardwareCams, setHardwareCams] = useState<CamHardwareSchema[]>([]);
    useEffect(() => {
        getCamsHardware()
            .then((response) => {
                setHardwareCams(response.data);
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
        const chosenCam = hardwareCams.find(
            (hardwareCam) => hardwareCam.card_name === values.card_name,
        );
        if (chosenCam === undefined) {
            notifications.show({
                title: "Something went wrong",
                message:
                    "The chosen hardware camera is not in the initial list",
                color: "red",
            });
            return;
        }
        values.hardware_id = chosenCam.hardware_id;
        submit(values);
    };

    return (
        <Stack>
            <form onSubmit={form.onSubmit(submitWrapper)}>
                <NativeSelect
                    label="Camera"
                    data={hardwareCams.map((hardwareCam) => {
                        return hardwareCam.card_name;
                    })}
                    {...form.getInputProps("card_name")}
                />

                <Group justify="flex-end" mt="md">
                    <Button type="submit">Create</Button>
                </Group>
            </form>
        </Stack>
    );
}
