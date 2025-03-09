import { useGameContext } from "@/app/services/game-context-provider";
import { type ResultMessage } from "@/app/types/schemas";
import {
    Card,
    CardSection,
    Group,
    Text,
    Table,
    Stack,
    Button,
} from "@mantine/core";
import React, { useEffect, useRef, useState, type ReactElement } from "react";
import { DartboardSketch } from "./dartboard-sketch";

/**
 * Component to show the status of the dartboard game.
 * @returns React component
 */
export function DartboardGameStatus(): ReactElement {
    const [currentCls, setCurrentCls] = useState<string>("Off");
    const [lastThreeResults, setLastThreeResults] = useState<ResultMessage[]>(
        [],
    );
    const { onNewResult } = useGameContext();
    const dartboardRef = useRef<{
        drawPoint: (x: number, y: number) => void;
        clearPoints: () => void;
    } | null>(null);

    /**
     * Clear points on dartboard
     */
    const handleClearPoints = (): void => {
        if (dartboardRef.current !== null) {
            dartboardRef.current.clearPoints();
        }
    };

    useEffect(() => {
        // register callback when new result is received
        const handleNewResult = (result: ResultMessage): void => {
            // Set class to new result
            setCurrentCls(result.cls);
            if (result.cls === "dart") {
                // add new result to last three results
                setLastThreeResults((prevResults) => {
                    const newResults = [...prevResults, result];
                    return newResults.slice(-3);
                });
                // draw point on dartboard
                if (
                    dartboardRef.current !== null &&
                    result.content?.point !== undefined
                ) {
                    const [x, y] = result.content.point;
                    dartboardRef.current.drawPoint(
                        Math.round(x * 100) / 100,
                        Math.round(y * 100) / 100,
                    );
                }
            } else if (result.cls === "hand") {
                // clear last three results and points on dartboard
                setLastThreeResults([]);
                if (dartboardRef.current !== null) {
                    dartboardRef.current.clearPoints();
                }
            }
        };

        onNewResult(handleNewResult);
    }, [onNewResult]);

    const lastResult = lastThreeResults[lastThreeResults.length - 1];

    return (
        <Group align="stretch">
            <Card shadow="sm" padding="lg" radius="md" withBorder>
                <CardSection p="lg">
                    <Text fw={700}>Last Result</Text>
                </CardSection>
                <CardSection>
                    <Table miw={300}>
                        <Table.Tbody>
                            <Table.Tr>
                                <Table.Td>
                                    <Text c="dimmed">Class</Text>
                                </Table.Td>
                                <Table.Td>{currentCls}</Table.Td>
                            </Table.Tr>
                            <Table.Tr>
                                <Table.Td>
                                    <Text c="dimmed">Score</Text>
                                </Table.Td>
                                <Table.Td>
                                    {lastResult?.content?.score}
                                </Table.Td>
                            </Table.Tr>
                            <Table.Tr>
                                <Table.Td>
                                    <Text c="dimmed">Confidence</Text>
                                </Table.Td>
                                <Table.Td>
                                    {lastResult?.content?.confidence.toFixed(2)}
                                </Table.Td>
                            </Table.Tr>
                            <Table.Tr>
                                <Table.Td>
                                    <Text c="dimmed">Point</Text>
                                </Table.Td>
                                <Table.Td>
                                    [{lastResult?.content?.point[0].toFixed(2)},{" "}
                                    {lastResult?.content?.point[1].toFixed(2)}]
                                </Table.Td>
                            </Table.Tr>
                        </Table.Tbody>
                    </Table>
                </CardSection>
            </Card>
            <Card miw={300} shadow="sm" padding="lg" radius="md" withBorder>
                <Stack justify="center" h={"100%"}>
                    <Group>
                        <Card shadow="sm" padding="lg" radius="md" withBorder>
                            {lastThreeResults[0]?.content?.score ?? "None"}
                        </Card>
                        <Card shadow="sm" padding="lg" radius="md" withBorder>
                            {lastThreeResults[1]?.content?.score ?? "None"}
                        </Card>
                        <Card shadow="sm" padding="lg" radius="md" withBorder>
                            {lastThreeResults[2]?.content?.score ?? "None"}
                        </Card>
                    </Group>
                </Stack>
            </Card>
            <Card shadow="sm" padding="lg" radius="md" withBorder>
                <DartboardSketch ref={dartboardRef} />
                <Button onClick={handleClearPoints}>Clear Points</Button>
            </Card>
        </Group>
    );
}
