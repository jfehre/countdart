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

export interface CamSchema {
    card_name: string;
    active: boolean;
    hardware_id: number;
    id: string;
}

export interface CamCreateSchema {
    card_name: string;
    hardware_id: number;
}

export interface CamHardwareSchema {
    card_name: string;
    hardware_id: number;
}
