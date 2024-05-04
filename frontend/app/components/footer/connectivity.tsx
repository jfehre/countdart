import { health, host } from "@/app/services/api";
import { Group, Text } from "@mantine/core";
import { IconCircleFilled } from "@tabler/icons-react";
import React, { useState, type ReactElement, useEffect } from "react";

/**
 * React component which returns api host name and
 * connectivity status of api.
 * Checks all 3 seconds the if api is reachable
 */
export function Connectivity(): ReactElement {
    const [isConnected, setIsConnected] = useState(false);

    // Function to check connection. Will set isConnected state
    const checkConnection = (): void => {
        health()
            .then((response) => {
                setIsConnected(true);
            })
            .catch(() => {
                setIsConnected(false);
            });
    };

    // effect hook, which starts js interval
    // to check connection every 3 seconds
    useEffect(() => {
        checkConnection();
        const interval = setInterval(() => {
            checkConnection();
        }, 3000);

        return () => {
            clearInterval(interval);
        };
    });

    return (
        <Group gap={5}>
            <Text size="0.7rem" c={isConnected ? "green" : "red"}>
                {host}
            </Text>
            <IconCircleFilled
                size={"0.7rem"}
                color={isConnected ? "green" : "red"}
            />
        </Group>
    );
}
