"use client";

import { getDartboard, patchDartboard } from "../../services/api";
import React, { type ReactElement, useEffect, useState } from "react";
import { notifications } from "@mantine/notifications";
import { Stack, Tabs } from "@mantine/core";
import { CameraOverview } from "@/app/components/camera/camera-overview";
import {
    type DartboardPatchSchema,
    type DartboardSchema,
} from "@/app/types/schemas";
import { DartboardSettings } from "@/app/components/dartboard/dartboard-settings";
import { DartboardOverview } from "@/app/components/dartboard/dartboard-overview";

export default function Page({
    params,
}: {
    params: { board: string };
}): ReactElement {
    // retrieve dartboard
    const [dartboard, setDartboard] = useState<DartboardSchema>();
    const [isActive, setIsActive] = useState<boolean>(false);
    useEffect(() => {
        getDartboard(params.board)
            .then((response) => {
                setDartboard(response.data);
                setIsActive(response.data.active);
            })
            .catch((error) => {
                notifications.show({
                    title: "Connection error",
                    message: "Could not retrieve Board " + error,
                    color: "red",
                });
            });
    }, []);

    // function to patch dartboard
    const patchFunc = (patchData: DartboardPatchSchema): void => {
        patchDartboard(dartboard?.id, patchData)
            .then((response) => {})
            .catch((error) => {
                notifications.show({
                    title: "Patch error",
                    message: "Could not update Dartboard" + error,
                    color: "red",
                });
            });
    };

    return (
        <Stack>
            <h1>{dartboard?.name}</h1>
            <Tabs keepMounted={false} defaultValue="overview">
                <Tabs.List>
                    <Tabs.Tab value="overview">Overview</Tabs.Tab>
                    <Tabs.Tab value="cameras">Cameras</Tabs.Tab>
                    <Tabs.Tab value="settings">Settings</Tabs.Tab>
                </Tabs.List>

                <Tabs.Panel value="overview">
                    {dartboard !== undefined && (
                        <DartboardOverview
                            dartboard={dartboard}
                            isActive={isActive}
                            setIsActive={setIsActive}
                        ></DartboardOverview>
                    )}
                </Tabs.Panel>
                <Tabs.Panel value="cameras">
                    <CameraOverview
                        dartboard={dartboard}
                        setDartboard={setDartboard}
                    ></CameraOverview>
                </Tabs.Panel>
                <Tabs.Panel value="settings">
                    <DartboardSettings
                        dartboard={dartboard}
                        patchFunc={patchFunc}
                    />
                </Tabs.Panel>
            </Tabs>
        </Stack>
    );
}
