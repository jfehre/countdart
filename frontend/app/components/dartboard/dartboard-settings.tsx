import {
    type DartboardPatchSchema,
    type DartboardSchema,
} from "@/app/types/schemas";
import { SimpleGrid } from "@mantine/core";
import React, { type ReactElement } from "react";
import { SettingCard } from "../settings/setting-card";

/**
 * Properties for dartboard settings view
 */
export interface DartboardSettingsProps {
    dartboard: DartboardSchema | undefined;
    patchFunc: (patchData: DartboardPatchSchema) => void;
}

/**
 * Component to show all settings for a dartboard
 * @param param0 dartboard schema
 * @returns React component
 */
export function DartboardSettings({
    dartboard,
    patchFunc,
}: DartboardSettingsProps): ReactElement {
    // retrieve all cams

    // keys
    let operators: string[] = [];
    if (dartboard !== undefined) {
        operators = Object.keys(dartboard.op_configs);
    }

    return (
        <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} m="lg">
            {operators.map((name) => {
                return (
                    <SettingCard
                        key={name}
                        title={name}
                        configs={dartboard?.op_configs[name]}
                        patchFunc={patchFunc}
                    />
                );
            })}
        </SimpleGrid>
    );
}
