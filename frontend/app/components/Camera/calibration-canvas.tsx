import { type CalibrationPoint, type CamSchema } from "@/app/types/schemas";
import { Group } from "@mantine/core";
import React, {
    useRef,
    type ReactElement,
    useEffect,
    forwardRef,
    useImperativeHandle,
    useState,
} from "react";

export interface Shape {
    x: number;
    y: number;
    radius: number;
    label: string;
}

/**
 * Interface for event function which is called by parent
 */
export interface CalibrationCanvasHandle {
    handleScroll: () => void;
    getCalibPoints: () => CalibrationPoint[];
    clearCalibPoints: () => void;
}

/**
 * Properties of CalibrationCanvas
 */
export interface CalibrationCanvasProps {
    cam: CamSchema;
}

/**
 * Calibration canvas element
 * This element will be exported below, because it uses a forwardRef function
 * It implements a zoom function on mouseMove and enables the user to drag around
 * 4 canvas shapes defined by the given camera.
 */
const CalibrationCanvas = forwardRef<
    CalibrationCanvasHandle,
    CalibrationCanvasProps
>(function CalibrationCanvas(
    { cam }: CalibrationCanvasProps,
    ref,
): ReactElement {
    // define reference of different html elements
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const zoomRef = useRef<HTMLCanvasElement>(null);
    const wrapperRef = useRef<HTMLDivElement>(null);
    // offset to update position of mouse in canvas
    // will be updated onScroll of parent and on resize of the window
    let offset = new DOMRect();

    // Set image to websocket url
    const url: string = `ws://localhost:7878/api/v1/cams/ws/${cam.id}/live`;
    const img = new Image();
    // default image;
    const [imgSrc, setImgSrc] = useState("/images/no_image.webp");
    img.src = imgSrc;

    // define canvas variables, but do not initialize
    // initialize it in the useEffect hook
    let canvas: HTMLCanvasElement | null;
    let ctx: CanvasRenderingContext2D | null | undefined;
    let zoom: HTMLCanvasElement | null;
    let zoomCtx: CanvasRenderingContext2D | null | undefined;

    // define 4 targets/shapes from camera
    const targets: Shape[] = [];
    const initTargets = (): void => {
        // initialize targets with 4 default points
        targets.length = 0;
        targets.push({ x: 0.1, y: 0.1, radius: 0.01, label: "20 | 1" });
        targets.push({ x: 0.2, y: 0.1, radius: 0.01, label: "6 | 10" });
        targets.push({ x: 0.3, y: 0.1, radius: 0.01, label: "3 | 19" });
        targets.push({ x: 0.4, y: 0.1, radius: 0.01, label: "11 | 14" });
    };
    if (cam.calibration_points.length !== 4) {
        // database needs to have exactly 4 points
        initTargets();
    } else {
        // populate targets from saved points
        for (const calibPoint of cam.calibration_points) {
            targets.push({
                x: calibPoint.x,
                y: calibPoint.y,
                radius: 0.01,
                label: calibPoint.label,
            });
        }
    }

    // drag related vars
    let isDragging = false;
    let startX: number = -1;
    let startY: number = -1;
    let selectedShapeIndex: number;

    // redraw targets/shapes and the image
    const updateCanvas = (): void => {
        if (ctx !== null && ctx !== undefined && canvas !== null) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawImageScaled(img, ctx);
            drawShapesScaled(targets, ctx);
        }
    };

    // resize event to update offset
    const handleResize = (): void => {
        if (canvas !== null && wrapperRef.current !== null) {
            // calculate new canvas size based on wrapper
            canvas.width = wrapperRef.current.clientWidth - 10;
            const imgRatio = img.height / img.width;
            canvas.height = canvas.width * imgRatio;
            // update offset
            offset = canvas.getBoundingClientRect();
            updateCanvas();
        }
    };
    // scroll event to set offset
    // declared as imperative because the event happens on the parent component
    useImperativeHandle(ref, () => ({
        handleScroll() {
            handleResize();
            const fakeEvent = new MouseEvent("mousemove");
            zoomFunction(fakeEvent);
        },
        getCalibPoints() {
            // convert shapes to calibration points
            return targets.map((target, i) => {
                return { x: target.x, y: target.y, label: target.label };
            });
        },
        clearCalibPoints() {
            targets[0].x = 0.5;
            targets[0].y = 0.5;
        },
    }));

    // dragging events to move targets/shapes
    const handleMouseDown = (e: MouseEvent): void => {
        if (canvas !== null) {
            e.preventDefault();
            e.stopPropagation();
            startX = e.clientX - offset.left;
            startY = e.clientY - offset.top;
            // check if mouse is inside shape
            for (let i = 0; i < targets.length; i++) {
                if (isInsideShape(startX, startY, targets[i], canvas)) {
                    selectedShapeIndex = i;
                    isDragging = true;
                    return;
                }
            }
        }
    };
    const handleMouseUp = (e: MouseEvent): void => {
        // return if we're not dragging
        if (!isDragging) {
            return;
        }
        e.preventDefault();
        e.stopPropagation();
        isDragging = false;
    };
    const handleMouseMove = (e: MouseEvent): void => {
        // return if we're not dragging
        if (!isDragging) {
            return;
        }
        if (canvas !== null) {
            e.preventDefault();
            e.stopPropagation();
            // calculate the current mouse position
            const mouseX = e.clientX - offset.left;
            const mouseY = e.clientY - offset.top;
            // how far has the mouse dragged from its previous mousemove position?
            const dx = mouseX - startX;
            const dy = mouseY - startY;
            // calculate the distance in percentage of canvas width
            const px = dx / canvas.width;
            const py = dy / canvas.height;
            // move the selected shape by the drag distance
            const selectedShape = targets[selectedShapeIndex];
            selectedShape.x += px;
            selectedShape.y += py;
            // clear the canvas and redraw all shapes
            updateCanvas();
            // update the starting drag position (== the current mouse position)
            startX = mouseX;
            startY = mouseY;
        }
    };
    const handleMouseOut = (e: MouseEvent): void => {
        // return if we're not dragging
        if (!isDragging) {
            return;
        }
        e.preventDefault();
        e.stopPropagation();
        isDragging = false;
    };

    // zoom event to show zoom canvas on mouse move
    const zoomFunction = (e: MouseEvent): void => {
        if (
            zoomCtx !== null &&
            zoomCtx !== undefined &&
            zoom !== null &&
            canvas !== null
        ) {
            // size and zoom factor
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
        }
    };

    // Use effect hook to add all events and remove them when this components get unmounted
    useEffect(() => {
        // load canvas context after rendering
        canvas = canvasRef.current;
        ctx = canvasRef.current?.getContext("2d");
        zoom = zoomRef.current;
        zoomCtx = zoomRef.current?.getContext("2d");
        if (ctx !== null && ctx !== undefined && canvas !== null) {
            // onload function (Should be called one time on load)

            const ws = new WebSocket(url);

            ws.onmessage = (e) => {
                const b64String: string = e.data;
                img.src = "data: image:jpeg;base64, " + b64String;
                // set img src state, so no reflash happening on rerender
                setImgSrc("data: image:jpeg;base64, " + b64String);
            };

            img.onload = () => {
                // initialize offset and draw image on current size
                handleResize();
            };
            // update canvas offset on resize
            window.addEventListener("resize", handleResize);
            // mouse events for dragging around targets/shapes
            wrapperRef.current?.addEventListener("mousedown", handleMouseDown);
            wrapperRef.current?.addEventListener("mouseup", handleMouseUp);
            wrapperRef.current?.addEventListener("mousemove", handleMouseMove);
            wrapperRef.current?.addEventListener("mouseout", handleMouseOut);
            // Zoom mousemove event
            wrapperRef.current?.addEventListener("mousemove", zoomFunction);
            // remove event listener
            return () => {
                window.removeEventListener("resize", handleResize);
                wrapperRef.current?.removeEventListener(
                    "mousedown",
                    handleMouseDown,
                );
                wrapperRef.current?.removeEventListener(
                    "mouseup",
                    handleMouseUp,
                );
                wrapperRef.current?.removeEventListener(
                    "mousemove",
                    handleMouseMove,
                );
                wrapperRef.current?.removeEventListener(
                    "mouseout",
                    handleMouseOut,
                );
                // Zoom ctx
                wrapperRef.current?.removeEventListener(
                    "mousemove",
                    zoomFunction,
                );
                ws.close();
            };
        }
    }, [cam]);
    return (
        <Group ref={wrapperRef} pl="md">
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
});

CalibrationCanvas.displayName = "CalibrationCanvas";
export { CalibrationCanvas };

/**
 * Help function to check if given coordinates are inside target/shape
 * @param mx x coord
 * @param my y coord
 * @param shape given shape
 * @returns true if cord is inside shape
 */
const isInsideShape = (
    mx: number,
    my: number,
    shape: Shape,
    canvas: HTMLCanvasElement,
): boolean => {
    const dx = mx - shape.x * canvas.width;
    const dy = my - shape.y * canvas.height;
    // math test to see if mouse is inside circle
    const radius = shape.radius * canvas.width;
    if (dx * dx + dy * dy < radius * radius) {
        // yes, mouse is inside this circle
        return true;
    } else {
        return false;
    }
};

const drawImageScaled = (
    img: HTMLImageElement,
    ctx: CanvasRenderingContext2D,
): void => {
    // calculate image canvas ratio
    const canvas = ctx.canvas;
    const hRatio = canvas.width / img.width;
    const vRatio = canvas.height / img.height;
    const ratio = Math.min(hRatio, vRatio);
    // calculate center
    const centerShiftX = (canvas.width - img.width * ratio) / 2;
    const centerShiftY = (canvas.height - img.height * ratio) / 2;
    // clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // draw image
    ctx.drawImage(
        img,
        0,
        0,
        img.width,
        img.height,
        centerShiftX,
        centerShiftY,
        img.width * ratio,
        img.height * ratio,
    );
};

const drawShapesScaled = (
    shapes: Shape[],
    ctx: CanvasRenderingContext2D,
): void => {
    // calculate image canvas ratio
    const canvas = ctx.canvas;
    for (let i = 0; i < shapes.length; i++) {
        const shape = shapes[i];
        const x = shape.x * canvas.width;
        const y = shape.y * canvas.height;
        const r = shape.radius * canvas.width;
        ctx.strokeStyle = "red";
        ctx.lineWidth = 2;
        ctx.stroke(
            new Path2D(
                `M${x} ${y}m-${r} 0
                a ${r} ${r} 0 1 0 ${r * 2} 0
                a ${r} ${r} 0 1 0 ${-r * 2} 0`,
            ),
        );
        ctx.stroke(new Path2D(`M${x} ${y + 1}l0 4`));
        ctx.stroke(new Path2D(`M${x} ${y - 1}l0 -4`));
        ctx.stroke(new Path2D(`M${x + 1} ${y}l4 0`));
        ctx.stroke(new Path2D(`M${x - 1} ${y}l-4 0`));
        ctx.fillStyle = "red";
        const textProps = ctx.measureText(shape.label);
        ctx.fillText(shape.label, x - 0.5 * textProps.width, y - r - 5);
    }
};
