import {
    type AllConfigSchema,
    type NumberConfigSchema,
    type SelectConfigSchema,
    type BooleanConfigSchema,
} from "@/app/types/schemas";
import React, { type ReactElement } from "react";
import { IntComponent } from "./int-component";
import { SelectComponent } from "./select-component";
import { BooleanComponent } from "./boolean-component";
import { FloatComponent } from "./float-component";

/**
 * Properties for a settings component
 * Contains key, the config schema and a on change function
 * to update changes in db
 */
export interface SettingComponentProps {
    config: AllConfigSchema;
    onChange: (patchData: AllConfigSchema[]) => void;
}

/**
 * Settings Component
 * @param param0 properties
 * @returns React component for one setting
 */
export function SettingComponent({
    config,
    onChange,
}: SettingComponentProps): ReactElement {
    // Choose which type of component was received
    let component;
    switch (config.type) {
        case "float":
            component = (
                <FloatComponent
                    config={config as NumberConfigSchema}
                    onChange={onChange}
                />
            );
            break;

        case "int":
            component = (
                <IntComponent
                    config={config as NumberConfigSchema}
                    onChange={onChange}
                />
            );
            break;
        case "bool":
            component = (
                <BooleanComponent
                    config={config as BooleanConfigSchema}
                    onChange={onChange}
                />
            );
            break;
        case "select":
            component = (
                <SelectComponent
                    config={config as SelectConfigSchema}
                    onChange={onChange}
                />
            );
            break;
        default:
            component = "no component for " + config.type;
    }

    // return specific settings type component
    return <div>{component}</div>;
}
