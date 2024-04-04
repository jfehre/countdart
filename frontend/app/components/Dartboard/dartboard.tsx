import { ActionIcon, Badge, Card, Group, Menu, Text } from "@mantine/core";
import Link from "next/link";
import React, { type ReactElement } from "react";
import styles from "./Dartboard.module.css";
import {
    IconDotsVertical,
    IconPlayerPlay,
    IconTrash,
} from "@tabler/icons-react";

export interface DartboardProps {
    name: string;
    active: boolean;
    id: string;
}

export interface DartboardUIProps {
    dartboard: DartboardProps;
    deleteFunc: (id: string) => void;
}

export function Dartboard({
    dartboard,
    deleteFunc,
}: DartboardUIProps): ReactElement {
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
