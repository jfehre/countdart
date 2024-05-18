import {
    type SelectConfigSchema,
    type AllConfigSchema,
} from "@/app/types/schemas";
import { type ComboboxItem, Select, Stack, Text } from "@mantine/core";
import React, { useState, type ReactElement } from "react";

/**
 * Properties of SelectComponent. Given config
 * needs to be of type SelectConfigSchema
 */
export interface SelectComponentProps {
    config: SelectConfigSchema;
    onChange: (patchData: AllConfigSchema[]) => void;
}

/**
 * Select config component. Which renders a selection based
 * on given config
 * @param param0 props
 * @returns Component to select one option of given config
 */
export function SelectComponent({
    config,
    onChange,
}: SelectComponentProps): ReactElement {
    const [value, setValue] = useState<string | null>(config.value);
    const updateConfig = (value: string | null, option: ComboboxItem): void => {
        if (value === null) {
            return;
        }
        setValue(value);
        config.value = value;
        onChange([config]);
    };
    return (
        <Stack gap="xs">
            <Text size="sm" fw={500}>
                {config.name}
            </Text>
            <Select data={config.data} value={value} onChange={updateConfig} />
        </Stack>
    );
}
