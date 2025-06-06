import { useState, useEffect } from "react";
import { mqttManager } from "@/utils/mqttClient";

export function useMQTTConnection() {
  const [isConnected, setIsConnected] = useState(
    mqttManager.getConnectionStatus(),
  );

  useEffect(() => {
    // Set initial status
    setIsConnected(mqttManager.getConnectionStatus());

    // Subscribe to connection changes
    const unsubscribe = mqttManager.onConnectionChange((connected) => {
      setIsConnected(connected);
    });

    // Cleanup on unmount
    return unsubscribe;
  }, []);

  return isConnected;
}
