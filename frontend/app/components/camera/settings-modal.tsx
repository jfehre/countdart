import { type AllConfigSchema, type CamSchema } from "@/app/types/schemas";
import { Modal, SimpleGrid } from "@mantine/core";
import React, { useState, type ReactElement, useEffect } from "react";
import { WebSocketStream } from "./websocket-stream";
import { getCamConfig } from "@/app/services/api";
import { notifications } from "@mantine/notifications";
import { SettingComponent } from "../settings/setting-component";

/**
 * Properties for settings modal
 */
export interface SettingsModalProps {
    opened: boolean;
    onClose: () => void;
    cam: CamSchema;
    patchFunc: (patchData: AllConfigSchema[]) => void;
}

/**
 * Component which shows livestream and all settings available for this camera
 * @param param0 cam schema and patch function if one setting was changed
 * @returns Reac Modal
 */
export function SettingsModal({
    opened,
    onClose,
    cam,
    patchFunc,
}: SettingsModalProps): ReactElement {
    const [camInfo, setCamInfo] = useState<AllConfigSchema[]>([]);

    // get Camera settings
    const getCamInfoFunc = (id: string): void => {
        getCamConfig(id)
            .then((response) => {
                setCamInfo(response.data);
            })
            .catch((error) => {
                notifications.show({
                    title: "Get error",
                    message: "Could not get Cam Config: " + error,
                    color: "red",
                });
            });
    };

    // load cam info
    useEffect(() => {
        getCamInfoFunc(cam.id);
    }, []);

    // add settings component for each available setting
    return (
        <Modal
            opened={opened}
            onClose={onClose}
            keepMounted={false}
            title="Settings"
            size={"80%"}
            lockScroll={false}
        >
            <WebSocketStream height={300} cam={cam} />
            <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} m="lg">
                {camInfo.map((config, index) => {
                    return (
                        <SettingComponent
                            config={config}
                            key={index}
                            onChange={patchFunc}
                        />
                    );
                })}
            </SimpleGrid>
        </Modal>
    );
}
