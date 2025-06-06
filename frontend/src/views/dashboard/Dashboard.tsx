import { useAuthState } from "react-firebase-hooks/auth";
import { useState, useEffect, useCallback } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Upload, RefreshCw } from "lucide-react";
import { auth } from "@/utils/firebase";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import Main from "@/components/layout/Main";
import { ScrollToTop } from "@/components/ui/scroll-to-top";
import { usePageTitle } from "@/hooks/usePageTitle";
import { useMQTTConnection } from "@/hooks/useMQTTConnection";
import { FirmwareManagementTable } from "@/components/tables/FirmwareManagementTable";
import { AddNodeDialog } from "@/components/dialogs/AddNodeDialog";
import { AddFirmwareDialog } from "@/components/dialogs/AddFirmwareDialog";
import { nodeController, logController } from "@/controllers";
import { Alert, AlertDescription } from "@/components/ui/alert";
import Squares from "@/components/background/Squares";
import type { Node, NodesListParams, PaginatedApiResponse } from "@/types";

export default function Dashboard() {
  const [user] = useAuthState(auth);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [nodesLoading, setNodesLoading] = useState(true);
  const [nodesError, setNodesError] = useState<string>("");
  const [isAddNodeOpen, setIsAddNodeOpen] = useState(false);
  const [isAddFirmwareOpen, setIsAddFirmwareOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Simplified OTA statistics state
  const [otaStats, setOtaStats] = useState({
    total: 0,
    inProgress: 0,
    loading: true,
  });

  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 10,
    total_data: 0,
    total_page: 0,
  });
  const [filterOptions, setFilterOptions] = useState<{
    node_locations: string[];
    node_types: string[];
  }>({
    node_locations: [],
    node_types: [],
  });
  const [filters, setFilters] = useState({
    node_location: "",
    node_type: "",
  });

  const isMQTTConnected = useMQTTConnection();
  usePageTitle("Dashboard");

  // Simplified OTA statistics fetching
  const fetchOtaStats = useCallback(async () => {
    try {
      setOtaStats((prev) => ({ ...prev, loading: true }));

      // Fetch total logs and in-progress logs only
      const [allLogsResponse, inProgressResponse] = await Promise.all([
        logController.getAllLogs({ page: 1, page_size: 1 }),
        logController.getAllLogs({
          page: 1,
          page_size: 1,
          flash_status: "in progress",
        }),
      ]);

      setOtaStats({
        total: allLogsResponse.total_data,
        inProgress: inProgressResponse.total_data,
        loading: false,
      });
    } catch (error) {
      console.error("Failed to fetch OTA statistics:", error);
      setOtaStats((prev) => ({ ...prev, loading: false }));
    }
  }, []);

  const fetchNodes = useCallback(
    async (params?: Partial<NodesListParams>) => {
      try {
        setNodesLoading(true);
        setNodesError("");

        const requestParams: NodesListParams = {
          page: pagination.page,
          page_size: pagination.page_size,
        };

        if (filters.node_location && filters.node_location !== "") {
          requestParams.node_location = filters.node_location;
        }

        if (filters.node_type && filters.node_type !== "") {
          requestParams.node_type = filters.node_type;
        }

        const finalParams = { ...requestParams, ...params };
        const response: PaginatedApiResponse<Node> =
          await nodeController.getAllNodes(finalParams);

        setNodes(response.data);
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
        setNodesError(errorMessage);
      } finally {
        setNodesLoading(false);
      }
    },
    [pagination.page, pagination.page_size, filters],
  );

  useEffect(() => {
    fetchNodes();
    fetchOtaStats();
  }, [fetchNodes, fetchOtaStats]);

  const handleRefresh = useCallback(async () => {
    setNodesLoading(true);
    try {
      setRefreshKey((prev) => prev + 1);
      await Promise.all([fetchNodes(), fetchOtaStats()]);
    } finally {
      setNodesLoading(false);
    }
  }, [fetchNodes, fetchOtaStats]);

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

  const handleAddNodeSuccess = () => {
    setIsAddNodeOpen(false);
    handleRefresh();
  };

  const handleAddFirmwareSuccess = () => {
    setIsAddFirmwareOpen(false);
    handleRefresh();
  };

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
            {/* Welcome Section */}
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold">
                LokaSync Dashboard
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Welcome back, {user?.displayName || user?.email}!
              </p>
            </div>

            {/* Overview Section */}
            <div className="space-y-4">
              <h2 className="text-xl font-bold">Overview</h2>

              {/* Stats Cards - Enhanced with backdrop blur */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
                {/* Nodes Card */}
                <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">Nodes</CardTitle>
                    <CardDescription className="text-sm">
                      Manage your IoT devices
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {pagination.total_data}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Connected devices
                    </p>
                  </CardContent>
                </Card>

                {/* OTA Updates Card */}
                <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">OTA Updates</CardTitle>
                    <CardDescription className="text-sm">
                      Total firmware updates
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-2xl font-bold">
                      {otaStats.loading ? "..." : otaStats.total}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Total update logs
                    </p>
                  </CardContent>
                </Card>

                {/* In Progress Updates Card */}
                <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">Pending Updates</CardTitle>
                    <CardDescription className="text-sm">
                      Active firmware updates
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2">
                      <p className="text-2xl font-bold">
                        {otaStats.loading ? "..." : otaStats.inProgress}
                      </p>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Currently updating
                    </p>
                  </CardContent>
                </Card>

                {/* MQTT Monitoring Card */}
                <Card className="backdrop-blur-sm bg-card/95 border-border/50 shadow-lg">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">Monitoring</CardTitle>
                    <CardDescription className="text-sm">
                      Real-time data sensor
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center gap-2">
                      <div
                        className={`h-3 w-3 rounded-full ${isMQTTConnected ? "bg-green-500" : "bg-red-500"}`}
                      />
                      <p className="text-2xl font-bold">
                        {isMQTTConnected ? "Connected" : "Disconnected"}
                      </p>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      MQTT broker status
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Firmware Management Section */}
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
                <div>
                  <h2 className="text-xl font-bold">Firmware Management</h2>
                  <p className="text-sm text-muted-foreground">
                    Manage your IoT nodes and firmware versions
                  </p>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3">
                <Button
                  onClick={() => setIsAddNodeOpen(true)}
                  className="w-full sm:w-auto"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add New Node
                </Button>

                <Button
                  onClick={() => setIsAddFirmwareOpen(true)}
                  // variant="outline"
                  className="w-full sm:w-auto"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Add Firmware Version
                </Button>

                <Button
                  onClick={handleRefresh}
                  // variant="outline"
                  size="sm"
                  disabled={nodesLoading || otaStats.loading}
                  className="w-full sm:w-auto"
                >
                  <RefreshCw
                    className={`h-4 w-4 mr-2 ${nodesLoading || otaStats.loading ? "animate-spin" : ""}`}
                  />
                  Refresh
                </Button>
              </div>

              {nodesError && (
                <Alert variant="destructive">
                  <AlertDescription>{nodesError}</AlertDescription>
                </Alert>
              )}

              <FirmwareManagementTable
                key={refreshKey}
                refreshKey={refreshKey}
                nodes={nodes}
                loading={nodesLoading}
                pagination={pagination}
                filterOptions={filterOptions}
                filters={filters}
                onPageChange={handlePageChange}
                onPageSizeChange={handlePageSizeChange}
                onFilterChange={handleFilterChange}
                onRefresh={handleRefresh}
              />
            </div>
          </div>
        </Main>

        <Footer />

        {/* Scroll to Top Button */}
        <ScrollToTop />

        <AddNodeDialog
          open={isAddNodeOpen}
          onOpenChange={setIsAddNodeOpen}
          onSuccess={handleAddNodeSuccess}
        />

        <AddFirmwareDialog
          open={isAddFirmwareOpen}
          onOpenChange={setIsAddFirmwareOpen}
          onSuccess={handleAddFirmwareSuccess}
          existingNodes={nodes}
        />
      </div>
    </div>
  );
}
