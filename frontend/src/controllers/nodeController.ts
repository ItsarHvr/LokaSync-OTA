import axios from "axios";
import { getAuthToken } from "@/utils/auth";
import type {
  Node,
  NodesListParams,
  PaginatedApiResponse,
  ApiResponse,
  ApiError,
  AddNodeRequest,
  EditFirmwareRequest,
} from "@/types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_VERSION = import.meta.env.VITE_API_VERSION || "v1";
const RTO_MINUTES = parseInt(import.meta.env.VITE_RTO_MINUTES || "2");

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  timeout: RTO_MINUTES * 60 * 1000, // Convert minutes to milliseconds
  headers: {
    "Content-Type": "application/json",
  },
});

// Create a separate instance for file uploads with longer timeout and multipart support
const uploadApi = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  timeout: RTO_MINUTES * 60 * 1000, // 2 minutes timeout for uploads
  headers: {
    "Content-Type": "multipart/form-data",
  },
});

// Request interceptor to add auth token for both instances
const addAuthInterceptor = (instance: typeof api) => {
  instance.interceptors.request.use(
    async (config) => {
      const token = await getAuthToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    },
  );
};

// Response interceptor for error handling for both instances
const addResponseInterceptor = (instance: typeof api) => {
  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (error.response?.status === 401) {
        // Handle unauthorized access
        window.location.href = "/auth/login";
      }

      const apiError: ApiError = {
        message:
          error.response?.data?.message || error.message || "An error occurred",
        status_code: error.response?.status || 500,
      };

      return Promise.reject(apiError);
    },
  );
};

// Apply interceptors to both instances
addAuthInterceptor(api);
addAuthInterceptor(uploadApi);
addResponseInterceptor(api);
addResponseInterceptor(uploadApi);

// Updated interface for adding firmware
interface AddFirmwareRequest {
  firmware_version: string;
  firmware_file?: File;
  firmware_url?: string;
}

export const nodeController = {
  /**
   * Get all nodes
   */
  async getAllNodes(
    params?: NodesListParams,
  ): Promise<PaginatedApiResponse<Node>> {
    const cleanParams = Object.fromEntries(
      Object.entries(params || {}).filter(
        ([, value]) => value !== undefined && value !== "",
      ),
    );

    const response = await api.get("/node/", { params: cleanParams });
    return response.data;
  },

  /**
   * Get node detail by codename and optional firmware version
   */
  async getNodeDetail(
    nodeCodename: string,
    firmwareVersion?: string,
  ): Promise<ApiResponse<Node>> {
    const params = firmwareVersion ? { firmware_version: firmwareVersion } : {};
    const response = await api.get(`/node/detail/${nodeCodename}`, { params });
    return response.data;
  },

  /**
   * Create new node
   */
  async createNode(data: AddNodeRequest): Promise<ApiResponse<Node>> {
    const response = await api.post("/node/add-new", data);
    return response.data;
  },

  /**
   * Add firmware version to existing node
   */
  async addFirmware(
    nodeCodename: string,
    data: AddFirmwareRequest,
    onUploadProgress?: (progress: number) => void,
  ): Promise<ApiResponse<Node>> {
    const formData = new FormData();

    // Always add firmware_version
    formData.append("firmware_version", data.firmware_version);

    // Add either firmware_file OR firmware_url, but never both
    if (data.firmware_file) {
      formData.append("firmware_file", data.firmware_file);
      // DON'T add firmware_url when uploading file
    } else if (data.firmware_url) {
      formData.append("firmware_url", data.firmware_url);
      // DON'T add firmware_file when using URL
    }

    const response = await uploadApi.post(
      `/node/add-firmware/${nodeCodename}`,
      formData,
      {
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total && onUploadProgress) {
            const progress = (progressEvent.loaded / progressEvent.total) * 100;
            onUploadProgress(progress);
          }
        },
      },
    );

    return response.data;
  },

  /**
   * Edit firmware information
   */
  async editFirmware(
    nodeCodename: string,
    data: EditFirmwareRequest,
    firmwareVersion?: string,
  ): Promise<ApiResponse<Node>> {
    const params = firmwareVersion ? { firmware_version: firmwareVersion } : {};
    const response = await api.patch(
      `/node/edit-firmware/${nodeCodename}`,
      data,
      { params },
    );
    return response.data;
  },

  /**
   * Get all firmware versions for a node
   */
  async getFirmwareVersions(
    nodeCodename: string,
  ): Promise<ApiResponse<string[]>> {
    const response = await api.get(`/node/version/${nodeCodename}`);
    return response.data;
  },

  /**
   * Delete node or specific firmware version
   */
  async deleteNode(
    nodeCodename: string,
    firmwareVersion?: string,
  ): Promise<void> {
    const params = firmwareVersion ? { firmware_version: firmwareVersion } : {};
    await api.delete(`/node/delete/${nodeCodename}`, { params });
  },

  /**
   * Download firmware file for specific version
   */
  async downloadFirmware(
    nodeCodename: string,
    firmwareVersion: string,
    filename?: string,
  ): Promise<void> {
    try {
      // Use the correct endpoint with firmware_version parameter
      const response = await api.get(
        `/node/download-firmware/${nodeCodename}`,
        {
          params: { firmware_version: firmwareVersion },
          responseType: "blob",
        },
      );

      // Extract filename from Content-Disposition header if available
      const contentDisposition = response.headers["content-disposition"];
      let downloadFilename =
        filename || `${nodeCodename}_v${firmwareVersion}.bin`;

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=(.+)/);
        if (filenameMatch) {
          downloadFilename = filenameMatch[1].replace(/"/g, "");
        }
      }

      // Create blob and download
      const blob = new Blob([response.data], {
        type: response.headers["content-type"] || "application/octet-stream",
      });

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = downloadFilename;
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download failed:", error);
      throw new Error(
        error instanceof Error ? error.message : "Failed to download firmware",
      );
    }
  },
};
