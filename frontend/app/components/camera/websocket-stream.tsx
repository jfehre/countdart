import { getCamFps } from "@/app/services/api";
import { type CamSchema } from "@/app/types/schemas";
import {
    ActionIcon,
    ActionIconGroup,
    Stack,
    Text,
    Tooltip,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import {
    IconActivity,
    IconLivePhoto,
    IconPerspective,
} from "@tabler/icons-react";
import Image from "next/image";
import React, { useEffect, type ReactElement, useState, useRef } from "react";

export interface WebSocketStreamProps {
    cam: CamSchema;
    height: number;
}

export function WebSocketStream({
    cam,
    height,
}: WebSocketStreamProps): ReactElement {
    // base64 image
    const [image, setImage] = useState("/images/no_image.webp");
    const [fps, setFps] = useState<number>();
    const url: string = `ws://localhost:7878/api/v1/cams/ws/${cam.id}/live`;
    const [activeView, setActiveView] = useState(cam.type);
    const ws = useRef<WebSocket>();

    // get cam fps
    const getCamFpsFunc = (): void => {
        getCamFps(cam.id)
            .then((response) => {
                setFps(response.data);
            })
            .catch((error) => {
                notifications.show({
                    title: "Error",
                    message: "Could not get cam fps: " + error,
                    color: "red",
                });
            });
    };

    // change image view between different operators
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
            // update fps
            getCamFpsFunc();
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
            <Text pos={"absolute"} right={0} c="red">
                FPS: {fps}
            </Text>
            <ActionIconGroup pos={"absolute"} orientation="vertical">
                <ActionIcon
                    variant={activeView === cam.type ? "filled" : "outline"}
                    size="md"
                    aria-label="Live"
                    onClick={() => {
                        changeImageView(cam.type);
                        setActiveView(cam.type);
                    }}
                >
                    <Tooltip label="Live View" position="bottom">
                        <IconLivePhoto />
                    </Tooltip>
                </ActionIcon>
                <ActionIcon
                    variant={
                        activeView === "HomographyWarper" ? "filled" : "outline"
                    }
                    size="md"
                    aria-label="Warped"
                    onClick={() => {
                        changeImageView("HomographyWarper");
                        setActiveView("HomographyWarper");
                    }}
                >
                    <Tooltip label="Warped View" position="bottom">
                        <IconPerspective />
                    </Tooltip>
                </ActionIcon>
                <ActionIcon
                    variant={
                        activeView === "ChangeDetector" ? "filled" : "outline"
                    }
                    size="md"
                    aria-label="Motion"
                    onClick={() => {
                        changeImageView("ChangeDetector");
                        setActiveView("ChangeDetector");
                    }}
                >
                    <Tooltip label="Activity View" position="bottom">
                        <IconActivity />
                    </Tooltip>
                </ActionIcon>
            </ActionIconGroup>
        </Stack>
    );
}
