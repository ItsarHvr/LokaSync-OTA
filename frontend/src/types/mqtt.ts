export interface MQTTPublishPayload {
  node_codename: string;
  firmware_url: string;
  firmware_version: string;
  session_id: string;
}

export interface MQTTConnectionOptions {
  username?: string;
  password?: string;
  clientId?: string;
  clean?: boolean;
  connectTimeout?: number;
  reconnectPeriod?: number;
}
