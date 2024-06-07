"use client";

import React, { useState, type ReactElement, useEffect } from "react";
import {
    getDartboards,
    createDartboard,
    deleteDartboard,
    getDartboardProcedures,
} from "../services/api";
import { notifications } from "@mantine/notifications";
import { Button, Group, Modal, Stack } from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";

import { Dartboard } from "../components/dartboard/dartboard";
import { useDisclosure } from "@mantine/hooks";
import {
    CreateDartboardForm,
    type DartboardCreateFunction,
} from "../components/dartboard/create-form";
import {
    type DartboardCreateSchema,
    type DartboardSchema,
} from "../types/schemas";

export default function Page(): ReactElement {
    // Create modal state
    const [createModalState, createModalHandler] = useDisclosure(false);

    // retrieve all dartboards and types
    const [dartboards, setDartboards] = useState<DartboardSchema[]>([]);
    const [dartboardProcedures, setDartboardProcedures] = useState<string[]>(
        [],
    );
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
        // get dartboard procedure types
        getDartboardProcedures()
            .then((response) => {
                setDartboardProcedures(response.data);
            })
            .catch((error) => {
                notifications.show({
                    title: "Connection error",
                    message:
                        "Could not retrieve available procedures: " + error,
                    color: "red",
                });
            });
    }, []);

    // Create dartboard and close modal
    const createBoard: DartboardCreateFunction = (
        values: DartboardCreateSchema,
    ): void => {
        createDartboard(values)
            .then((response) => {
                const newDartboards: DartboardSchema[] = dartboards.concat(
                    response.data,
                );
                setDartboards(newDartboards);
            })
            .catch((error) => {
                notifications.show({
                    title: "Post error",
                    message: "Could not create board: " + error,
                    color: "red",
                });
            });
        createModalHandler.close();
    };

    // Delete dartboard
    const deleteBoard = (key: string): void => {
        deleteDartboard(key)
            .then((response) => {
                const newDartboards: DartboardSchema[] = dartboards.filter(
                    (dartboard) => {
                        return dartboard.id !== key;
                    },
                );
                setDartboards(newDartboards);
            })
            .catch((error) => {
                notifications.show({
                    title: "Delete error",
                    message: "Could not delete board: " + error,
                    color: "red",
                });
            });
    };

    return (
        <Stack>
            <Group justify="space-between">
                <h1>Boardmanager</h1>
                <Button
                    leftSection={<IconPlus />}
                    onClick={createModalHandler.open}
                >
                    Create Board
                </Button>
            </Group>
            {dartboards.map((dartboard) => (
                <Dartboard
                    key={dartboard.id}
                    dartboard={dartboard}
                    deleteFunc={deleteBoard}
                />
            ))}

            <Modal
                opened={createModalState}
                onClose={createModalHandler.close}
                title="Create Board"
                centered
            >
                <CreateDartboardForm
                    submit={createBoard}
                    procedures={dartboardProcedures}
                />
            </Modal>
        </Stack>
    );
}
