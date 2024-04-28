export interface DartboardSchema {
    name: string;
    active: boolean;
    id: string;
    cams: string[];
    active_celery_tasks: string[];
}

export interface DartboardCreateSchema {
    name: string;
}

export interface DartboardPatchSchema {
    name: string | undefined;
    active: boolean | undefined;
    cams: string[] | undefined;
    active_celery_tasks: string[] | undefined;
}

export interface CalibrationPoint {
    x: number;
    y: number;
    label: string;
}

export interface CamSchema {
    card_name: string;
    active: boolean;
    hardware_id: number;
    id: string;
    calibration_points: CalibrationPoint[];
}

export interface CamCreateSchema {
    card_name: string;
    hardware_id: number;
}

export interface CamPatchSchema {
    card_name?: string;
    active?: boolean;
    active_task?: string;
    calibration_points?: CalibrationPoint[];
}

export interface CamHardwareSchema {
    card_name: string;
    hardware_id: number;
}
