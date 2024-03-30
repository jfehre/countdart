"use client";

import React, { useState, type ReactElement, useEffect } from "react";
import { getDartboards } from "../services/api";
import { notifications } from "@mantine/notifications";
import { Stack } from "@mantine/core";
import {
    type DartboardProps,
    Dartboard,
} from "../components/Dartboard/dartboard";

export default function Page(): ReactElement {
    // retrieve all dartboards
    const [dartboards, setDartboards] = useState<DartboardProps[]>([]);
    useEffect(() => {
        getDartboards()
            .then((response) => {
                setDartboards(response.data);
            })
            .catch((error) => {
                notifications.show({
                    title: "Connection error",
                    message: "Could not retrieve Boards: " + error,
                    color: "red",
                });
            });
    }, []);

    console.log(dartboards);

    return (
        <Stack>
            <h1>Boardmanager</h1>
            {dartboards.map((dartboard) => (
                <Dartboard key={dartboard.id} {...dartboard} />
            ))}
        </Stack>
    );
}
