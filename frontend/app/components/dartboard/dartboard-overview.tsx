import React, { type ReactElement } from "react";

import { Group, Stack, Badge } from "@mantine/core";
import { type DartboardSchema } from "@/app/types/schemas";
import { StartStopButton } from "./start-stop-button";
import { GameContextProvider } from "@/app/services/game-context-provider";
import { DartboardGameStatus } from "./dartboard-game-status";

/**
 * Properties for DartboardOverview
 */
export interface DartboardOverviewProps {
    dartboard: DartboardSchema;
    isActive: boolean;
    setIsActive: (isActive: boolean) => void;
}

/**
 * Component to show an overview of the dartboard.
 * @param param0 dartboard schema
 * @returns React component
 */
export function DartboardOverview({
    dartboard,
    isActive,
    setIsActive,
}: DartboardOverviewProps): ReactElement {
    return (
        <GameContextProvider>
            <Stack p="lg" gap="md">
                <Group justify="space-between">
                    <StartStopButton
                        dartboard={dartboard}
                        isActive={isActive}
                        setIsActive={setIsActive}
                    ></StartStopButton>
                    <Group>
                        <Badge color={isActive ? "green" : "red"}>
                            {isActive ? "active" : "inactive"}
                        </Badge>
                        <Badge>{dartboard.cams.length} Cams</Badge>
                    </Group>
                </Group>
                <DartboardGameStatus></DartboardGameStatus>
            </Stack>
        </GameContextProvider>
    );
}
