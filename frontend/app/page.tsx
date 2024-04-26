"use client";

import React, { type ReactElement } from "react";
import { CalibrationModal } from "./components/Camera/calibration-modal";
import { useDisclosure } from "@mantine/hooks";
import { Button } from "@mantine/core";

export default function Home(): ReactElement {
    const [calibrateModalState, calibrateModalHandler] = useDisclosure(false);

    return (
        <div>
            <h1>Start Page</h1>
            <Button onClick={calibrateModalHandler.open}></Button>
            <CalibrationModal
                opened={calibrateModalState}
                onClose={calibrateModalHandler.close}
                cam={undefined}
            />
        </div>
    );
}
