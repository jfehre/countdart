import { ActionIcon, ActionIconGroup, Stack, Tooltip } from "@mantine/core";
import {
    IconActivity,
    IconLivePhoto,
    IconPerspective,
} from "@tabler/icons-react";
import Image from "next/image";
import React, { useEffect, type ReactElement, useState, useRef } from "react";

export interface WebSocketStreamProps {
    camId: string;
    height: number;
}

export function WebSocketStream({
    camId,
    height,
}: WebSocketStreamProps): ReactElement {
    // base64 image
    const [image, setImage] = useState("/images/no_image.webp");
    const url: string = `ws://localhost:7878/api/v1/cams/ws/${camId}/live`;
    const [activeView, setActiveView] = useState("raw");
    const ws = useRef<WebSocket>();

    // change image view between raw, warped and motion
    const changeImageView = (view: string): void => {
        ws.current?.send(view);
        setActiveView(view);
    };

    useEffect(() => {
        ws.current = new WebSocket(url);

        ws.current.onmessage = (e) => {
            const b64String: string = e.data;
            // check if undefinded
            if (b64String === "undefined") {
                setImage("/images/no_image.webp");
                console.log("undef");
            } else {
                setImage("data: image:jpeg;base64, " + b64String);
            }
        };

        return () => {
            ws.current?.close();
        };
    }, []);

    return (
        <Stack gap="0">
            <div
                style={{
                    height,
                    position: "relative",
                    backgroundColor: "black",
                }}
            >
                <Image
                    src={image}
                    alt={"Live feed"}
                    fill
                    style={{ objectFit: "contain" }}
                ></Image>
            </div>
            <ActionIconGroup pos={"absolute"} orientation="vertical">
                <ActionIcon
                    variant={activeView === "raw" ? "filled" : "outline"}
                    size="md"
                    aria-label="Live"
                    onClick={() => {
                        changeImageView("raw");
                        setActiveView("raw");
                    }}
                >
                    <Tooltip label="Live View" position="bottom">
                        <IconLivePhoto />
                    </Tooltip>
                </ActionIcon>
                <ActionIcon
                    variant={activeView === "warped" ? "filled" : "outline"}
                    size="md"
                    aria-label="Warped"
                    onClick={() => {
                        changeImageView("warped");
                        setActiveView("warped");
                    }}
                >
                    <Tooltip label="Warped View" position="bottom">
                        <IconPerspective />
                    </Tooltip>
                </ActionIcon>
                <ActionIcon
                    variant={activeView === "motion" ? "filled" : "outline"}
                    size="md"
                    aria-label="Motion"
                >
                    <Tooltip label="Activity View" position="bottom">
                        <IconActivity />
                    </Tooltip>
                </ActionIcon>
            </ActionIconGroup>
        </Stack>
    );
}
