import axios from "axios";
import { getAuthToken } from "@/utils/auth";
import type {
  FirmwareLog,
  LogsListParams,
  PaginatedApiResponse,
  ApiResponse,
  ApiError,
  LogFilterOptions,
} from "@/types";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_VERSION = import.meta.env.VITE_API_VERSION || "v1";

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/${API_VERSION}`,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
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

// Response interceptor for error handling
api.interceptors.response.use(
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

interface PaginatedLogResponse extends PaginatedApiResponse<FirmwareLog> {
  filter_options: LogFilterOptions;
}

export const logController = {
  /**
   * Get all firmware update logs
   */
  async getAllLogs(params?: LogsListParams): Promise<PaginatedLogResponse> {
    const cleanParams = Object.fromEntries(
      Object.entries(params || {}).filter(
        ([, value]) => value !== undefined && value !== "",
      ),
    );

    const response = await api.get("/log/", { params: cleanParams });
    return response.data;
  },

  /**
   * Get log detail by session_id
   */
  async getLogDetail(sessionId: string): Promise<ApiResponse<FirmwareLog>> {
    const response = await api.get(`/log/detail/${sessionId}`);
    return response.data;
  },

  /**
   * Delete log data by session_id
   */
  async deleteLog(sessionId: string): Promise<void> {
    await api.delete(`/log/delete/${sessionId}`);
  },

  /**
   * Export logs with filters
   */
  async exportLogs(params: Record<string, string>): Promise<void> {
    try {
      // Send request - let backend handle filename generation
      const response = await api.get("/log/export", {
        params: params,
        responseType: "blob", // For binary data
      });

      // Extract filename from Content-Disposition header (if CORS allows it)
      const contentDisposition = response.headers["content-disposition"];
      let filename = `firmware_logs.${params.type || "csv"}`; // Default fallback

      if (contentDisposition) {
        // Backend provided filename via Content-Disposition header
        const filenameMatch = contentDisposition.match(/filename=(.+)/);
        if (filenameMatch) {
          filename = filenameMatch[1].replace(/"/g, ""); // Remove quotes
        }
      } else {
        // Fallback if CORS is blocking the header
        // CORS is blocking the request header, generate filename based on parameters
        const baseFilename = params.filename || "firmware_logs";

        if (params.with_datetime === "true") {
          const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
          filename = `${baseFilename}_${today}.${params.type || "csv"}`;
        } else {
          filename = `${baseFilename}.${params.type || "csv"}`;
        }
      }

      // Create blob and download
      const blob = new Blob([response.data], {
        type: response.headers["content-type"] || "application/octet-stream",
      });

      // Download the file
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Export error:", error);
      throw error;
    }
  },
};
