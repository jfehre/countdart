import {
    type AllConfigSchema,
    type NumberConfigSchema,
} from "@/app/types/schemas";
import { NumberInput, Stack, Text } from "@mantine/core";
import React, { useState, type ReactElement } from "react";

/**
 * Properties of IntComponent. Given config
 * needs to be of type NumberConfigSchema
 */
export interface IntComponentProps {
    config: NumberConfigSchema;
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
    const [value, setValue] = useState<string | number>(config.value);
    const updateConfig = (value: string | number): void => {
        config.value = Number(value);
        setValue(value);
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
                value={value}
                fixedDecimalScale
                decimalScale={0}
                step={1}
                stepHoldDelay={500}
                stepHoldInterval={(t) => Math.max(1000 / t ** 2, 25)}
                onChange={updateConfig}
            />
        </Stack>
    );
}
