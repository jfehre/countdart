import { useGameContext } from "@/app/services/game-context-provider";
import { Card } from "@mantine/core";
import React, { type ReactElement } from "react";

export function DartboardGameStatus(): ReactElement {
    const { isReady } = useGameContext();

    return (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
            Websocket is {isReady ? "ready" : "not ready"}
        </Card>
    );
}
