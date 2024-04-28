import { type CamPatchSchema, type CamSchema } from "@/app/types/schemas";
import { Button, Modal } from "@mantine/core";
import React, { useRef, type ReactElement } from "react";
import {
    CalibrationCanvas,
    type CalibrationCanvasHandle,
} from "./calibration-canvas";

export interface CalibrationModalProps {
    opened: boolean;
    onClose: () => void;
    cam: CamSchema;
    patchFunc: (id: string, patchData: CamPatchSchema) => void;
    setIsCalibrated: (calibrated: boolean) => void;
}

export function CalibrationModal({
    opened,
    onClose,
    cam,
    patchFunc,
    setIsCalibrated,
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
            <Button
                onClick={() => {
                    // get patchdata from Child and call given patchFunc to save Calibration
                    const calibPoints = childRef.current?.getCalibPoints();
                    const patchData = {
                        calibration_points: calibPoints,
                    };
                    patchFunc(cam.id, patchData);
                    setIsCalibrated(true);
                }}
                ml="md"
                mt="md"
            >
                Save Calibration
            </Button>
            <Button
                onClick={() => {
                    // remove calibration points
                    const patchData = {
                        calibration_points: [],
                    };
                    patchFunc(cam.id, patchData);
                    childRef.current?.clearCalibPoints();
                    setIsCalibrated(false);
                }}
                ml="sm"
                mt="md"
            >
                Reset Calibration
            </Button>
        </Modal>
    );
}
