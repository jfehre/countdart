import React, {
    useRef,
    useEffect,
    type ReactElement,
    forwardRef,
    useImperativeHandle,
    useState,
} from "react";
import { useMantineColorScheme, useMantineTheme } from "@mantine/core";

/**
 * Component to draw a dartboard. The dartboard is a canvas element.
 * The component can be used to draw points on the dartboard.
 *
 * @param props React component props
 * @returns React component
 */
export const DartboardSketch = forwardRef((props, ref): ReactElement => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const { colorScheme } = useMantineColorScheme();
    const isDark = colorScheme === "dark";
    const theme = useMantineTheme();
    const [points, setPoints] = useState<Array<{ x: number; y: number }>>([]);

    // Define colors for the dartboard. The colors are different for dark and light mode.
    const colors = {
        segmentWhite: isDark ? "rgb(201, 201, 201)" : "rgb(255, 255, 255)",
        segmentBlack: "rgb(54, 53, 53)",
        segmentBlackRing: "rgb(99, 169, 65)",
        segmentWhiteRing: "rgb(200, 9, 17)",
        bull: "rgb(99, 169, 65)",
        doubleBull: "rgb(200, 9, 17)",
        pointCross: "rgb(255, 136, 0)",
        numberColor: isDark ? theme.colors.dark[0] : theme.colors.gray[7],
    };

    /**
     * draws the basic dartboard
     *
     * @param ctx
     * @returns
     */
    const drawDartboard = (ctx: CanvasRenderingContext2D): void => {
        const canvas = canvasRef.current;
        if (canvas === null) {
            return;
        }
        // define the size of the dartboard. Same as in the backend
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const outerDoubleRing = 170;
        const innerDoubleRing = 162;
        const outerTripleRing = 107;
        const innerTripleRing = 99;
        const bull = 31.8 / 2;
        const doubleBull = 12.7 / 2;

        const segments = [
            20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12,
            5,
        ];

        /**
         * draws a segment of the dartboard
         * @param startAngle
         * @param endAngle
         * @param innerRadius
         * @param outerRadius
         * @param color
         */
        const drawSegment = (
            startAngle: number,
            endAngle: number,
            innerRadius: number,
            outerRadius: number,
            color: string,
        ): void => {
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, outerRadius, startAngle, endAngle);
            ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true);
            ctx.closePath();
            ctx.fillStyle = color;
            ctx.fill();
            ctx.stroke();
        };

        /**
         * draws a number on the dartboard
         * @param angle
         * @param number
         */
        const drawNumber = (angle: number, number: number): void => {
            const x = centerX + (outerDoubleRing + 20) * Math.cos(angle);
            const y = centerY + (outerDoubleRing + 20) * Math.sin(angle);
            ctx.font = "20px Arial";
            ctx.fillStyle = colors.numberColor;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillText(number.toString(), x, y);
        };

        // Draw all segments
        const segmentAngle = (2 * Math.PI) / 20;
        const rotationAngle = -segmentAngle / 2 - Math.PI / 2;
        segments.forEach((segment, i) => {
            const startAngle = i * segmentAngle + rotationAngle;
            const endAngle = startAngle + segmentAngle;
            const color =
                i % 2 === 0 ? colors.segmentBlack : colors.segmentWhite;

            // Draw the main segment
            drawSegment(startAngle, endAngle, 0, innerDoubleRing, color);

            // Draw the double ring segment
            const doubleRingColor =
                i % 2 === 0 ? colors.segmentWhiteRing : colors.segmentBlackRing;
            drawSegment(
                startAngle,
                endAngle,
                innerDoubleRing,
                outerDoubleRing,
                doubleRingColor,
            );

            // Draw the triple ring segment
            const tripleRingColor =
                i % 2 === 0 ? colors.segmentWhiteRing : colors.segmentBlackRing;
            drawSegment(
                startAngle,
                endAngle,
                innerTripleRing,
                outerTripleRing,
                tripleRingColor,
            );

            // Draw the number
            const numberAngle = startAngle + segmentAngle / 2;
            drawNumber(numberAngle, segment);
        });

        // Draw bullseye
        ctx.beginPath();
        ctx.arc(centerX, centerY, bull, 0, 2 * Math.PI);
        ctx.fillStyle = colors.bull;
        ctx.fill();
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(centerX, centerY, doubleBull, 0, 2 * Math.PI);
        ctx.fillStyle = colors.doubleBull;
        ctx.fill();
        ctx.stroke();
    };

    /**
     * translate points from backend coordinates to canvas coordinates
     * In the backend the origin is in the center of the dartboard
     * @param x
     * @param y
     * @returns
     */
    const translatePoint = (x: number, y: number): [number, number] => {
        const canvas = canvasRef.current;
        if (canvas !== null) {
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            return [centerX + x, centerY - y];
        }
        return [x, y];
    };

    /**
     * draws a point on the dartboard canvas
     * this will also translate the point
     * @param x
     * @param y
     */
    const drawPoint = (x: number, y: number): void => {
        const canvas = canvasRef.current;
        if (canvas !== null) {
            const ctx = canvas.getContext("2d");
            if (ctx !== null) {
                const [canvasX, canvasY] = translatePoint(x, y);
                const size = 5;
                ctx.save();
                ctx.beginPath();
                // Draw diagonal cross
                ctx.moveTo(canvasX - size, canvasY - size);
                ctx.lineTo(canvasX + size, canvasY + size);
                ctx.moveTo(canvasX + size, canvasY - size);
                ctx.lineTo(canvasX - size, canvasY + size);
                ctx.strokeStyle = colors.pointCross;
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.restore();
            }
        }
    };

    /**
     * add a point to the state. This will redraw the points on the canvas
     * if the canvas is updated
     * @param x
     * @param y
     */
    const addPoint = (x: number, y: number): void => {
        setPoints((prevPoints) => [...prevPoints, { x, y }]);
    };

    /**
     * clear all points from the canvas and state
     */
    const clearPoints = (): void => {
        const canvas = canvasRef.current;
        if (canvas !== null) {
            const ctx = canvas.getContext("2d");
            if (ctx !== null) {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                drawDartboard(ctx);
                setPoints([]);
            }
        }
    };

    /**
     * useEffect to draw the dartboard and all points
     */
    useEffect(() => {
        const canvas = canvasRef.current;
        if (canvas !== null) {
            const ctx = canvas.getContext("2d");
            if (ctx !== null) {
                drawDartboard(ctx);
                points.forEach((point) => {
                    drawPoint(point.x, point.y);
                });
            }
        }
    }, [colors, points]);

    /**
     * expose drawPoint and clearPoints functions to parent component
     */
    useImperativeHandle(ref, () => ({
        drawPoint: addPoint,
        clearPoints,
    }));

    // return finished canvas
    return <canvas ref={canvasRef} width={400} height={400} />;
});

DartboardSketch.displayName = "DartboardSketch";
