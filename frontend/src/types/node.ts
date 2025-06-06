export interface Node {
  _id: string;
  created_at: string;
  latest_updated: string;
  node_location: string;
  node_type: string;
  node_id: string;
  node_codename: string;
  description?: string;
  firmware_url: string;
  firmware_version: string;
}

export interface AddNodeRequest {
  description?: string;
  node_id: string;
  node_location: string;
  node_type: string;
}

export interface AddFirmwareRequest {
  firmware_url: string;
  firmware_version: string;
}

export interface EditFirmwareRequest {
  description?: string;
}

export interface NodesListParams {
  page?: number;
  page_size?: number;
  node_location?: string;
  node_type?: string;
}
