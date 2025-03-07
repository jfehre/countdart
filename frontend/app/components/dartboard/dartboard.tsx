import { ActionIcon, Badge, Card, Group, Menu, Text } from "@mantine/core";
import Link from "next/link";
import React, { useState, type ReactElement } from "react";
import styles from "./Dartboard.module.css";
import { IconDotsVertical, IconTrash } from "@tabler/icons-react";
import { type DartboardSchema } from "@/app/types/schemas";
import { StartStopButton } from "./start-stop-button";

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
                    <StartStopButton
                        dartboard={dartboard}
                        isActive={isActive}
                        setIsActive={setIsActive}
                        asIcon={true}
                    />
                </Group>
            </Card.Section>
        </Card>
    );
}
