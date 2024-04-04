/**
 * Service to do all api calls with axios. Import functions when needed
 */
import axios, { type AxiosInstance, type AxiosResponse } from "axios";
import { type DartboardSchema } from "../components/Dartboard/dartboard";
import { type DartboardCreateSchema } from "../components/Dartboard/create-form";
import {
    type CamHardwareSchema,
    type CamSchema,
} from "../components/Camera/camera-overview";
import { type CamCreateSchema } from "../components/Camera/create-form";

// Create a new Axios instance
// TODO: get url from settings
const api: AxiosInstance = axios.create({
    baseURL: "http://127.0.0.1:7878/api/v1",
});

/**
 * Get all Dartboards
 */
export async function getDartboards(): Promise<
    AxiosResponse<DartboardSchema[]>
> {
    return await api.get("/dartboards");
}

/**
 * Create Dartboard
 */
export async function createDartboard(
    data: DartboardCreateSchema,
): Promise<AxiosResponse<DartboardSchema>> {
    return await api.post("/dartboards", data);
}

/**
 * Get Dartboard
 */
export async function getDartboard(
    id: string,
): Promise<AxiosResponse<DartboardSchema>> {
    return await api.get("/dartboards/" + id);
}

/**
 * Delete Dartboard
 */
export async function deleteDartboard(
    id: string,
): Promise<AxiosResponse<DartboardSchema>> {
    return await api.delete("/dartboards/" + id);
}

/**
 * Get Cams
 */
export async function getCams(
    camIds: string[] = [],
): Promise<AxiosResponse<CamSchema[]>> {
    return await api.get("/cams");
}

/**
 * Get Hardware Cams
 */
export async function getCamsHardware(): Promise<
    AxiosResponse<CamHardwareSchema[]>
> {
    return await api.get("/cams/find");
}

/**
 * Create Cam
 */
export async function createCam(
    data: CamCreateSchema,
): Promise<AxiosResponse<CamSchema>> {
    return await api.post("/cams", data);
}

/**
 * Delete Cam
 */
export async function deleteCam(id: string): Promise<AxiosResponse<CamSchema>> {
    return await api.delete("/cams/" + id);
}
