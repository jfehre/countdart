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
    name: string;
    active: boolean;
    source: number | string;
    type: string;
    id: string;
    calibration_points: CalibrationPoint[];
    cam_config: any;
}

export interface CamCreateSchema {
    name: string;
    source: number | string;
    type: string;
}

export interface CamPatchSchema {
    name?: string;
    active?: boolean;
    active_task?: string;
    calibration_points?: CalibrationPoint[];
    cam_config?: any;
}

export interface CamHardwareSchema {
    name: string;
    source: number;
}

export interface IntConfigSchema {
    name: string;
    description: string | undefined;
    type: string;
    default_value: number;
    value: number;
    max_value: number;
    min_value: number;
}

export interface BooleanConfigSchema {
    name: string;
    description: string | undefined;
    type: string;
    default_value: boolean;
    value: boolean;
}

export interface SelectConfigSchema {
    name: string;
    description: string | undefined;
    type: string;
    default_value: string;
    value: string;
    data: string[];
}

export type AllConfigSchema =
    | SelectConfigSchema
    | BooleanConfigSchema
    | IntConfigSchema;
