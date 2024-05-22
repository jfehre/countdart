import { getCamFps } from "@/app/services/api";
import { type CamSchema } from "@/app/types/schemas";
import {
    ActionIcon,
    ActionIconGroup,
    Group,
    Stack,
    Text,
    Tooltip,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import {
    IconActivity,
    IconBug,
    IconLivePhoto,
    IconMaximize,
    IconMinimize,
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
    // reference of this component
    const componentRef = useRef<any>(null);
    // base64 image
    const [image, setImage] = useState("/images/no_image.webp");
    // height of image, will be changed on toggle fullscreen
    const [heightState, setHeightState] = useState<number | string>(height);
    // current fps
    const [fps, setFps] = useState<number>();
    // state if fullscreen or not
    const [isFullscreen, setIsFullscreen] = useState(false);
    // state of view
    const [activeView, setActiveView] = useState(cam.type);

    // websocket source and ref
    const url: string = `ws://localhost:7878/api/v1/cams/ws/${cam.id}/live`;
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
    // will send message to websocket
    const changeImageView = (view: string): void => {
        ws.current?.send(view);
        setActiveView(view);
    };

    // function to toggle fullscreen
    const toggleFullScreen = (): void => {
        const element = componentRef.current;
        if (!isFullscreen) {
            if (element?.requestFullscreen !== undefined) {
                void element.requestFullscreen();
            }
            setIsFullscreen(true);
            setHeightState("100vh");
        } else {
            if (document.exitFullscreen !== undefined) {
                void document.exitFullscreen();
            }
            setIsFullscreen(false);
            setHeightState(height);
        }
    };
    // function to capture exit fullscreen with ESC key
    const exitFullScreenWithEsc = (): void => {
        if (document.fullscreenElement === null) {
            setIsFullscreen(false);
            setHeightState(height);
        }
    };

    // Effect on first load (will open websocket)
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

        // add event listener for fullscreenchange
        document.addEventListener("fullscreenchange", exitFullScreenWithEsc);

        return () => {
            ws.current?.close();
            document.removeEventListener(
                "fullscreenchange",
                exitFullScreenWithEsc,
            );
        };
    }, []);

    // Component to return
    return (
        <Stack gap="0" ref={componentRef}>
            {/* Image */}
            <div
                style={{
                    height: heightState,
                    position: "relative",
                    backgroundColor: "black",
                }}
            >
                <Image
                    src={image}
                    alt={"Live feed"}
                    fill
                    style={{ objectFit: "contain" }}
                />
            </div>
            {/* Icons and text on image */}
            <Text pos={"absolute"} right={0} c="red">
                FPS: {fps?.toFixed(2)}
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
                <ActionIcon
                    variant={
                        activeView === "ResultVisualizer" ? "filled" : "outline"
                    }
                    size="md"
                    aria-label="ResultVisualizer"
                    onClick={() => {
                        changeImageView("ResultVisualizer");
                        setActiveView("ResultVisualizer");
                    }}
                >
                    <Tooltip label="Debug view" position="bottom">
                        <IconBug />
                    </Tooltip>
                </ActionIcon>
            </ActionIconGroup>
            <Group justify="flex-end" pos={"relative"} top={-28}>
                <ActionIcon
                    variant={"subtle"}
                    size="md"
                    aria-label="Fullscreen"
                    onClick={() => {
                        toggleFullScreen();
                    }}
                >
                    <Tooltip label="Debug view" position="bottom">
                        <div>
                            <IconMaximize
                                visibility={isFullscreen ? "hidden" : "visible"}
                                display={isFullscreen ? "None" : "block"}
                            />
                            <IconMinimize
                                visibility={isFullscreen ? "visible" : "hidden"}
                                display={isFullscreen ? "block" : "None"}
                            />
                        </div>
                    </Tooltip>
                </ActionIcon>
            </Group>
        </Stack>
    );
}
