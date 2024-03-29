/**
 * Service to do all api calls with axios. Import functions when needed
 */
import axios, { type AxiosInstance, type AxiosResponse } from "axios";

// Create a new Axios instance
// TODO: get url from settings
const api: AxiosInstance = axios.create({
    baseURL: "http://127.0.0.1:7878/api/v1",
});

/**
 * Get all Dartboards
 */
export async function getDartboards(): Promise<AxiosResponse> {
    return await api.get("/dartboards");
}
