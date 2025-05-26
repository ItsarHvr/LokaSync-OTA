import { fetchWithAuth, createQueryParams } from "../utils/api";
import type { Firmware, FirmwareResponse } from "../types";
import { auth } from "../firebase";
import { mqttController } from "./MQTTController";

// Define return types for API endpoints
type ApiResponse = {
  message: string;
  statusCode: number;
};

// Define types for backend responses
interface BackendFirmwareResponse {
  message: string;
  status_code?: number;
  statusCode?: number;
  page: number;
  page_size?: number;
  size?: number;
  total_data?: number;
  totalData?: number;
  total_page?: number;
  totalPage?: number;
  filter_options?: {
    node_id?: number[];
    node_location?: string[];
    sensor_type?: string[];
  };
  filterOptions?: {
    nodeId?: number[];
    nodeLocation?: string[];
    sensorType?: string[];
  };
  firmware_data?: BackendFirmwareItem[];
  firmwareData?: BackendFirmwareItem[];
}

interface BackendFirmwareItem {
  firmware_description?: string;
  firmwareDescription?: string;
  firmware_version?: string;
  firmwareVersion?: string;
  firmware_url?: string;
  firmwareUrl?: string;
  node_id?: number;
  nodeId?: number;
  node_location?: string;
  nodeLocation?: string;
  node_name?: string;
  nodeName?: string;
  sensor_type?: string;
  sensorType?: string;
}

// FirmwareController for handling firmware-related API calls
export const FirmwareController = {
  // Get all firmware with optional filters
  async getAllFirmware(
    page = 1,
    size = 10,
    filters: {
      nodeId?: number;
      nodeLocation?: string;
      sensorType?: string;
    } = {},
  ): Promise<FirmwareResponse> {
    try {
      const queryParams = createQueryParams({
        page,
        page_size: size,  // Match backend parameter name
        node_id: filters.nodeId,  // Match backend parameter name
        node_location: filters.nodeLocation,  // Match backend parameter name
        sensor_type: filters.sensorType,  // Match backend parameter name
      });

      const response = await fetchWithAuth<BackendFirmwareResponse>(`/firmware${queryParams}`, {
        method: "GET"  // Explicitly set method to GET
      });
      
      // Transform snake_case to camelCase for frontend consumption
      const transformedResponse: FirmwareResponse = {
        message: response.message,
        statusCode: response.status_code || response.statusCode || 200,
        page: response.page,
        size: response.page_size || response.size || size,
        totalData: response.total_data || response.totalData || 0,
        totalPage: response.total_page || response.totalPage || 1,
        filterOptions: {
          nodeId: response.filter_options?.node_id || response.filterOptions?.nodeId || [],
          nodeLocation: response.filter_options?.node_location || response.filterOptions?.nodeLocation || [],
          sensorType: response.filter_options?.sensor_type || response.filterOptions?.sensorType || [],
        },
        firmwareData: (response.firmware_data || response.firmwareData || []).map((item) => ({
          firmwareDescription: item.firmware_description || item.firmwareDescription || '',
          firmwareVersion: item.firmware_version || item.firmwareVersion || '',
          firmwareUrl: item.firmware_url || item.firmwareUrl || '',
          nodeId: item.node_id || item.nodeId || 0,
          nodeLocation: item.node_location || item.nodeLocation || '',
          nodeName: item.node_name || item.nodeName || '',
          sensorType: item.sensor_type || item.sensorType || '',
        })),
      };
      
      return transformedResponse;
    } catch (err) {
      console.error(`Error fetching firmware data: ${err}`);
      throw err;
    }
  },

  // Add new firmware
  async addFirmware(
    firmware: Omit<Firmware, "nodeName">,
    file?: File,
  ): Promise<ApiResponse> {
    if (file) {
      // If file is provided, use FormData
      const formData = new FormData();
      formData.append("file", file);
      
      // Convert camelCase to snake_case for backend
      formData.append("node_id", String(firmware.nodeId));
      formData.append("node_location", firmware.nodeLocation);
      formData.append("sensor_type", firmware.sensorType);
      formData.append("firmware_version", firmware.firmwareVersion);
      formData.append("firmware_description", firmware.firmwareDescription);
      
      return fetchWithAuth<ApiResponse>("/firmware/add", {
        method: "POST",
        body: formData,
      });
    } else {
      // If no file, use JSON with snake_case properties
      const snakeCaseFirmware = {
        node_id: firmware.nodeId,
        node_location: firmware.nodeLocation,
        sensor_type: firmware.sensorType,
        firmware_version: firmware.firmwareVersion,
        firmware_description: firmware.firmwareDescription,
        firmware_url: firmware.firmwareUrl,
      };
      
      return fetchWithAuth<ApiResponse>("/firmware/add", {
        method: "POST",
        body: JSON.stringify(snakeCaseFirmware),
      });
    }
  },

  // Update firmware
  async updateFirmware(
    firmware: Partial<Firmware>,
    file?: File,
  ): Promise<ApiResponse> {
    if (file) {
      // If file is provided, use FormData
      const formData = new FormData();
      formData.append("file", file);
      
      // Convert camelCase to snake_case for backend
      if (firmware.nodeId !== undefined) formData.append("node_id", String(firmware.nodeId));
      if (firmware.nodeLocation !== undefined) formData.append("node_location", firmware.nodeLocation);
      if (firmware.sensorType !== undefined) formData.append("sensor_type", firmware.sensorType);
      if (firmware.firmwareVersion !== undefined) formData.append("firmware_version", firmware.firmwareVersion);
      if (firmware.firmwareDescription !== undefined) formData.append("firmware_description", firmware.firmwareDescription);
      if (firmware.nodeName !== undefined) formData.append("node_name", firmware.nodeName);

      return fetchWithAuth<ApiResponse>(`/firmware/update`, {
        method: "PUT",
        body: formData,
      });
    } else {
      // If no file, use JSON with snake_case properties
      const snakeCaseFirmware: Record<string, unknown> = {};
      
      if (firmware.nodeId !== undefined) snakeCaseFirmware.node_id = firmware.nodeId;
      if (firmware.nodeLocation !== undefined) snakeCaseFirmware.node_location = firmware.nodeLocation;
      if (firmware.sensorType !== undefined) snakeCaseFirmware.sensor_type = firmware.sensorType;
      if (firmware.firmwareVersion !== undefined) snakeCaseFirmware.firmware_version = firmware.firmwareVersion;
      if (firmware.firmwareDescription !== undefined) snakeCaseFirmware.firmware_description = firmware.firmwareDescription;
      if (firmware.firmwareUrl !== undefined) snakeCaseFirmware.firmware_url = firmware.firmwareUrl;
      if (firmware.nodeName !== undefined) snakeCaseFirmware.node_name = firmware.nodeName;
      
      return fetchWithAuth<ApiResponse>(`/firmware/update`, {
        method: "PUT",
        body: JSON.stringify(snakeCaseFirmware),
      });
    }
  },

  // Delete firmware
  async deleteFirmware(nodeId: string): Promise<ApiResponse> {
    return fetchWithAuth<ApiResponse>(`/firmware/delete/${nodeId}`, {
      method: "DELETE",
    });
  },

  // Get firmware by nodeId
  async getFirmwareByNodeId(nodeId: string): Promise<Firmware> {
    const response = await fetchWithAuth<BackendFirmwareItem>(`/firmware/${nodeId}`, {
      method: "GET"
    });
    
    // Transform snake_case to camelCase
    return {
      firmwareDescription: response.firmware_description || response.firmwareDescription || '',
      firmwareVersion: response.firmware_version || response.firmwareVersion || '',
      firmwareUrl: response.firmware_url || response.firmwareUrl || '',
      nodeId: response.node_id || response.nodeId || 0,
      nodeLocation: response.node_location || response.nodeLocation || '',
      nodeName: response.node_name || response.nodeName || '',
      sensorType: response.sensor_type || response.sensorType || '',
    };
  },

  // Generate JWT token for MQTT payload
  async generateMQTTToken(): Promise<string> {
    // This would call your backend to generate a token
    const token = await auth.currentUser?.getIdToken();
    return token || "";
  },
  
  // Publish firmware update via MQTT
  async publishFirmwareUpdate(firmware: Firmware): Promise<ApiResponse> {
    try {
      // Create the payload in snake_case format for the ESP devices
      const mqttPayload = {
        firmware_version: firmware.firmwareVersion,
        firmware_url: firmware.firmwareUrl,
        node_id: firmware.nodeId,
        node_location: firmware.nodeLocation,
        node_name: firmware.nodeName,
        sensor_type: firmware.sensorType
      };

      // Define MQTT topic for this specific node (you can adjust this as needed)
      const pubTopic = `LokaSync/CloudOTA/Firmware`;
      
      // Directly publish to MQTT broker
      console.log(`Publishing firmware update to ${pubTopic}:`, mqttPayload);
      mqttController.publish(pubTopic, mqttPayload);

      // Return a success response without calling the backend API
      return {
        message: `Firmware update published to ${firmware.nodeName}`,
        statusCode: 200
      };
    } catch (error) {
      console.error("Error publishing firmware update:", error);
      throw error;
    }
  },
};