"use client";

import { getDartboard } from "../../services/api";
import { type DartboardProps } from "../../components/Dartboard/dartboard";
import React, { type ReactElement, useEffect, useState } from "react";
import { notifications } from "@mantine/notifications";
import { Stack, Tabs } from "@mantine/core";

export default function Page({
    params,
}: {
    params: { board: string };
}): ReactElement {
    // retrieve dartboard
    const [dartboard, setDartboard] = useState<DartboardProps>();
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
            <h1>Board {dartboard?.name}</h1>
            <Tabs defaultValue="overview">
                <Tabs.List>
                    <Tabs.Tab value="overview">Overview</Tabs.Tab>
                    <Tabs.Tab value="live">Live</Tabs.Tab>
                    <Tabs.Tab value="settings">Settings</Tabs.Tab>
                    <Tabs.Tab value="calibration">Calibration</Tabs.Tab>
                </Tabs.List>

                <Tabs.Panel value="overview">No overview content</Tabs.Panel>
                <Tabs.Panel value="live">No live content</Tabs.Panel>
                <Tabs.Panel value="settings">No settings content</Tabs.Panel>
                <Tabs.Panel value="calibration">
                    No calibration content
                </Tabs.Panel>
            </Tabs>
        </Stack>
    );
}
