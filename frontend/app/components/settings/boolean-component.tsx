import {
    type AllConfigSchema,
    type BooleanConfigSchema,
} from "@/app/types/schemas";
import { Stack, Switch, Text } from "@mantine/core";
import React, { useState, type ReactElement } from "react";

/**
 * Properties of BooleanComponent. Given config
 * needs to be of type BooleanConfigSchema
 */
export interface BooleanComponentProps {
    config: BooleanConfigSchema;
    onChange: (patchData: AllConfigSchema[]) => void;
}

/**
 * Boolean config component. Which renders a switch based
 * on given config
 * @param param0 props
 * @returns Component with switch to set config to true or false
 */
export function BooleanComponent({
    config,
    onChange,
}: BooleanComponentProps): ReactElement {
    const [checked, setChecked] = useState<boolean>(config.value);
    const updateConfig = (value: boolean): void => {
        config.value = value;
        onChange([config]);
    };
    return (
        <Stack gap="xs">
            <Text size="sm" fw={500}>
                {config.name}
            </Text>
            <Switch
                checked={checked}
                onChange={(event) => {
                    const value = event.currentTarget.checked;
                    updateConfig(value);
                    setChecked(value);
                }}
            />
        </Stack>
    );
}
