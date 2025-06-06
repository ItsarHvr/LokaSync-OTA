import { useState, useEffect, useCallback } from "react";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import Main from "@/components/layout/Main";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import {
  Thermometer,
  Droplets,
  Wifi,
  WifiOff,
  RefreshCw,
  Beaker,
  Zap,
  Info,
} from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";
import { usePageTitle } from "@/hooks/usePageTitle";
import { useMQTTConnection } from "@/hooks/useMQTTConnection";
import { mqttManager, type MonitoringMQTTMessage } from "@/utils/mqttClient";
import { ScrollToTop } from "@/components/ui/scroll-to-top";
import Squares from "@/components/background/Squares";
import {
  parseNodeCodename,
  getNodeDisplayName,
  type ParsedNodeCodename,
} from "@/utils/nodeCodenameParser";

// Extended sensor data interface to support different sensor types
interface SensorData {
  timestamp: string;
  time: string; // For display
  // Node 1: Temperature & Humidity
  temperature?: number;
  humidity?: number;
  // Node 2: TDS (Total Dissolved Solids)
  tds?: number;
  // Node 3: DS (Dissolved Solids/EC - Electrical Conductivity)
  ds?: number;
}

interface NodeData {
  codename: string;
  parsedInfo: ParsedNodeCodename;
  lastUpdate: string | null;
  isReceivingData: boolean;
  sensorHistory: SensorData[];
  currentValues: {
    temperature?: number;
    humidity?: number;
    tds?: number;
    ds?: number;
  };
}

// Type for sensor data from MQTT messages that might contain ds or ec
interface SensorMQTTMessage extends MonitoringMQTTMessage {
  ds?: number;
  ec?: number;
  tds?: number;
}

export default function Monitoring() {
  const [connectedNodes, setConnectedNodes] = useState<Map<string, NodeData>>(
    new Map(),
  );
  const [selectedNodeCodename, setSelectedNodeCodename] = useState<string>("");

  const isMQTTConnected = useMQTTConnection();
  usePageTitle("Monitoring");

  // Handle real-time monitoring messages from MQTT
  const handleMonitoringMessage = useCallback(
    (message: MonitoringMQTTMessage) => {
      console.log("Received monitoring message:", message);

      if (!message.node_codename) {
        console.error("Missing node_codename in message:", message);
        return;
      }

      const parsedNode = parseNodeCodename(message.node_codename);
      if (!parsedNode) {
        console.error("Unable to parse node codename:", message.node_codename);
        return;
      }

      // Extract sensor data based on message format
      const sensorData: Partial<SensorData> = {};

      // Handle different message formats
      if ("temperature" in message && "humidity" in message) {
        // Node 1: Temperature & Humidity
        sensorData.temperature = message.temperature as number;
        sensorData.humidity = message.humidity as number;
      } else if ("tds" in message) {
        // Node 2: TDS sensor
        sensorData.tds = message.tds as number;
      } else if ("ds" in message || "ec" in message) {
        // Node 3: DS/EC sensor
        const sensorMessage = message as SensorMQTTMessage;
        sensorData.ds = (sensorMessage.ds || sensorMessage.ec) as number;
      } else if (
        message.sensor_data &&
        typeof message.sensor_data === "object" &&
        message.sensor_data !== null
      ) {
        // Nested format
        const data = message.sensor_data as Record<string, unknown>;

        if (typeof data.temperature === "number")
          sensorData.temperature = data.temperature;
        if (typeof data.humidity === "number")
          sensorData.humidity = data.humidity;
        if (typeof data.tds === "number") sensorData.tds = data.tds;
        if (typeof data.ds === "number") sensorData.ds = data.ds;
        if (typeof data.ec === "number") sensorData.ds = data.ec; // EC and DS are related
      } else {
        console.error("Unknown sensor data format:", message);
        return;
      }

      const timestamp = new Date().toISOString();
      const timeDisplay = new Date().toLocaleTimeString("en-US", {
        hour12: false,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });

      const newSensorData: SensorData = {
        timestamp,
        time: timeDisplay,
        ...sensorData,
      };

      // Update nodes data
      setConnectedNodes((prevNodes) => {
        const updatedNodes = new Map(prevNodes);
        const nodeCodename = message.node_codename;

        const existingNode = updatedNodes.get(nodeCodename);

        if (existingNode) {
          // Update existing node
          const updatedHistory = [
            ...existingNode.sensorHistory,
            newSensorData,
          ].slice(-50);

          updatedNodes.set(nodeCodename, {
            ...existingNode,
            lastUpdate: timestamp,
            isReceivingData: true,
            sensorHistory: updatedHistory,
            currentValues: {
              ...existingNode.currentValues,
              ...sensorData,
            },
          });
        } else {
          // Add new node
          updatedNodes.set(nodeCodename, {
            codename: nodeCodename,
            parsedInfo: parsedNode,
            lastUpdate: timestamp,
            isReceivingData: true,
            sensorHistory: [newSensorData],
            currentValues: sensorData,
          });
        }

        // Auto-select the first node if none selected
        if (!selectedNodeCodename && updatedNodes.size > 0) {
          setSelectedNodeCodename(nodeCodename);
        }

        return updatedNodes;
      });
    },
    [selectedNodeCodename],
  );

  // Subscribe to MQTT monitoring messages
  useEffect(() => {
    const unsubscribe = mqttManager.onMonitoringMessage(
      handleMonitoringMessage,
    );
    return unsubscribe;
  }, [handleMonitoringMessage]);

  // Get all nodes as array
  const allNodes = Array.from(connectedNodes.values());

  // Get selected node data
  const selectedNode = selectedNodeCodename
    ? connectedNodes.get(selectedNodeCodename) || null
    : null;

  // Generate chart data for selected node
  const getChartData = () => {
    if (!selectedNode || selectedNode.sensorHistory.length === 0) {
      // Generate placeholder data
      const placeholderData: SensorData[] = Array.from(
        { length: 10 },
        (_, i) => ({
          time: `${String(new Date().getHours()).padStart(2, "0")}:${String(new Date().getMinutes() - 9 + i).padStart(2, "0")}`,
          timestamp: new Date(Date.now() - (9 - i) * 60000).toISOString(),
          temperature: 25,
          humidity: 50,
        }),
      );
      return placeholderData;
    }

    // Return last 50 points from selected node
    return selectedNode.sensorHistory
      .sort(
        (a, b) =>
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
      )
      .slice(-50);
  };

  const chartConfig = {
    temperature: {
      label: "Temperature (°C)",
      color: "hsl(142, 72%, 29%)", // Green
    },
    humidity: {
      label: "Humidity (%)",
      color: "hsl(32, 98%, 50%)", // Orange
    },
    tds: {
      label: "TDS (ppm)",
      color: "hsl(217, 91%, 60%)", // Blue
    },
    ds: {
      label: "DS/EC (μS/cm)",
      color: "hsl(262, 83%, 58%)", // Purple
    },
  };

  const clearHistory = () => {
    if (selectedNode) {
      setConnectedNodes((prevNodes) => {
        const updatedNodes = new Map(prevNodes);
        updatedNodes.set(selectedNode.codename, {
          ...selectedNode,
          sensorHistory: [],
          currentValues: {},
          isReceivingData: false,
          lastUpdate: null,
        });
        return updatedNodes;
      });
    }
  };

  const formatLastUpdate = (timestamp: string | null) => {
    if (!timestamp) return "No data received";
    return new Date(timestamp).toLocaleString("en-US", {
      hour12: false,
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  // Get sensor types from selected node
  const getSensorTypesFromNode = (node: NodeData | null) => {
    if (!node) return [];
    const sensorTypes = new Set<string>();
    Object.keys(node.currentValues).forEach((key) => {
      if (
        node.currentValues[key as keyof typeof node.currentValues] !== undefined
      ) {
        sensorTypes.add(key);
      }
    });
    return Array.from(sensorTypes);
  };

  const availableSensorTypes = getSensorTypesFromNode(selectedNode);

  // Format node location for display (capitalize properly)
  const formatNodeLocation = (location: string) => {
    return location
      .split("-")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join("-");
  };

  // Format node type for display
  const formatNodeType = (type: string) => {
    return type.charAt(0).toUpperCase() + type.slice(1).toLowerCase();
  };

  // Add a timeout mechanism to detect when data stops coming
  useEffect(() => {
    const timeoutIds = new Map<string, NodeJS.Timeout>();

    connectedNodes.forEach((node, codename) => {
      if (node.isReceivingData) {
        // Clear existing timeout
        const existingTimeoutId = timeoutIds.get(codename);
        if (existingTimeoutId) {
          clearTimeout(existingTimeoutId);
        }

        // Set new timeout for 30 seconds
        const timeoutId = setTimeout(() => {
          setConnectedNodes((prevNodes) => {
            const updatedNodes = new Map(prevNodes);
            const currentNode = updatedNodes.get(codename);
            if (currentNode) {
              updatedNodes.set(codename, {
                ...currentNode,
                isReceivingData: false,
              });
            }
            return updatedNodes;
          });
        }, 10000); // 10 seconds timeout

        timeoutIds.set(codename, timeoutId);
      }
    });

    // Cleanup function to clear timeouts on unmount
    return () => {
      timeoutIds.forEach((timeoutId) => clearTimeout(timeoutId));
    };
  }, [connectedNodes]);

  return (
    <div className="min-h-screen flex flex-col bg-background relative">
      {/* Squares Background Animation */}
      <div className="absolute inset-0 z-0">
        <Squares
          speed={0.2}
          squareSize={12}
          direction="diagonal"
          borderColor="#24371f"
          hoverFillColor="#284e13"
        />
      </div>

      {/* Content Layer */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <Header />
        <Main>
          <div className="space-y-6">
            {/* Header Section */}
            <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold">
                  Real-time Monitoring
                </h1>
                <p className="text-sm text-muted-foreground mt-1">
                  Monitor IoT sensor data from multiple nodes in real-time via
                  MQTT
                </p>
              </div>

              <div className="flex items-center gap-4">
                {/* MQTT Connection Status */}
                <div className="flex items-center gap-2">
                  {isMQTTConnected ? (
                    <>
                      <Wifi className="h-4 w-4 text-green-500" />
                      <span className="text-sm text-green-500">
                        MQTT Connected
                      </span>
                    </>
                  ) : (
                    <>
                      <WifiOff className="h-4 w-4 text-red-500" />
                      <span className="text-sm text-red-500">
                        MQTT Disconnected
                      </span>
                    </>
                  )}
                </div>

                {/* Clear History Button */}
                <Button
                  onClick={clearHistory}
                  // variant="outline"
                  size="sm"
                  disabled={!selectedNode}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Clear History
                </Button>
              </div>
            </div>

            {/* Node Selection and Parsed Information */}
            <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="h-5 w-5" />
                  Node Information
                </CardTitle>
                <CardDescription>
                  Select a node to view its parsed information and sensor data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 items-center">
                  {/* Node Selection */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Select Node</label>
                    <Select
                      value={selectedNodeCodename}
                      onValueChange={setSelectedNodeCodename}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Choose a node..." />
                      </SelectTrigger>
                      <SelectContent>
                        {allNodes.map((node) => (
                          <SelectItem key={node.codename} value={node.codename}>
                            <div className="flex flex-col text-left w-full">
                              <span className="font-mono text-sm">
                                {node.codename}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {getNodeDisplayName(node.parsedInfo)}
                              </span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Parsed Node Location */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Node Location</label>
                    <Select
                      value={selectedNode?.parsedInfo.node_location || ""}
                      disabled
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="No node selected" />
                      </SelectTrigger>
                      <SelectContent>
                        {selectedNode && (
                          <SelectItem
                            value={selectedNode.parsedInfo.node_location}
                          >
                            {formatNodeLocation(
                              selectedNode.parsedInfo.node_location,
                            )}
                          </SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Parsed Node Type */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Node Type</label>
                    <Select
                      value={selectedNode?.parsedInfo.node_type || ""}
                      disabled
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="No node selected" />
                      </SelectTrigger>
                      <SelectContent>
                        {selectedNode && (
                          <SelectItem value={selectedNode.parsedInfo.node_type}>
                            {formatNodeType(selectedNode.parsedInfo.node_type)}
                          </SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Parsed Node ID */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Node ID</label>
                    <Select
                      value={selectedNode?.parsedInfo.node_id || ""}
                      disabled
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="No node selected" />
                      </SelectTrigger>
                      <SelectContent>
                        {selectedNode && (
                          <SelectItem value={selectedNode.parsedInfo.node_id}>
                            {selectedNode.parsedInfo.node_id.toUpperCase()}
                          </SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Node Information Summary */}
                <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                  <span>
                    {connectedNodes.size === 0
                      ? "No nodes detected yet"
                      : `${connectedNodes.size} total node${connectedNodes.size > 1 ? "s" : ""} available`}
                  </span>
                  {selectedNode && (
                    <>
                      <span>•</span>
                      <span>
                        Status:{" "}
                        {selectedNode.isReceivingData ? "Live" : "No Data"}
                      </span>
                      {availableSensorTypes.length > 0 && (
                        <>
                          <span>•</span>
                          <span>
                            Sensors: {availableSensorTypes.join(", ")}
                          </span>
                        </>
                      )}
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            {selectedNode ? (
              <>
                {/* Current Values Card */}
                <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                  <CardHeader>
                    <CardTitle className="text-lg">
                      Current Sensor Values
                    </CardTitle>
                    <CardDescription>
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                          <div
                            className={`h-2 w-2 rounded-full ${
                              selectedNode.isReceivingData
                                ? "bg-green-500"
                                : "bg-gray-400"
                            }`}
                          />
                          <span className="text-xs">
                            {selectedNode.isReceivingData
                              ? "Live Data"
                              : "No Data"}
                          </span>
                        </div>
                        <p className="text-sm font-medium">
                          Current node:{" "}
                          <span className="font-semibold">
                            {getNodeDisplayName(selectedNode.parsedInfo)}
                          </span>
                        </p>
                      </div>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-4">
                      {/* Display current sensor values */}
                      {Object.entries(selectedNode.currentValues).map(
                        ([key, value]) => {
                          if (value === undefined || value === null)
                            return null;

                          const getSensorConfig = (sensorKey: string) => {
                            switch (sensorKey) {
                              case "temperature":
                                return {
                                  icon: Thermometer,
                                  unit: "°C",
                                  iconColor: "text-green-600",
                                  bgColor: "bg-muted",
                                  textColor: "text-foreground",
                                  valueColor: "text-foreground",
                                };
                              case "humidity":
                                return {
                                  icon: Droplets,
                                  unit: "%",
                                  iconColor: "text-orange-500",
                                  bgColor: "bg-muted",
                                  textColor: "text-foreground",
                                  valueColor: "text-foreground",
                                };
                              case "tds":
                                return {
                                  icon: Beaker,
                                  unit: "ppm",
                                  iconColor: "text-blue-600",
                                  bgColor: "bg-muted",
                                  textColor: "text-foreground",
                                  valueColor: "text-foreground",
                                };
                              case "ds":
                                return {
                                  icon: Zap,
                                  unit: "μS/cm",
                                  iconColor: "text-purple-600",
                                  bgColor: "bg-muted",
                                  textColor: "text-foreground",
                                  valueColor: "text-foreground",
                                };
                              default:
                                return {
                                  icon: Thermometer,
                                  unit: "",
                                  iconColor: "text-gray-600",
                                  bgColor: "bg-muted",
                                  textColor: "text-foreground",
                                  valueColor: "text-foreground",
                                };
                            }
                          };

                          const sensorConfig = getSensorConfig(key);
                          const SensorIcon = sensorConfig.icon;

                          return (
                            <div
                              key={key}
                              className={`p-4 rounded-lg border ${sensorConfig.bgColor}`}
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                  <SensorIcon
                                    className={`h-5 w-5 ${sensorConfig.iconColor}`}
                                  />
                                  <span
                                    className={`text-sm font-medium capitalize ${sensorConfig.textColor}`}
                                  >
                                    {key}
                                  </span>
                                </div>
                              </div>
                              <div className="mt-2">
                                <span
                                  className={`text-2xl font-bold ${sensorConfig.valueColor}`}
                                >
                                  {value}
                                  {sensorConfig.unit}
                                </span>
                              </div>
                            </div>
                          );
                        },
                      )}
                    </div>

                    <div className="mt-4 pt-4 border-t text-sm text-muted-foreground">
                      <div className="flex flex-wrap items-center gap-4">
                        <span>
                          Last Update:{" "}
                          {formatLastUpdate(selectedNode.lastUpdate)}
                        </span>
                        <span>•</span>
                        <span>
                          Data Points: {selectedNode.sensorHistory.length}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Charts Section */}
                <div className="space-y-6">
                  {/* Individual Sensor Charts */}
                  {availableSensorTypes.length > 0 && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                      {availableSensorTypes.map((sensorType) => {
                        const getSensorConfig = (sensorKey: string) => {
                          switch (sensorKey) {
                            case "temperature":
                              return {
                                icon: Thermometer,
                                label: "Temperature",
                                unit: "°C",
                                color: "text-green-600",
                              };
                            case "humidity":
                              return {
                                icon: Droplets,
                                label: "Humidity",
                                unit: "%",
                                color: "text-orange-500",
                              };
                            case "tds":
                              return {
                                icon: Beaker,
                                label: "TDS",
                                unit: "ppm",
                                color: "text-blue-600",
                              };
                            case "ds":
                              return {
                                icon: Zap,
                                label: "DS/EC",
                                unit: "μS/cm",
                                color: "text-purple-600",
                              };
                            default:
                              return {
                                icon: Thermometer,
                                label: sensorKey,
                                unit: "",
                                color: "text-gray-600",
                              };
                          }
                        };

                        const sensorConfig = getSensorConfig(sensorType);
                        const SensorIcon = sensorConfig.icon;

                        return (
                          <Card
                            key={sensorType}
                            className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg"
                          >
                            <CardHeader>
                              <CardTitle className="flex items-center gap-2">
                                <SensorIcon
                                  className={`h-5 w-5 ${sensorConfig.color}`}
                                />
                                {sensorConfig.label} Over Time
                              </CardTitle>
                              <CardDescription>
                                Reading {sensorConfig.label.toLowerCase()} from:{" "}
                                <span className="font-medium">
                                  {getNodeDisplayName(selectedNode.parsedInfo)}
                                </span>
                              </CardDescription>
                            </CardHeader>
                            <CardContent>
                              <ChartContainer config={chartConfig}>
                                <LineChart
                                  data={getChartData()}
                                  margin={{
                                    top: 5,
                                    right: 30,
                                    left: 20,
                                    bottom: 5,
                                  }}
                                >
                                  <CartesianGrid
                                    strokeDasharray="3 3"
                                    className="stroke-muted"
                                  />
                                  <XAxis
                                    dataKey="time"
                                    className="text-xs"
                                    tick={{ fontSize: 12 }}
                                  />
                                  <YAxis
                                    domain={
                                      sensorType === "humidity"
                                        ? ["dataMin - 10", "dataMax + 10"]
                                        : ["dataMin - 5", "dataMax + 5"]
                                    }
                                    className="text-xs"
                                    tick={{ fontSize: 12 }}
                                  />
                                  <ChartTooltip
                                    content={<ChartTooltipContent />}
                                  />
                                  <Line
                                    type="monotone"
                                    dataKey={sensorType}
                                    stroke={
                                      chartConfig[
                                        sensorType as keyof typeof chartConfig
                                      ]?.color
                                    }
                                    strokeWidth={2}
                                    dot={{
                                      fill: chartConfig[
                                        sensorType as keyof typeof chartConfig
                                      ]?.color,
                                      strokeWidth: 2,
                                      r: 0,
                                    }}
                                    connectNulls={false}
                                  />
                                </LineChart>
                              </ChartContainer>
                            </CardContent>
                          </Card>
                        );
                      })}
                    </div>
                  )}

                  {/* Combined Chart for all sensors */}
                  {availableSensorTypes.length > 1 && (
                    <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                      <CardHeader>
                        <CardTitle>Combined Sensor Data</CardTitle>
                        <CardDescription>
                          All sensor readings from{" "}
                          {getNodeDisplayName(selectedNode.parsedInfo)} on the
                          same timeline
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <ChartContainer config={chartConfig}>
                          <LineChart
                            data={getChartData()}
                            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                          >
                            <CartesianGrid
                              strokeDasharray="3 3"
                              className="stroke-muted"
                            />
                            <XAxis
                              dataKey="time"
                              className="text-xs"
                              tick={{ fontSize: 12 }}
                            />
                            <YAxis
                              className="text-xs"
                              tick={{ fontSize: 12 }}
                            />
                            <ChartTooltip content={<ChartTooltipContent />} />
                            {availableSensorTypes.map((sensorType) => (
                              <Line
                                key={sensorType}
                                type="monotone"
                                dataKey={sensorType}
                                stroke={
                                  chartConfig[
                                    sensorType as keyof typeof chartConfig
                                  ]?.color
                                }
                                strokeWidth={2}
                                dot={{
                                  fill: chartConfig[
                                    sensorType as keyof typeof chartConfig
                                  ]?.color,
                                  strokeWidth: 2,
                                  r: 0,
                                }}
                                name={sensorType}
                              />
                            ))}
                          </LineChart>
                        </ChartContainer>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </>
            ) : (
              <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                <CardContent className="text-center py-12">
                  <div className="space-y-4">
                    <div className="mx-auto w-16 h-16 bg-muted rounded-full flex items-center justify-center">
                      <Wifi className="h-8 w-8 text-muted-foreground" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold">
                        {connectedNodes.size === 0
                          ? "Waiting for Sensor Data"
                          : "Select a Node"}
                      </h3>
                      <p className="text-muted-foreground">
                        {connectedNodes.size === 0
                          ? isMQTTConnected
                            ? "MQTT is connected. Waiting for nodes to send sensor data..."
                            : "Please check your MQTT connection and ensure nodes are publishing data."
                          : "Please select a node from the dropdown above to view its sensor data."}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </Main>
        <Footer />

        {/* Scroll to Top Button */}
        <ScrollToTop />
      </div>
    </div>
  );
}
