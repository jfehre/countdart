import { ActionIcon, Badge, Card, Group, Menu, Text } from "@mantine/core";
import Link from "next/link";
import React, { useState, type ReactElement } from "react";
import styles from "./Dartboard.module.css";
import {
    IconDotsVertical,
    IconPlayerPlay,
    IconPlayerStop,
    IconTrash,
} from "@tabler/icons-react";
import { type DartboardSchema } from "@/app/types/schemas";
import { startDartboard, stopDartboard } from "@/app/services/api";
import { notifications } from "@mantine/notifications";

/**
 * Properties for Dartboard component
 */
export interface DartboardProps {
    dartboard: DartboardSchema;
    deleteFunc: (id: string) => void;
}

/**
 * Component for Dartboard. Will show each dartboard and its information and
 * details in a card.
 * @param param0 dartboard and delete function
 * @returns React Card Component
 */
export function Dartboard({
    dartboard,
    deleteFunc,
}: DartboardProps): ReactElement {
    const [isActive, setIsActive] = useState(dartboard.active);

    // Function to start dartboard via api. On error notification is shown
    const startDartboardFunc = (): void => {
        startDartboard(dartboard.id)
            .then((response) => {
                dartboard = response.data;
                setIsActive(true);
            })
            .catch((error) => {
                notifications.show({
                    title: "Error",
                    message: "Could not start dartboard: " + error,
                    color: "red",
                });
            });
    };

    // Function to stop dartboard via api. On error notification is shown
    const stopDartboardFunc = (): void => {
        stopDartboard(dartboard.id)
            .then((response) => {
                dartboard = response.data;
                setIsActive(false);
            })
            .catch((error) => {
                notifications.show({
                    title: "Error",
                    message: "Could not stop dartboard: " + error,
                    color: "red",
                });
            });
    };

    // Function to start stop camera with icon. Will call api
    const toggleStartStop = (): void => {
        if (isActive) {
            stopDartboardFunc();
        } else {
            startDartboardFunc();
        }
    };
    return (
        <Card
            className={styles.card}
            component={Link}
            href={`/boardmanager/${dartboard.id}`}
            shadow="sm"
            padding="lg"
            radius="md"
            withBorder
        >
            <Card.Section>
                {/* Header with name and menu */}
                <Group justify="space-between" m="md">
                    <Group>
                        <Text>{dartboard.name}</Text>
                        <Badge color={isActive ? "green" : "red"}>
                            {isActive ? "active" : "inactive"}
                        </Badge>
                    </Group>
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
                                    deleteFunc(dartboard.id);
                                    e.preventDefault();
                                }}
                            >
                                Delete
                            </Menu.Item>
                        </Menu.Dropdown>
                    </Menu>
                </Group>
            </Card.Section>
            <Card.Section>
                {/* Footer with start stop button */}
                <Group m="md">
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
                </Group>
            </Card.Section>
        </Card>
    );
}
