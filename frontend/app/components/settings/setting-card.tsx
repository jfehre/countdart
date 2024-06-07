import {
    type DartboardPatchSchema,
    type AllConfigSchema,
} from "@/app/types/schemas";
import React, { type ReactElement } from "react";
import { Button, Card, Group, SimpleGrid, Text } from "@mantine/core";
import { SettingComponent } from "./setting-component";

/**
 * Properties for a settings card
 * Contains key, the config schema and a on change function
 * to update changes in db
 */
export interface SettingCardProps {
    configs: AllConfigSchema[] | undefined;
    title: string;
    patchFunc: (patchData: DartboardPatchSchema) => void;
}

/**
 * Settings Card
 * @param param0 properties
 * @returns React component for one setting
 */
export function SettingCard({
    configs,
    title,
    patchFunc,
}: SettingCardProps): ReactElement | null {
    // return specific settings type component
    if (configs === undefined) {
        return null;
    } else {
        return (
            <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Card.Section withBorder inheritPadding py="xs">
                    <Text fw={500}>{title}</Text>
                </Card.Section>
                <Card.Section>
                    <SimpleGrid cols={{ base: 1 }} m="lg">
                        {configs?.map((config, index) => {
                            return (
                                <SettingComponent
                                    config={config}
                                    key={index}
                                    onChange={() => {}}
                                />
                            );
                        })}
                    </SimpleGrid>
                    <Group p="md" justify="flex-end">
                        <Button
                            onClick={() => {
                                const patchData: DartboardPatchSchema = {
                                    op_configs: { [title]: configs },
                                };
                                patchFunc(patchData);
                            }}
                        >
                            Apply
                        </Button>
                    </Group>
                </Card.Section>
            </Card>
        );
    }
}
