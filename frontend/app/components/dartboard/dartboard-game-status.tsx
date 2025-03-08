import { useGameContext } from "@/app/services/game-context-provider";
import { Card } from "@mantine/core";
import React, { type ReactElement } from "react";

export function DartboardGameStatus(): ReactElement {
    const { currentCls, currentResult } = useGameContext();

    return (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
            Current class is {currentCls}
            <br />
            Result is {currentResult}
        </Card>
    );
}
