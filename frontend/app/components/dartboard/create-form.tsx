import React, { type ReactElement } from "react";
import { useForm } from "@mantine/form";
import { Stack, TextInput, Button, Group, Select } from "@mantine/core";
import { type DartboardCreateSchema } from "@/app/types/schemas";

/**
 * Create function props which is called on submit
 */
export type DartboardCreateFunction = (values: DartboardCreateSchema) => void;

/**
 * Properties for CreateDartboardForm
 */
interface CreateDartboardFormProps {
    submit: DartboardCreateFunction;
    procedures: string[];
}

/**
 * Component which shows a new form to create a Dartboard in the api
 * with the given submit function
 * @param param0 submit function
 * @returns component with the create form
 */
export function CreateDartboardForm({
    submit,
    procedures,
}: CreateDartboardFormProps): ReactElement {
    // create mantine form
    const form = useForm({
        initialValues: {
            name: "",
            type: "",
        },
    });

    return (
        <Stack>
            <form onSubmit={form.onSubmit(submit)}>
                <TextInput label="Name" {...form.getInputProps("name")} />
                <Select
                    label="Procedure"
                    data={procedures}
                    {...form.getInputProps("type")}
                ></Select>
                <Group justify="flex-end" mt="md">
                    <Button type="submit">Create</Button>
                </Group>
            </form>
        </Stack>
    );
}
