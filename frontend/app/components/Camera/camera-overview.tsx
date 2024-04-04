import React, { type ReactElement, useEffect, useState } from "react";
import { type DartboardSchema } from "../Dartboard/dartboard";
import { createCam, deleteCam, getCams } from "@/app/services/api";
import { notifications } from "@mantine/notifications";
import { Button, Group, Modal, SimpleGrid, Stack } from "@mantine/core";
import { CameraCard } from "./camera-card";
import { IconPlus } from "@tabler/icons-react";
import { useDisclosure } from "@mantine/hooks";
import {
    CreateCamForm,
    type CamCreateFunction,
    type CamCreateSchema,
} from "./create-form";

export interface CamSchema {
    card_name: string;
    active: boolean;
    hardware_id: number;
    id: string;
}

export interface CamHardwareSchema {
    card_name: string;
    hardware_id: number;
}

export interface CameraOverviewProps {
    dartboard: DartboardSchema | undefined;
}

export function CameraOverview({
    dartboard,
}: CameraOverviewProps): ReactElement {
    // Create modal state
    const [createModalState, createModalHandler] = useDisclosure(false);

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

    // Delete dartboard
    const deleteCamFunc = (key: string): void => {
        deleteCam(key)
            .then((response) => {
                const newCams: CamSchema[] = cams.filter((cam) => {
                    return cam.id !== key;
                });
                setCams(newCams);
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
                    <CreateCamForm submit={createCamFunc} />
                </Modal>
            </Group>
            <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} m="md">
                {cams.map((cam) => (
                    <CameraCard
                        key={cam.id}
                        cam={cam}
                        deleteFunc={deleteCamFunc}
                    />
                ))}
            </SimpleGrid>
        </Stack>
    );
}
