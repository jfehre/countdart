import React, { type ReactElement } from "react";
import { useForm } from "@mantine/form";
import { Stack, Button, Group, TextInput } from "@mantine/core";
import { type CamCreateSchema } from "@/app/types/schemas";

/**
 * Create function props which is called on submit
 */
export type SimulationCreateFunction = (values: CamCreateSchema) => void;

/**
 * Properties for CreateSimForm
 */
interface CreateSimFormProps {
    submit: SimulationCreateFunction;
}

/**
 * Form to create a new simulation
 * @param param0 submit function
 * @returns React form
 */
export function CreateSimForm({ submit }: CreateSimFormProps): ReactElement {
    // create mantine form
    const form = useForm({
        initialValues: {
            name: "",
            source: "",
            type: "VideoReader",
        },
    });

    return (
        <Stack>
            <form onSubmit={form.onSubmit(submit)}>
                <TextInput label="Name" {...form.getInputProps("name")} />
                <TextInput label="Source" {...form.getInputProps("source")} />

                <Group justify="flex-end" mt="md">
                    <Button type="submit">Create</Button>
                </Group>
            </form>
        </Stack>
    );
}
