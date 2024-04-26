import { type CamSchema } from "@/app/types/schemas";
import { Modal } from "@mantine/core";
import React, { type ReactElement } from "react";
import { CalibrationCanvas } from "./calibration-canvas";

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
    return (
        <Modal
            opened={opened}
            onClose={onClose}
            keepMounted={false}
            title="Calibration View"
            size={"80%"}
        >
            <CalibrationCanvas cam={cam} />
        </Modal>
    );
}
