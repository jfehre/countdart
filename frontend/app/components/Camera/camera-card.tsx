import { Card, Group, Badge, Text, Menu, ActionIcon } from "@mantine/core";
import React, { useState, type ReactElement } from "react";
import {
    IconDotsVertical,
    IconPlayerPlay,
    IconPlayerStop,
    IconSettings,
    IconTrash,
} from "@tabler/icons-react";
import { WebSocketStream } from "./websocket-stream";
import { startCam, stopCam } from "@/app/services/api";
import { notifications } from "@mantine/notifications";
import { type CamSchema } from "@/app/types/schemas";

/**
 * Properties for the CameraCard
 */
export interface CameraCardProps {
    cam: CamSchema;
    deleteFunc: (id: string) => void;
}

/**
 * Component to show a camera object within a card
 * @param param0 cam schema and delete function
 * @returns React Card Component
 */
export function CameraCard({ cam, deleteFunc }: CameraCardProps): ReactElement {
    const [isActive, setIsActive] = useState(cam.active);

    // Function to start camera via api. On error notification is shown
    const startCamFunc = (): void => {
        startCam(cam.id)
            .then((response) => {
                cam = response.data;
                setIsActive(true);
            })
            .catch((error) => {
                notifications.show({
                    title: "Error",
                    message: "Could not start cam: " + error,
                    color: "red",
                });
            });
    };

    // Function to stop camera via api. On error notification is shown
    const stopCamFunc = (): void => {
        stopCam(cam.id)
            .then((response) => {
                cam = response.data;
                setIsActive(false);
            })
            .catch((error) => {
                notifications.show({
                    title: "Error",
                    message: "Could not stop cam: " + error,
                    color: "red",
                });
            });
    };

    // Function to start stop camera with icon. Will call api
    const toggleStartStop = (): void => {
        if (isActive) {
            stopCamFunc();
        } else {
            startCamFunc();
        }
    };

    return (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Card.Section>
                {/* Header is showing the camera stream */}
                <WebSocketStream height={200} camId={cam.id} />
            </Card.Section>
            <Card.Section>
                {/* display cam name, menu and badges */}
                <Group
                    justify="space-between"
                    ml="md"
                    mr="md"
                    mt="md"
                    wrap="nowrap"
                    align="top"
                >
                    <Text>{cam.card_name}</Text>
                    <Menu position="bottom-end">
                        <Menu.Target>
                            <ActionIcon
                                onClickCapture={(e: React.MouseEvent) => {
                                    e.preventDefault();
                                }}
                                variant="subtle"
                            >
                                <IconDotsVertical />
                            </ActionIcon>
                        </Menu.Target>
                        <Menu.Dropdown>
                            <Menu.Item
                                color="red"
                                leftSection={<IconTrash />}
                                onClick={(e: React.MouseEvent) => {
                                    deleteFunc(cam.id);
                                    e.preventDefault();
                                }}
                            >
                                Delete
                            </Menu.Item>
                        </Menu.Dropdown>
                    </Menu>
                </Group>
                <Group ml="md" mr="md">
                    <Badge color={isActive ? "green" : "red"}>
                        {isActive ? "active" : "inactive"}
                    </Badge>
                    <Badge color={isActive ? "green" : "red"}>
                        {isActive ? "calibrated" : "uncalibrated"}
                    </Badge>
                </Group>
            </Card.Section>
            <Card.Section mt="xl">
                {/* display start stop function */}
                <Group justify="space-between" m="md">
                    <ActionIcon
                        onClick={(e: React.MouseEvent) => {
                            toggleStartStop();
                            e.preventDefault();
                        }}
                        variant="subtle"
                    >
                        <IconPlayerPlay
                            visibility={isActive ? "hidden" : "visible"}
                            display={isActive ? "None" : "block"}
                        />
                        <IconPlayerStop
                            visibility={isActive ? "visible" : "hidden"}
                            display={isActive ? "block" : "None"}
                        />
                    </ActionIcon>
                    <ActionIcon
                        onClickCapture={(e: React.MouseEvent) => {
                            e.preventDefault();
                        }}
                        variant="subtle"
                    >
                        <IconSettings />
                    </ActionIcon>
                </Group>
            </Card.Section>
        </Card>
    );
}
