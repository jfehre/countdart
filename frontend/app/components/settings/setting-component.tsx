import {
    type AllConfigSchema,
    type IntConfigSchema,
    type SelectConfigSchema,
    type BooleanConfigSchema,
} from "@/app/types/schemas";
import React, { type ReactElement } from "react";
import { IntComponent } from "./int-component";
import { SelectComponent } from "./select-component";
import { BooleanComponent } from "./boolean-component";

/**
 * Properties for a settings component
 * Contains key, the config schema and a on change function
 * to update changes in db
 */
export interface SettingComponentProps {
    config: AllConfigSchema;
    key: string | number;
    onChange: (patchData: AllConfigSchema[]) => void;
}

/**
 * Settings Component
 * @param param0 properties
 * @returns React component for one setting
 */
export function SettingComponent({
    config,
    key,
    onChange,
}: SettingComponentProps): ReactElement {
    // Choose which type of component was received
    let component;
    switch (config.type) {
        case "int":
            component = (
                <IntComponent
                    config={config as IntConfigSchema}
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
            component = "dont know";
    }

    // return specific settings type component
    return <div key={key}>{component}</div>;
}
