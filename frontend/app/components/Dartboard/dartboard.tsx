import { ActionIcon, Badge, Card, Group, Menu, Text } from "@mantine/core";
import Link from "next/link";
import React, { type ReactElement } from "react";
import styles from "./Dartboard.module.css";
import {
    IconDotsVertical,
    IconPlayerPlay,
    IconTrash,
} from "@tabler/icons-react";
import { type DartboardSchema } from "@/app/types/schemas";

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
                        <Badge color={dartboard.active ? "green" : "red"}>
                            {dartboard.active ? "active" : "inactive"}
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
                        onClickCapture={(e: React.MouseEvent) => {
                            e.preventDefault();
                        }}
                        variant="subtle"
                    >
                        <IconPlayerPlay />
                    </ActionIcon>
                </Group>
            </Card.Section>
        </Card>
    );
}
