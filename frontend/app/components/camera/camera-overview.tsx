import React, { type ReactElement, useEffect, useState } from "react";
import {
    createCam,
    deleteCam,
    getCams,
    patchCam,
    patchDartboard,
} from "@/app/services/api";
import { notifications } from "@mantine/notifications";
import { Button, Group, Modal, SimpleGrid, Stack } from "@mantine/core";
import { CameraCard } from "./camera-card";
import { IconPlus } from "@tabler/icons-react";
import { useDisclosure } from "@mantine/hooks";
import { CreateCamForm, type CamCreateFunction } from "./create-form";
import {
    type DartboardPatchSchema,
    type CamCreateSchema,
    type CamSchema,
    type DartboardSchema,
    type CamPatchSchema,
} from "@/app/types/schemas";
import { CreateSimForm } from "./create-sim-form";

/**
 * Properties for CamOverview
 */
export interface CameraOverviewProps {
    dartboard: DartboardSchema | undefined;
    setDartboard: (dartboard: DartboardSchema) => void;
}

/**
 * Component to show all cameras of given dartboard.
 * For each camera one CameraCard is created and shown in a grid.
 * @param param0 dartboard schema
 * @returns React component
 */
export function CameraOverview({
    dartboard,
    setDartboard,
}: CameraOverviewProps): ReactElement {
    // Create modal state
    const [createModalState, createModalHandler] = useDisclosure(false);
    const [createModalStateSim, createModalHandlerSim] = useDisclosure(false);

    // retrieve all cams
    const [cams, setCams] = useState<CamSchema[]>([]);
    useEffect(() => {
        getCams(dartboard?.cams)
            .then((response) => {
                setCams(response.data);
            })
            .catch((error) => {
                notifications.show({
                    title: "Connection error",
                    message: "Could not retrieve Boards: " + error,
                    color: "red",
                });
            });
    }, []);
    // Create Cam and close modal
    const createCamFunc: CamCreateFunction = (
        values: CamCreateSchema,
    ): void => {
        createCam(values)
            .then((response) => {
                const newCams: CamSchema[] = cams.concat(response.data);
                setCams(newCams);
                // patch dartboard
                const patchData: DartboardPatchSchema = {
                    cams: newCams.map((cam) => cam.id),
                };
                patchDartboard(dartboard?.id, patchData)
                    .then((response) => {
                        setDartboard(response.data);
                    })
                    .catch((error) => {
                        notifications.show({
                            title: "Patch error",
                            message: "Could not patch Dartboard: " + error,
                            color: "red",
                        });
                    });
            })
            .catch((error) => {
                notifications.show({
                    title: "Post error",
                    message: "Could not create Cam: " + error,
                    color: "red",
                });
            });

        createModalHandler.close();
    };
    // Function to update cam via api
    const patchCamFunc = (id: string, patchData: CamPatchSchema): void => {
        patchCam(id, patchData)
            .then((response) => {
                const updatedCam = response.data;
                const updatedCams = cams.map((cam, i) => {
                    if (cam.id === updatedCam.id) {
                        return updatedCam;
                    } else {
                        return cam;
                    }
                });
                setCams(updatedCams);
                notifications.show({
                    title: "Sucessfull",
                    message: "Updated Cam",
                    color: "green",
                });
            })
            .catch((error) => {
                notifications.show({
                    title: "Patch error",
                    message: "Could not update Cam: " + error,
                    color: "red",
                });
            });
    };

    // Delete dartboard
    const deleteCamFunc = (key: string): void => {
        deleteCam(key)
            .then((response) => {
                const newCams: CamSchema[] = cams.filter((cam) => {
                    return cam.id !== key;
                });
                setCams(newCams);
                // Patch Dartboard
                const patchData: DartboardPatchSchema = {
                    cams: newCams.map((cam) => cam.id),
                };
                patchDartboard(dartboard?.id, patchData)
                    .then((response) => {
                        setDartboard(response.data);
                    })
                    .catch((error) => {
                        notifications.show({
                            title: "Patch error",
                            message: "Could not patch Dartboard: " + error,
                            color: "red",
                        });
                    });
            })
            .catch((error) => {
                notifications.show({
                    title: "Delete error",
                    message: "Could not delete cam: " + error,
                    color: "red",
                });
            });
    };

    return (
        <Stack>
            <Group justify="end" m="md">
                {/** Add Camera */}
                <Button
                    leftSection={<IconPlus />}
                    onClick={createModalHandler.open}
                >
                    Add Camera
                </Button>
                <Modal
                    opened={createModalState}
                    onClose={createModalHandler.close}
                    title="Add Camera"
                    centered
                >
                    <CreateCamForm submit={createCamFunc} existingCams={cams} />
                </Modal>
                {/** Add Simulation (maybe delete later) */}
                <Button
                    leftSection={<IconPlus />}
                    onClick={createModalHandlerSim.open}
                >
                    Add Simulation
                </Button>
                <Modal
                    opened={createModalStateSim}
                    onClose={createModalHandlerSim.close}
                    title="Add Simulation"
                    centered
                >
                    <CreateSimForm submit={createCamFunc} />
                </Modal>
            </Group>
            <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} m="md">
                {cams.map((cam) => (
                    <CameraCard
                        key={cam.id}
                        cam={cam}
                        deleteFunc={deleteCamFunc}
                        patchFunc={patchCamFunc}
                    />
                ))}
            </SimpleGrid>
        </Stack>
    );
}
