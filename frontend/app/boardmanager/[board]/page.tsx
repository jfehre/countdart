"use client";

import { getDartboard } from "../../services/api";
import { type DartboardSchema } from "../../components/Dartboard/dartboard";
import React, { type ReactElement, useEffect, useState } from "react";
import { notifications } from "@mantine/notifications";
import { Stack, Tabs } from "@mantine/core";
import { CameraOverview } from "@/app/components/Camera/camera-overview";

export default function Page({
    params,
}: {
    params: { board: string };
}): ReactElement {
    // retrieve dartboard
    const [dartboard, setDartboard] = useState<DartboardSchema>();
    useEffect(() => {
        getDartboard(params.board)
            .then((response) => {
                setDartboard(response.data);
            })
            .catch((error) => {
                notifications.show({
                    title: "Connection error",
                    message: "Could not retrieve Boards " + error,
                    color: "red",
                });
            });
    }, []);

    return (
        <Stack>
            <h1>{dartboard?.name}</h1>
            <Tabs keepMounted={false} defaultValue="overview">
                <Tabs.List>
                    <Tabs.Tab value="overview">Overview</Tabs.Tab>
                    <Tabs.Tab value="cameras">Cameras</Tabs.Tab>
                    <Tabs.Tab value="settings">Settings</Tabs.Tab>
                    <Tabs.Tab value="calibration">Calibration</Tabs.Tab>
                </Tabs.List>

                <Tabs.Panel value="overview">No overview content</Tabs.Panel>
                <Tabs.Panel value="cameras">
                    <CameraOverview dartboard={dartboard}></CameraOverview>
                </Tabs.Panel>
                <Tabs.Panel value="settings">No settings content</Tabs.Panel>
                <Tabs.Panel value="calibration">
                    No calibration content
                </Tabs.Panel>
            </Tabs>
        </Stack>
    );
}
