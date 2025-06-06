export interface FirmwareLog {
  _id: string;
  created_at: string;
  session_id: string;
  node_mac: string;
  node_location: string;
  node_type: string;
  node_id: string;
  node_codename: string;
  firmware_version: string;
  download_started_at: string;
  firmware_size_kb: number;
  bytes_written: number;
  download_duration_sec: number;
  download_speed_kbps: number;
  download_completed_at: string;
  flash_completed_at: string;
  flash_status: "in progress" | "success" | "failed";
}

export interface LogsListParams {
  page?: number;
  page_size?: number;
  node_location?: string;
  node_type?: string;
  flash_status?: string;
}

export interface LogFilterOptions {
  node_locations: string[];
  node_types: string[];
  flash_statuses: string[];
}
