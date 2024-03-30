import { Badge, Card, Group, Text } from "@mantine/core";
import Link from "next/link";
import React, { type ReactElement } from "react";
import styles from "./Dartboard.module.css";

export interface DartboardProps {
    name: string;
    active: boolean;
    id: number;
}

export function Dartboard(
    dartboard: DartboardProps,
    key: number,
): ReactElement {
    return (
        <Card
            className={styles.card}
            component={Link}
            href={`/boardmanager/${dartboard.id}`}
            shadow="sm"
            padding="lg"
            radius="md"
            withBorder
            key={key}
        >
            <Card.Section>
                <Group justify="space-between" m="md">
                    <Text>{dartboard.name}</Text>
                    <Badge color={dartboard.active ? "green" : "red"}>
                        {dartboard.active ? "active" : "inactive"}
                    </Badge>
                </Group>
            </Card.Section>
        </Card>
    );
}
