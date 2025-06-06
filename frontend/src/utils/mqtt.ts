import type { MQTTPublishPayload } from "@/types";
import { generateSessionId } from "./sessionIdGenerator";

/**
 * Create MQTT publish payload for firmware update
 */
export const createMQTTPayload = (
  nodeCodename: string,
  firmwareUrl: string,
  firmwareVersion: string,
): MQTTPublishPayload => {
  return {
    node_codename: nodeCodename,
    firmware_url: firmwareUrl,
    firmware_version: firmwareVersion,
    session_id: generateSessionId(),
  };
};

/**
 * Convert Google Drive share URL to direct download URL
 */
export const convertGoogleDriveUrl = (shareUrl: string): string => {
  const fileIdMatch = shareUrl.match(/\/d\/([a-zA-Z0-9-_]+)/);
  if (fileIdMatch) {
    const fileId = fileIdMatch[1];
    return `https://drive.google.com/uc?export=download&id=${fileId}`;
  }
  return shareUrl; // Return original if not a Google Drive URL
};
