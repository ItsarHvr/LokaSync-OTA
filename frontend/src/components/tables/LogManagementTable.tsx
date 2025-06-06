import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Eye,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Wifi,
  WifiOff,
  Download,
} from "lucide-react";
import type { FirmwareLog, ApiError, LogFilterOptions } from "@/types";
import { LogDetailDialog } from "@/components/dialogs/LogDetailDialog";
import { DeleteLogDialog } from "@/components/dialogs/DeleteLogDialog";
import { ExportLogDialog } from "@/components/dialogs/ExportLogDialog";
import { logController } from "@/controllers";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { toast } from "@/utils/notifications";

interface LogManagementTableProps {
  logs: FirmwareLog[];
  loading: boolean;
  pagination: {
    page: number;
    page_size: number;
    total_data: number;
    total_page: number;
  };
  filterOptions: LogFilterOptions;
  filters: {
    node_location: string;
    node_type: string;
    flash_status: string;
  };
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  onFilterChange: (filters: {
    node_location: string;
    node_type: string;
    flash_status: string;
  }) => void;
  onRefresh: () => void;
  mqttConnected: boolean;
}

// Skeleton row component
const SkeletonTableRow = () => (
  <TableRow>
    <TableCell className="text-center">
      <Skeleton className="h-4 w-20 mx-auto" />
    </TableCell>
    <TableCell className="text-center">
      <Skeleton className="h-4 w-24 mx-auto" />
    </TableCell>
    <TableCell className="text-center">
      <Skeleton className="h-6 w-16 mx-auto rounded-full" />
    </TableCell>
    <TableCell className="text-center">
      <Skeleton className="h-4 w-12 mx-auto" />
    </TableCell>
    <TableCell className="text-center">
      <Skeleton className="h-6 w-16 mx-auto rounded-full" />
    </TableCell>
    <TableCell className="text-center">
      <Skeleton className="h-8 w-16 mx-auto" />
    </TableCell>
  </TableRow>
);

export function LogManagementTable({
  logs,
  loading,
  pagination,
  filterOptions,
  filters,
  onPageChange,
  onPageSizeChange,
  onFilterChange,
  onRefresh,
  mqttConnected,
}: LogManagementTableProps) {
  const [selectedLog, setSelectedLog] = useState<FirmwareLog | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<FirmwareLog | null>(null);
  const [isExportOpen, setIsExportOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>(
    {},
  );

  // Handle view detail
  const handleViewDetail = async (log: FirmwareLog) => {
    const actionKey = `detail_${log.session_id}`;
    setActionLoading((prev) => ({ ...prev, [actionKey]: true }));

    try {
      const response = await logController.getLogDetail(log.session_id);
      setSelectedLog(response.data);
    } catch (error: unknown) {
      toast.error("Error", {
        description:
          (error as ApiError).message || "Failed to fetch log details",
      });
    } finally {
      setActionLoading((prev) => ({ ...prev, [actionKey]: false }));
    }
  };

  // Handle delete button click
  const handleDeleteClick = (log: FirmwareLog) => {
    setDeleteTarget(log);
  };

  // Handle delete confirmation
  const handleDeleteConfirm = async () => {
    if (!deleteTarget) return;

    const actionKey = `delete_${deleteTarget.session_id}`;
    setActionLoading((prev) => ({ ...prev, [actionKey]: true }));

    try {
      await logController.deleteLog(deleteTarget.session_id);

      // Show success notification
      toast.success("Log has been deleted", {
        description: `Log for ${deleteTarget.node_codename} deleted successfully`,
      });

      setDeleteTarget(null);
      onRefresh();
    } catch (error: unknown) {
      toast.error("Delete Failed", {
        description:
          error instanceof Error ? error.message : "Failed to delete log",
      });
    } finally {
      setActionLoading((prev) => ({ ...prev, [actionKey]: false }));
    }
  };

  const formatNumber = (
    value: number | null | undefined,
    decimals: number = 1,
    unit: string = "",
  ) => {
    if (value === null || value === undefined || isNaN(value)) {
      return <Skeleton className="h-4 w-12 inline-block" />;
    }
    return `${value.toFixed(decimals)}${unit}`;
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "success":
        return "default";
      case "failed":
        return "destructive";
      case "in progress":
        return "secondary";
      default:
        return "outline";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "text-green-400";
      case "failed":
        return "text-red-400";
      case "in progress":
        return "text-orange-400";
      default:
        return "text-gray-400";
    }
  };

  return (
    <div className="space-y-4">
      {/* Filter Options */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Filter Options</CardTitle>
            <div className="flex items-center gap-2 text-sm">
              {mqttConnected ? (
                <>
                  <Wifi className="h-4 w-4 text-green-500" />
                  <span className="text-green-500">MQTT Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-4 w-4 text-red-500" />
                  <span className="text-red-500">MQTT Disconnected</span>
                </>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div className="flex flex-col items-center">
              <label className="text-sm font-medium mb-2 block w-full text-center">
                Node Location
              </label>
              <Select
                value={filters.node_location || "all"}
                onValueChange={(value) =>
                  onFilterChange({
                    ...filters,
                    node_location: value === "all" ? "" : value,
                  })
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="All Locations" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Locations</SelectItem>
                  {filterOptions.node_locations.map((location) => (
                    <SelectItem key={location} value={location}>
                      {location}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col items-center">
              <label className="text-sm font-medium mb-2 block w-full text-center">
                Node Type
              </label>
              <Select
                value={filters.node_type || "all"}
                onValueChange={(value) =>
                  onFilterChange({
                    ...filters,
                    node_type: value === "all" ? "" : value,
                  })
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {filterOptions.node_types.map((type) => (
                    <SelectItem key={type} value={type}>
                      {type}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col items-center">
              <label className="text-sm font-medium mb-2 block w-full text-center">
                Flash Status
              </label>
              <Select
                value={filters.flash_status || "all"}
                onValueChange={(value) =>
                  onFilterChange({
                    ...filters,
                    flash_status: value === "all" ? "" : value,
                  })
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  {filterOptions.flash_statuses.map((status) => (
                    <SelectItem key={status} value={status}>
                      <span className={`capitalize ${getStatusColor(status)}`}>
                        {status}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex flex-col items-center">
              <label className="text-sm font-medium mb-2 block w-full text-center">
                Show Data
              </label>
              <Select
                value={pagination.page_size.toString()}
                onValueChange={(value) => onPageSizeChange(parseInt(value))}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="25">25</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Log Management Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Firmware Update Logs</CardTitle>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  onClick={() => setIsExportOpen(true)}
                  variant="outline"
                  size="sm"
                  disabled={loading || logs.length === 0}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Export Logs to CSV/PDF</p>
              </TooltipContent>
            </Tooltip>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-center">Node Codename</TableHead>
                  <TableHead className="text-center">Node MAC</TableHead>
                  <TableHead className="text-center">
                    Previous Version
                  </TableHead>
                  <TableHead className="text-center">Firmware Size</TableHead>
                  <TableHead className="text-center">Flash Status</TableHead>
                  <TableHead className="text-center">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  // Show skeleton rows when loading
                  Array.from({ length: pagination.page_size }).map(
                    (_, index) => <SkeletonTableRow key={index} />,
                  )
                ) : logs.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={6}
                      className="text-center py-8 text-muted-foreground"
                    >
                      No logs found
                    </TableCell>
                  </TableRow>
                ) : (
                  logs.map((log) => (
                    <TableRow key={log._id}>
                      <TableCell className="font-mono text-center text-sm">
                        {log.node_codename || "N/A"}
                      </TableCell>
                      <TableCell className="font-mono text-center text-sm">
                        {log.node_mac || "N/A"}
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="outline">
                          {log.firmware_version || "N/A"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        {formatNumber(log.firmware_size_kb, 1, " KB")}
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge
                          variant={getStatusBadgeVariant(log.flash_status)}
                          className="capitalize"
                        >
                          {log.flash_status || "unknown"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1 justify-center">
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleViewDetail(log)}
                                disabled={
                                  actionLoading[`detail_${log.session_id}`]
                                }
                                className="h-8 w-8 p-0"
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>View Log Details</p>
                            </TooltipContent>
                          </Tooltip>

                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleDeleteClick(log)}
                                disabled={
                                  actionLoading[`delete_${log.session_id}`]
                                }
                                className="h-8 w-8 p-0"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Delete Log Entry</p>
                            </TooltipContent>
                          </Tooltip>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          {!loading && logs.length > 0 && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                Showing {(pagination.page - 1) * pagination.page_size + 1} to{" "}
                {Math.min(
                  pagination.page * pagination.page_size,
                  pagination.total_data,
                )}{" "}
                of {pagination.total_data} entries
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onPageChange(pagination.page - 1)}
                  disabled={pagination.page <= 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <span className="text-sm">
                  Page {pagination.page} of {pagination.total_page}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onPageChange(pagination.page + 1)}
                  disabled={pagination.page >= pagination.total_page}
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialogs */}
      <LogDetailDialog
        log={selectedLog}
        open={!!selectedLog}
        onOpenChange={() => setSelectedLog(null)}
      />

      <DeleteLogDialog
        open={!!deleteTarget}
        onOpenChange={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        nodeCodename={deleteTarget?.node_codename || ""}
        sessionId={deleteTarget?.session_id || ""}
      />

      <ExportLogDialog
        open={isExportOpen}
        onOpenChange={setIsExportOpen}
        logs={logs}
        totalCount={pagination.total_data}
        filters={filters}
      />
    </div>
  );
}
