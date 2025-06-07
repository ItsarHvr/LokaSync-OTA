import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import Main from "@/components/layout/Main";
import { ScrollToTop } from "@/components/ui/scroll-to-top";
import { usePageTitle } from "@/hooks/usePageTitle";
import { useMQTTConnection } from "@/hooks/useMQTTConnection";
import { LogManagementTable } from "@/components/tables/LogManagementTable";
import { logController } from "@/controllers";
import { mqttManager, type LogMQTTMessage } from "@/utils/mqttClient";
import { Alert, AlertDescription } from "@/components/ui/alert";
import Squares from "@/components/background/Squares";
import type { FirmwareLog, LogsListParams, LogFilterOptions } from "@/types";
import { toast } from "@/utils/notifications";

export default function Log() {
  const [logs, setLogs] = useState<FirmwareLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 10,
    total_data: 0,
    total_page: 0,
  });
  const [filterOptions, setFilterOptions] = useState<LogFilterOptions>({
    node_locations: [],
    node_types: [],
    flash_statuses: [],
  });
  const [filters, setFilters] = useState({
    node_location: "",
    node_type: "",
    flash_status: "",
  });

  const isMQTTConnected = useMQTTConnection();

  usePageTitle("Log Updates");

  // Handle real-time log messages from MQTT
  const handleLogMessage = useCallback(
    (message: LogMQTTMessage) => {
      console.log("Received real-time log message:", message);

      // Convert MQTT message to FirmwareLog format
      const newLog: FirmwareLog = {
        _id: `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, // Temporary ID until refresh
        created_at: new Date().toISOString(),
        session_id: message.session_id,
        node_mac: message.node_mac,
        node_location: "", // Will be filled on next refresh
        node_type: "", // Will be filled on next refresh
        node_id: "", // Will be filled on next refresh
        node_codename: message.node_codename,
        firmware_version: message.firmware_version,
        download_started_at: message.download_started_at,
        firmware_size_kb: message.firmware_size_kb,
        bytes_written: message.bytes_written,
        download_duration_sec: message.download_duration_sec,
        download_speed_kbps: message.download_speed_kbps,
        download_completed_at: message.download_completed_at,
        flash_completed_at: "", // Will be updated later
        flash_status: message.flash_status,
      };

      // Check if this log already exists (by session_id or node_codename + firmware_version + timestamp)
      setLogs((prevLogs) => {
        const existingLogIndex = prevLogs.findIndex(
          (log) =>
            log.session_id === message.session_id ||
            (log.node_codename === message.node_codename &&
              log.firmware_version === message.firmware_version &&
              new Date(log.download_started_at).getTime() ===
                new Date(message.download_started_at).getTime()),
        );

        if (existingLogIndex >= 0) {
          // Update existing log
          const updatedLogs = [...prevLogs];
          updatedLogs[existingLogIndex] = {
            ...updatedLogs[existingLogIndex],
            ...newLog,
            _id: updatedLogs[existingLogIndex]._id, // Keep original ID
          };
          return updatedLogs;
        } else {
          // Add new log at the beginning
          return [newLog, ...prevLogs];
        }
      });

      // Update pagination total count
      setPagination((prev) => ({
        ...prev,
        total_data:
          prev.total_data +
          ((prevLogs) => {
            const exists = prevLogs.some(
              (log) =>
                log.session_id === message.session_id ||
                (log.node_codename === message.node_codename &&
                  log.firmware_version === message.firmware_version &&
                  new Date(log.download_started_at).getTime() ===
                    new Date(message.download_started_at).getTime()),
            );
            return exists ? 0 : 1;
          })(logs),
      }));

      // Show toast notification
      toast.success("New Log Update", {
        description: `${message.node_codename}: ${message.flash_status}`,
      });
    },
    [logs],
  );

  // Subscribe to MQTT log messages
  useEffect(() => {
    const unsubscribe = mqttManager.onLogMessage(handleLogMessage);
    return unsubscribe;
  }, [handleLogMessage]);

  // Use useCallback to memoize fetchLogs function
  const fetchLogs = useCallback(
    async (params?: Partial<LogsListParams>) => {
      try {
        setLoading(true);
        setError("");

        // Build clean params object - only include non-empty values
        const requestParams: LogsListParams = {
          page: pagination.page,
          page_size: pagination.page_size,
        };

        // Only add filter params if they have values
        if (filters.node_location && filters.node_location !== "") {
          requestParams.node_location = filters.node_location;
        }

        if (filters.node_type && filters.node_type !== "") {
          requestParams.node_type = filters.node_type;
        }

        if (filters.flash_status && filters.flash_status !== "") {
          requestParams.flash_status = filters.flash_status;
        }

        // Merge with any additional params
        const finalParams = { ...requestParams, ...params };

        const response = await logController.getAllLogs(finalParams);

        setLogs(response.data);
        setPagination({
          page: response.page,
          page_size: response.page_size,
          total_data: response.total_data,
          total_page: response.total_page,
        });
        setFilterOptions(response.filter_options);
      } catch (error: unknown) {
        const errorMessage =
          error instanceof Error
            ? error.message
            : "An unexpected error occurred";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    },
    [pagination.page, pagination.page_size, filters],
  );

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const handleRefresh = () => {
    fetchLogs();
  };

  const handlePageChange = (newPage: number) => {
    setPagination((prev) => ({ ...prev, page: newPage }));
  };

  const handlePageSizeChange = (newPageSize: number) => {
    setPagination((prev) => ({ ...prev, page_size: newPageSize, page: 1 }));
  };

  const handleFilterChange = (newFilters: typeof filters) => {
    setFilters(newFilters);
    setPagination((prev) => ({ ...prev, page: 1 }));
  };

  return (
    <div className="min-h-screen flex flex-col bg-background relative">
      {/* Squares Background Animation */}
      <div className="absolute inset-0 z-0">
        <Squares
          speed={0.5}
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
                <h1 className="text-2xl sm:text-3xl font-bold">Log Updates</h1>
                <p className="text-sm text-muted-foreground mt-1">
                  View and manage firmware update logs in real-time
                </p>
              </div>

              <div className="flex gap-2">
                <Button
                  onClick={handleRefresh}
                  // variant="outline"
                  size="sm"
                  disabled={loading}
                >
                  <RefreshCw
                    className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`}
                  />
                  Refresh
                </Button>
              </div>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Log Management Table */}
            <LogManagementTable
              logs={logs}
              loading={loading}
              pagination={pagination}
              filterOptions={filterOptions}
              filters={filters}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
              onFilterChange={handleFilterChange}
              onRefresh={fetchLogs}
              mqttConnected={isMQTTConnected}
            />
          </div>
        </Main>
        <Footer />

        {/* Scroll to Top Button */}
        <ScrollToTop />
      </div>
    </div>
  );
}
