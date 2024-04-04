import React, { type ReactElement } from "react";
import { useForm } from "@mantine/form";
import { Stack, TextInput, Button, Group } from "@mantine/core";

// CreateProps. For each prop an form element should exist
export interface DartboardCreateSchema {
    name: string;
}

// Create function props which is called on submit
export type DartboardCreateFunction = (values: DartboardCreateSchema) => void;

// Interface for ReactComponent CreateDartboardForm
interface CreateDartboardFormProps {
    submit: DartboardCreateFunction;
}

export function CreateDartboardForm({
    submit,
}: CreateDartboardFormProps): ReactElement {
    // create mantine form
    const form = useForm({
        initialValues: {
            name: "",
        },
    });

    return (
        <Stack>
            <form onSubmit={form.onSubmit(submit)}>
                <TextInput label="Name" {...form.getInputProps("name")} />
                <Group justify="flex-end" mt="md">
                    <Button type="submit">Create</Button>
                </Group>
            </form>
        </Stack>
    );
}
