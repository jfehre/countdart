import {
    Card,
    Group,
    Badge,
    Text,
    Menu,
    ActionIcon,
    Image,
} from "@mantine/core";
import React, { type ReactElement } from "react";
import { type CamSchema } from "./camera-overview";
import {
    IconDotsVertical,
    IconPlayerPlay,
    IconSettings,
    IconTrash,
} from "@tabler/icons-react";

export interface CameraCardProps {
    cam: CamSchema;
    deleteFunc: (id: string) => void;
}

export function CameraCard({ cam, deleteFunc }: CameraCardProps): ReactElement {
    return (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Card.Section>
                <Image src="/images/no_image.webp" alt="preview_image" />
            </Card.Section>
            <Card.Section>
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
                    <Badge color={cam.active ? "green" : "red"}>
                        {cam.active ? "active" : "inactive"}
                    </Badge>
                    <Badge color={cam.active ? "green" : "red"}>
                        {cam.active ? "calibrated" : "uncalibrated"}
                    </Badge>
                </Group>
            </Card.Section>
            <Card.Section mt="xl">
                <Group justify="space-between" m="md">
                    <ActionIcon
                        onClickCapture={(e: React.MouseEvent) => {
                            e.preventDefault();
                        }}
                        variant="subtle"
                    >
                        <IconPlayerPlay />
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
