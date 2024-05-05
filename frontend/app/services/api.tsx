/**
 * Service to do all api calls with axios. Import functions when needed
 */
import axios, { type AxiosInstance, type AxiosResponse } from "axios";
import {
    type DartboardPatchSchema,
    type CamCreateSchema,
    type CamHardwareSchema,
    type CamSchema,
    type DartboardCreateSchema,
    type DartboardSchema,
    type CamPatchSchema,
} from "../types/schemas";

export const host = "http://127.0.0.1:7878";
export const apiV1 = "/api/v1";

// Create a new Axios instance
// TODO: get url from settings
const api: AxiosInstance = axios.create({
    baseURL: host + apiV1,
});

/**
 * Check Health of connection
 */
export async function health(): Promise<AxiosResponse> {
    return await api.get("/health");
}
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
 * Patch Dartboard
 */
export async function patchDartboard(
    id: string | undefined,
    data: DartboardPatchSchema,
): Promise<AxiosResponse<DartboardSchema>> {
    if (id === undefined) {
        throw Error("Dartboard id is undefined");
    }
    return await api.patch("/dartboards/" + id, data);
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
 * Get Cams. Optional parameter contains list of all cam ids
 * to specify which cams should be returned.
 * If the list is empty send a request with [""]
 */
export async function getCams(
    camIds: string[] | undefined = undefined,
): Promise<AxiosResponse<CamSchema[]>> {
    if (camIds === undefined) {
        return await api.get("/cams");
    } else {
        // add empty string if no camids given
        if (camIds.length === 0) {
            camIds = [""];
        }
        return await api.get("/cams", {
            params: { id_list: camIds },
            paramsSerializer: { indexes: null },
        });
    }
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
 * Patch Cam
 */
export async function patchCam(
    id: string | undefined,
    data: CamPatchSchema,
): Promise<AxiosResponse<CamSchema>> {
    if (id === undefined) {
        throw Error("Cam id is undefined");
    }
    return await api.patch("/cams/" + id, data);
}

/**
 * Delete Cam
 */
export async function deleteCam(id: string): Promise<AxiosResponse<CamSchema>> {
    return await api.delete("/cams/" + id);
}

/**
 * Start Cam
 */
export async function startCam(id: string): Promise<AxiosResponse<CamSchema>> {
    return await api.get("/cams/" + id + "/start");
}

/**
 * Stop Cam
 */
export async function stopCam(id: string): Promise<AxiosResponse<CamSchema>> {
    return await api.get("/cams/" + id + "/stop");
}

/**
 * Get Cam FPS
 */
export async function getCamFps(id: string): Promise<AxiosResponse<number>> {
    return await api.get("/cams/" + id + "/fps");
}
