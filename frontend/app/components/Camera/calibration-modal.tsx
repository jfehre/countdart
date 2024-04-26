import { type CamSchema } from "@/app/types/schemas";
import { Modal } from "@mantine/core";
import React, { useRef, type ReactElement } from "react";
import {
    CalibrationCanvas,
    type CalibrationCanvasHandle,
} from "./calibration-canvas";

export interface CalibrationModalProps {
    opened: boolean;
    onClose: () => void;
    cam: CamSchema;
}

export function CalibrationModal({
    opened,
    onClose,
    cam,
}: CalibrationModalProps): ReactElement {
    const childRef = useRef<CalibrationCanvasHandle>(null);

    return (
        <Modal
            opened={opened}
            onClose={onClose}
            keepMounted={false}
            title="Calibration View"
            size={"80%"}
            lockScroll={false}
            onScrollCapture={(e) => {
                childRef.current?.handleScroll();
            }}
        >
            <CalibrationCanvas cam={cam} ref={childRef} />
        </Modal>
    );
}
