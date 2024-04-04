/**
 * Service to do all api calls with axios. Import functions when needed
 */
import axios, { type AxiosInstance, type AxiosResponse } from "axios";
import { type DartboardProps } from "../components/Dartboard/dartboard";
import { type DartboardCreateProps } from "../components/Dartboard/create-form";

// Create a new Axios instance
// TODO: get url from settings
const api: AxiosInstance = axios.create({
    baseURL: "http://127.0.0.1:7878/api/v1",
});

/**
 * Get all Dartboards
 */
export async function getDartboards(): Promise<
    AxiosResponse<DartboardProps[]>
> {
    return await api.get("/dartboards");
}

/**
 * Create Dartboard
 */
export async function createDartboard(
    data: DartboardCreateProps,
): Promise<AxiosResponse<DartboardProps>> {
    return await api.post("/dartboards", data);
}

/**
 * Get Dartboard
 */
export async function getDartboard(
    id: string,
): Promise<AxiosResponse<DartboardProps>> {
    return await api.get("/dartboards/" + id);
}

/**
 * Delete Dartboard
 */
export async function deleteDartboard(
    id: string,
): Promise<AxiosResponse<DartboardProps>> {
    return await api.delete("/dartboards/" + id);
}
