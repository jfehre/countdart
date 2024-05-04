import { Center, Group } from "@mantine/core";
import React, { type ReactElement } from "react";
import { Connectivity } from "./connectivity";

/**
 * Footer component for the app shell.
 * Contains connectivity check
 */
export function Footer(): ReactElement {
    return (
        <Center h={20}>
            <Group w={"100%"} justify="right" mr="md">
                <Connectivity />
            </Group>
        </Center>
    );
}
