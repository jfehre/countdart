import React, { useState, type ReactElement } from "react";

import { Group, Stack } from "@mantine/core";
import { type DartboardSchema } from "@/app/types/schemas";
import { StartStopButton } from "./start-stop-button";
import { GameContextProvider } from "@/app/services/game-context-provider";
import { DartboardGameStatus } from "./dartboard-game-status";

/**
 * Properties for DartboardOverview
 */
export interface DartboardOverviewProps {
    dartboard: DartboardSchema | undefined;
    setDartboard: (dartboard: DartboardSchema) => void;
}

/**
 * Component to show an overview of the dartboard.
 * @param param0 dartboard schema
 * @returns React component
 */
export function DartboardOverview({
    dartboard,
    setDartboard,
}: DartboardOverviewProps): ReactElement {
    const [isActive, setIsActive] = useState(dartboard?.active ?? false);
    console.log(isActive);

    return (
        <Stack p="lg" gap="md">
            <Group>
                <StartStopButton
                    dartboard={dartboard}
                    isActive={isActive}
                    setIsActive={setIsActive}
                ></StartStopButton>
            </Group>
            <GameContextProvider>
                <DartboardGameStatus></DartboardGameStatus>
            </GameContextProvider>
        </Stack>
    );
}
