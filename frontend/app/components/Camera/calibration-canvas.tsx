import { type CamSchema } from "@/app/types/schemas";
import { Group } from "@mantine/core";
import React, { useRef, type ReactElement, useEffect } from "react";

export interface CalibrationCanvasProps {
    cam: CamSchema;
}

export function CalibrationCanvas({
    cam,
}: CalibrationCanvasProps): ReactElement {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const zoomRef = useRef<HTMLCanvasElement>(null);
    const wrapperRef = useRef<HTMLDivElement>(null);
    let offset = new DOMRect();

    const img = new Image();
    img.src = "http://astrobioloblog.files.wordpress.com/2011/10/duck-1.jpg";

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvasRef.current?.getContext("2d");
        // get canvas context
        if (ctx !== null && ctx !== undefined && canvas !== null) {
            img.onload = () => {
                ctx.drawImage(img, 0, 0);
            };
            // update canvas offset on resize
            offset = canvas.getBoundingClientRect();
            const handleResize = (): void => {
                offset = canvas.getBoundingClientRect();
                console.log("hi");
            };
            window.addEventListener("resize", handleResize);
            // Zoom ctx
            const zoom = zoomRef.current;
            const zoomCtx = zoomRef.current?.getContext("2d");
            if (zoomCtx !== null && zoomCtx !== undefined && zoom !== null) {
                const zoomFunction = (e: MouseEvent): void => {
                    zoomCtx.fillRect(0, 0, 200, 200);
                    zoomCtx.drawImage(
                        canvas,
                        e.x - offset.left - 25,
                        e.y - offset.top - 25,
                        50,
                        50,
                        0,
                        0,
                        200,
                        200,
                    );
                    // canvas.style.top = offset.top + "px";
                    zoom.style.left = e.x - offset.left - 75 + "px";
                    zoom.style.top = e.y - offset.top - 25 + "px";
                    if (
                        e.x > offset.left + canvas.width ||
                        e.x < offset.left ||
                        e.y > offset.top + canvas.height ||
                        e.y < offset.top
                    ) {
                        zoom.style.display = "none";
                    } else {
                        zoom.style.display = "block";
                    }

                    console.log(e.y + " " + offset.top);
                };

                wrapperRef.current?.addEventListener("mousemove", zoomFunction);
            }
        }
    }, []);
    return (
        <Group ref={wrapperRef} p="md">
            <canvas
                style={{
                    position: "absolute",
                    display: "none",
                    zIndex: "100",
                }}
                width={200}
                height={200}
                ref={zoomRef}
            />
            <canvas width={500} height={500} ref={canvasRef} />
        </Group>
    );
}
