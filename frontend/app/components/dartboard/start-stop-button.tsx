import { type DartboardSchema } from "@/app/types/schemas";
import { ActionIcon, Button, Group } from "@mantine/core";
import React, { type ReactElement } from "react";
import { startDartboard, stopDartboard } from "@/app/services/api";
import { notifications } from "@mantine/notifications";
import { IconPlayerPlay, IconPlayerStop } from "@tabler/icons-react";

/**
 * Properties for Dartboard component
 */
export interface StartStopButtonProps {
    dartboard: DartboardSchema | undefined;
    isActive: boolean;
    setIsActive: (isActive: boolean) => void;
    asIcon?: boolean;
}

export function StartStopButton({
    dartboard,
    isActive,
    setIsActive,
    asIcon = false,
}: StartStopButtonProps): ReactElement {
    // Function to start dartboard via api. On error notification is shown
    const startDartboardFunc = (): void => {
        if (dartboard === undefined) {
            notifications.show({
                title: "Error",
                message: "Could not start dartboard: dartboard is undefined",
                color: "red",
            });
        } else {
            startDartboard(dartboard.id)
                .then((response) => {
                    dartboard = response.data;
                    setIsActive(true);
                })
                .catch((error) => {
                    notifications.show({
                        title: "Error",
                        message: "Could not start dartboard: " + error,
                        color: "red",
                    });
                });
        }
    };

    // Function to stop dartboard via api. On error notification is shown
    const stopDartboardFunc = (): void => {
        if (dartboard === undefined) {
            notifications.show({
                title: "Error",
                message: "Could not stop dartboard: dartboard is undefined",
                color: "red",
            });
        } else {
            stopDartboard(dartboard.id)
                .then((response) => {
                    dartboard = response.data;
                    setIsActive(false);
                })
                .catch((error) => {
                    notifications.show({
                        title: "Error",
                        message: "Could not stop dartboard: " + error,
                        color: "red",
                    });
                });
        }
    };

    // Function to start stop camera with icon. Will call api
    const toggleStartStop = (): void => {
        if (isActive) {
            stopDartboardFunc();
        } else {
            startDartboardFunc();
        }
    };

    const icons = (
        <Group>
            <IconPlayerPlay
                visibility={isActive ? "hidden" : "visible"}
                display={isActive ? "None" : "block"}
            />
            <IconPlayerStop
                visibility={isActive ? "visible" : "hidden"}
                display={isActive ? "block" : "None"}
            />
        </Group>
    );

    return asIcon ? (
        <ActionIcon
            onClick={(e: React.MouseEvent) => {
                toggleStartStop();
                e.preventDefault();
            }}
            variant="subtle"
        >
            {icons}
        </ActionIcon>
    ) : (
        <Button
            leftSection={icons}
            onClick={(e: React.MouseEvent) => {
                toggleStartStop();
                e.preventDefault();
            }}
        >
            {isActive ? "Stop" : "Start"}
        </Button>
    );
}
