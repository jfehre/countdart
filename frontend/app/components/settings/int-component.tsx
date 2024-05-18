import {
    type AllConfigSchema,
    type IntConfigSchema,
} from "@/app/types/schemas";
import { NumberInput, Stack, Text } from "@mantine/core";
import React, { type ReactElement } from "react";

/**
 * Properties of IntComponent. Given config
 * needs to be of type IntConfigSchema
 */
export interface IntComponentProps {
    config: IntConfigSchema;
    onChange: (patchData: AllConfigSchema[]) => void;
}

/**
 * Int config component. Which renders a number input based
 * on given config
 * @param param0 props
 * @returns Component with number input and label
 */
export function IntComponent({
    config,
    onChange,
}: IntComponentProps): ReactElement {
    const updateConfig = (value: string | number): void => {
        config.value = Number(value);
        onChange([config]);
    };

    return (
        <Stack gap="xs">
            <Text size="sm" fw={500}>
                {config.name}
            </Text>
            <NumberInput
                min={config.min_value}
                max={config.max_value}
                value={config.value}
                onChange={updateConfig}
            />
        </Stack>
    );
}
