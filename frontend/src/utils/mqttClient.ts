import mqtt from "mqtt";
import type { MQTTPublishPayload } from "@/types";

// Define the MQTT client type locally to avoid import issues
type MQTTClient = ReturnType<typeof mqtt.connect>;

export interface LogMQTTMessage {
  node_codename: string;
  node_mac: string;
  firmware_version: string;
  firmware_size_kb: number;
  download_started_at: string;
  bytes_written: number;
  download_duration_sec: number;
  download_speed_kbps: number;
  download_completed_at: string;
  flash_status: "in progress" | "success" | "failed";
  session_id: string;
}

export interface MonitoringMQTTMessage {
  node_codename: string;
  node_mac?: string;
  timestamp?: string;
  sensor_data?: Record<string, unknown>;
  // Add direct ESP32 format support
  temperature?: number;
  humidity?: number;
}

class MQTTManager {
  private client: MQTTClient | null = null;
  private isConnected: boolean = false;
  private connectionCallbacks: Array<(connected: boolean) => void> = [];
  private logCallbacks: Array<(message: LogMQTTMessage) => void> = [];
  private monitoringCallbacks: Array<(message: MonitoringMQTTMessage) => void> =
    [];

  constructor() {
    this.connect();
  }

  private connect() {
    const brokerUrl =
      import.meta.env.VITE_MQTT_BROKER_URL || "wss://broker.emqx.io:8084/mqtt";
    const username = import.meta.env.VITE_MQTT_USERNAME || "";
    const password = import.meta.env.VITE_MQTT_PASSWORD || "";

    try {
      this.client = mqtt.connect(brokerUrl, {
        username: username || undefined,
        password: password || undefined,
        clientId: `lokasync_frontend_${Math.random().toString(16).substring(2, 10)}`,
        clean: true,
        connectTimeout: 4000,
        reconnectPeriod: 1000,
      });

      this.client.on("connect", () => {
        console.log("MQTT connected");
        this.isConnected = true;
        this.notifyConnectionChange(true);
        this.subscribeToTopics();
      });

      this.client.on("disconnect", () => {
        console.log("MQTT disconnected");
        this.isConnected = false;
        this.notifyConnectionChange(false);
      });

      this.client.on("error", (error) => {
        console.error("MQTT connection error:", error);
        this.isConnected = false;
        this.notifyConnectionChange(false);
      });

      this.client.on("offline", () => {
        console.log("MQTT offline");
        this.isConnected = false;
        this.notifyConnectionChange(false);
      });

      this.client.on("message", (topic, message) => {
        this.handleMessage(topic, message);
      });
    } catch (error) {
      console.error("Failed to create MQTT connection:", error);
      this.isConnected = false;
      this.notifyConnectionChange(false);
    }
  }

  private subscribeToTopics() {
    if (!this.client || !this.isConnected) return;

    const logTopic =
      import.meta.env.VITE_MQTT_SUB_TOPIC_LOG || "LokaSync/Web/DisplayLog";
    const monitoringTopic =
      import.meta.env.VITE_MQTT_SUB_TOPIC_MONITORING ||
      "LokaSync/Web/DisplayMonitoring";

    this.client.subscribe([logTopic, monitoringTopic], { qos: 1 }, (error) => {
      if (error) {
        console.error("MQTT subscription error:", error);
      } else {
        console.log("Successfully subscribed to topics:", [
          logTopic,
          monitoringTopic,
        ]);
      }
    });
  }

  private handleMessage(topic: string, message: Buffer) {
    try {
      const messageString = message.toString();
      const data = JSON.parse(messageString);

      const logTopic =
        import.meta.env.VITE_MQTT_SUB_TOPIC_LOG || "LokaSync/Web/DisplayLog";
      const monitoringTopic =
        import.meta.env.VITE_MQTT_SUB_TOPIC_MONITORING ||
        "LokaSync/Web/DisplayMonitoring";

      if (topic === logTopic) {
        console.log("Received log message:", data);
        this.notifyLogMessage(data as LogMQTTMessage);
      } else if (topic === monitoringTopic) {
        console.log("Received monitoring message:", data);
        this.notifyMonitoringMessage(data as MonitoringMQTTMessage);
      }
    } catch (error) {
      console.error("Error parsing MQTT message:", error);
    }
  }

  private notifyConnectionChange(connected: boolean) {
    this.connectionCallbacks.forEach((callback) => callback(connected));
  }

  private notifyLogMessage(message: LogMQTTMessage) {
    this.logCallbacks.forEach((callback) => callback(message));
  }

  private notifyMonitoringMessage(message: MonitoringMQTTMessage) {
    this.monitoringCallbacks.forEach((callback) => callback(message));
  }

  public onConnectionChange(callback: (connected: boolean) => void) {
    this.connectionCallbacks.push(callback);

    // Return unsubscribe function
    return () => {
      const index = this.connectionCallbacks.indexOf(callback);
      if (index > -1) {
        this.connectionCallbacks.splice(index, 1);
      }
    };
  }

  public onLogMessage(callback: (message: LogMQTTMessage) => void) {
    this.logCallbacks.push(callback);

    // Return unsubscribe function
    return () => {
      const index = this.logCallbacks.indexOf(callback);
      if (index > -1) {
        this.logCallbacks.splice(index, 1);
      }
    };
  }

  public onMonitoringMessage(
    callback: (message: MonitoringMQTTMessage) => void,
  ) {
    this.monitoringCallbacks.push(callback);

    // Return unsubscribe function
    return () => {
      const index = this.monitoringCallbacks.indexOf(callback);
      if (index > -1) {
        this.monitoringCallbacks.splice(index, 1);
      }
    };
  }

  public getConnectionStatus(): boolean {
    return this.isConnected;
  }

  public async publishFirmwareUpdate(
    payload: MQTTPublishPayload,
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.client || !this.isConnected) {
        reject(new Error("MQTT client not connected"));
        return;
      }

      const topic =
        import.meta.env.VITE_MQTT_PUB_TOPIC ||
        "LokaSync/CloudOTA/FirmwareUpdate";
      const message = JSON.stringify(payload);

      this.client.publish(topic, message, { qos: 1 }, (error) => {
        if (error) {
          console.error("MQTT publish error:", error);
          reject(error);
        } else {
          console.log("MQTT message published:", { topic, payload });
          resolve();
        }
      });
    });
  }

  public disconnect() {
    if (this.client) {
      this.client.end();
      this.client = null;
      this.isConnected = false;
      this.notifyConnectionChange(false);
    }
  }
}

// Export singleton instance
export const mqttManager = new MQTTManager();
