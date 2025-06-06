import { useState, useEffect, useCallback } from "react";
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
import { Input } from "@/components/ui/input";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  Eye,
  Trash2,
  Download,
  Send,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Edit3,
  Check,
  X,
} from "lucide-react";
import type { Node, ApiError } from "@/types";
import { NodeDetailDialog } from "@/components/dialogs/NodeDetailDialog";
import { DeleteVersionDialog } from "@/components/dialogs/DeleteVersionDialog";
import { EditDescriptionDialog } from "@/components/dialogs/EditDescriptionDialog";
import { MQTTPushConfirmationDialog } from "@/components/dialogs/MQTTPushConfirmationDialog";
import { nodeController } from "@/controllers";
import { createMQTTPayload, convertGoogleDriveUrl } from "@/utils/mqtt";
import { mqttManager } from "@/utils/mqttClient";
import { toast } from "@/utils/notifications";

interface FirmwareManagementTableProps {
  nodes: Node[];
  loading: boolean;
  pagination: {
    page: number;
    page_size: number;
    total_data: number;
    total_page: number;
  };
  filterOptions: {
    node_locations: string[];
    node_types: string[];
  };
  filters: {
    node_location: string;
    node_type: string;
  };
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  onFilterChange: (filters: {
    node_location: string;
    node_type: string;
  }) => void;
  onRefresh: () => void;
  refreshKey?: number;
}

export function FirmwareManagementTable({
  nodes,
  loading,
  pagination,
  filterOptions,
  filters,
  onPageChange,
  onPageSizeChange,
  onFilterChange,
  onRefresh,
  refreshKey = 0,
}: FirmwareManagementTableProps) {
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<{
    node: Node;
    firmwareVersion?: string;
    hasMultipleVersions: boolean;
  } | null>(null);

  const [editDescriptionTarget, setEditDescriptionTarget] = useState<{
    nodeCodename: string;
    currentDescription: string;
    selectedVersion: string;
    hasMultipleVersions: boolean;
  } | null>(null);

  const [mqttPushTarget, setMqttPushTarget] = useState<{
    node: Node;
    firmwareVersion: string;
    firmwareUrl: string;
  } | null>(null);

  const [firmwareVersions, setFirmwareVersions] = useState<
    Record<string, string[]>
  >({});
  const [selectedVersions, setSelectedVersions] = useState<
    Record<string, string>
  >({});
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>(
    {},
  );

  const [editingDescription, setEditingDescription] = useState<
    Record<string, boolean>
  >({});
  const [editDescriptionValue, setEditDescriptionValue] = useState<
    Record<string, string>
  >({});

  // Fetch firmware versions for a node
  const fetchFirmwareVersions = useCallback(
    async (nodeCodename: string) => {
      try {
        const response = await nodeController.getFirmwareVersions(nodeCodename);
        setFirmwareVersions((prev) => ({
          ...prev,
          [nodeCodename]: response.data,
        }));

        const currentNode = nodes.find((n) => n.node_codename === nodeCodename);
        if (currentNode && !selectedVersions[nodeCodename]) {
          setSelectedVersions((prev) => ({
            ...prev,
            [nodeCodename]: currentNode.firmware_version,
          }));
        }
      } catch (error: unknown) {
        console.error(
          `Failed to fetch firmware versions for ${nodeCodename}:`,
          error,
        );
      }
    },
    [nodes, selectedVersions],
  );

  useEffect(() => {
    const fetchAllVersions = async () => {
      for (const node of nodes) {
        if (!firmwareVersions[node.node_codename]) {
          await fetchFirmwareVersions(node.node_codename);
        }
      }
    };

    if (nodes.length > 0) {
      fetchAllVersions();
    }
  }, [nodes, firmwareVersions, fetchFirmwareVersions]);

  useEffect(() => {
    if (refreshKey > 0) {
      setFirmwareVersions({});
      setSelectedVersions({});
    }
  }, [refreshKey]);

  const handleVersionSelect = (nodeCodename: string, version: string) => {
    setSelectedVersions((prev) => ({
      ...prev,
      [nodeCodename]: version,
    }));
  };

  const handleViewDetail = async (node: Node) => {
    const selectedVersion =
      selectedVersions[node.node_codename] || node.firmware_version;
    try {
      const response = await nodeController.getNodeDetail(
        node.node_codename,
        selectedVersion,
      );
      setSelectedNode(response.data);
    } catch (error: unknown) {
      toast.error("Error", {
        description:
          (error as ApiError).message || "Failed to fetch node details",
      });
    }
  };

  const handleEditDescription = (
    nodeCodename: string,
    currentDescription: string,
  ) => {
    setEditingDescription((prev) => ({ ...prev, [nodeCodename]: true }));
    setEditDescriptionValue((prev) => ({
      ...prev,
      [nodeCodename]: currentDescription || "",
    }));
  };

  const handleSaveDescription = async (nodeCodename: string) => {
    const selectedVersion =
      selectedVersions[nodeCodename] ||
      nodes.find((n) => n.node_codename === nodeCodename)?.firmware_version ||
      "";
    const description = editDescriptionValue[nodeCodename] || "";

    const nodeVersions = firmwareVersions[nodeCodename];
    const hasMultipleVersions = nodeVersions && nodeVersions.length > 1;

    if (hasMultipleVersions) {
      setEditDescriptionTarget({
        nodeCodename,
        currentDescription: description,
        selectedVersion,
        hasMultipleVersions: true,
      });
    } else {
      setEditDescriptionTarget({
        nodeCodename,
        currentDescription: description,
        selectedVersion,
        hasMultipleVersions: false,
      });
    }

    setEditingDescription((prev) => ({ ...prev, [nodeCodename]: false }));
  };

  const handleDescriptionUpdateConfirm = async (updateAllVersions: boolean) => {
    if (!editDescriptionTarget) return;

    const {
      nodeCodename,
      currentDescription,
      selectedVersion,
      hasMultipleVersions,
    } = editDescriptionTarget;
    const actionKey = `edit_description_${nodeCodename}`;
    setActionLoading((prev) => ({ ...prev, [actionKey]: true }));

    try {
      const firmwareVersion =
        !hasMultipleVersions || updateAllVersions ? undefined : selectedVersion;

      await nodeController.editFirmware(
        nodeCodename,
        { description: currentDescription },
        firmwareVersion,
      );

      const message = !hasMultipleVersions
        ? "Node has been edited"
        : updateAllVersions
          ? "Node has been edited for all versions"
          : `Node has been edited for version ${selectedVersion}`;

      toast.success(message, {
        description: "Description updated successfully",
      });

      setEditDescriptionTarget(null);
      setFirmwareVersions({});
      setSelectedVersions({});
      onRefresh();
    } catch (error: unknown) {
      toast.error("Update Failed", {
        description:
          error instanceof Error
            ? error.message
            : "Failed to update description",
      });
    } finally {
      setActionLoading((prev) => ({ ...prev, [actionKey]: false }));
    }
  };

  const handleCancelEdit = (nodeCodename: string) => {
    setEditingDescription((prev) => ({ ...prev, [nodeCodename]: false }));
    setEditDescriptionValue((prev) => ({ ...prev, [nodeCodename]: "" }));
  };

  const handleDownload = async (node: Node) => {
    const actionKey = `download_${node.node_codename}`;
    setActionLoading((prev) => ({ ...prev, [actionKey]: true }));

    try {
      const selectedVersion =
        selectedVersions[node.node_codename] || node.firmware_version;
      const filename = `${node.node_codename}_v${selectedVersion}.bin`;

      await nodeController.downloadFirmware(
        node.node_codename,
        selectedVersion,
        filename,
      );

      toast.success("Firmware file has successfully downloaded", {
        description: `${filename} downloaded to your device`,
      });
    } catch (error: unknown) {
      toast.error("Download Failed", {
        description:
          error instanceof Error
            ? error.message
            : "Failed to download firmware",
      });
    } finally {
      setActionLoading((prev) => ({ ...prev, [actionKey]: false }));
    }
  };

  const handleMQTTPushClick = async (node: Node) => {
    if (!mqttManager.getConnectionStatus()) {
      toast.error("MQTT Not Connected", {
        description: "Please check your MQTT broker connection",
      });
      return;
    }

    try {
      const selectedVersion =
        selectedVersions[node.node_codename] || node.firmware_version;

      const nodeDetail = await nodeController.getNodeDetail(
        node.node_codename,
        selectedVersion,
      );

      const firmwareUrl = convertGoogleDriveUrl(nodeDetail.data.firmware_url);

      setMqttPushTarget({
        node,
        firmwareVersion: selectedVersion,
        firmwareUrl,
      });
    } catch (error: unknown) {
      toast.error("Error", {
        description:
          (error as ApiError).message || "Failed to get firmware details",
      });
    }
  };

  const handleMQTTPublishConfirm = async () => {
    if (!mqttPushTarget) return;

    const { node, firmwareVersion, firmwareUrl } = mqttPushTarget;
    const actionKey = `mqtt_${node.node_codename}`;
    setActionLoading((prev) => ({ ...prev, [actionKey]: true }));

    try {
      const payload = createMQTTPayload(
        node.node_codename,
        firmwareUrl,
        firmwareVersion,
      );

      await mqttManager.publishFirmwareUpdate(payload);

      toast.success("Firmware Update on Progress", {
        description: `Firmware update command sent to ${node.node_codename}`,
      });

      console.log("MQTT Payload Published:", JSON.stringify(payload, null, 2));

      setMqttPushTarget(null);
    } catch (error: unknown) {
      toast.error("Publish Failed", {
        description:
          error instanceof Error
            ? error.message
            : "Failed to publish MQTT message",
      });
    } finally {
      setActionLoading((prev) => ({ ...prev, [actionKey]: false }));
    }
  };

  const handleDeleteClick = async (node: Node) => {
    const selectedVersion =
      selectedVersions[node.node_codename] || node.firmware_version;

    if (!firmwareVersions[node.node_codename]) {
      await fetchFirmwareVersions(node.node_codename);
    }

    const nodeVersions = firmwareVersions[node.node_codename];
    const hasMultipleVersions = nodeVersions && nodeVersions.length > 1;

    if (hasMultipleVersions) {
      setDeleteTarget({
        node,
        firmwareVersion: selectedVersion,
        hasMultipleVersions: true,
      });
    } else {
      setDeleteTarget({
        node,
        hasMultipleVersions: false,
      });
    }
  };

  const handleDeleteConfirm = async (deleteAllVersions?: boolean) => {
    if (!deleteTarget) return;

    try {
      const { node, firmwareVersion, hasMultipleVersions } = deleteTarget;

      if (!hasMultipleVersions || deleteAllVersions) {
        await nodeController.deleteNode(node.node_codename);
      } else {
        await nodeController.deleteNode(node.node_codename, firmwareVersion);
      }

      const message =
        !hasMultipleVersions || deleteAllVersions
          ? "Node has been deleted"
          : "Version has been deleted";

      const description =
        !hasMultipleVersions || deleteAllVersions
          ? `Node ${node.node_codename} deleted successfully`
          : `Firmware version ${firmwareVersion} deleted successfully`;

      toast.success(message, { description });

      setDeleteTarget(null);
      setFirmwareVersions({});
      setSelectedVersions({});
      onRefresh();
    } catch (error: unknown) {
      toast.error("Delete Failed", {
        description:
          error instanceof Error ? error.message : "Failed to delete",
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // ... rest of your JSX remains the same
  return (
    <div className="space-y-4">
      {/* All your existing JSX code stays the same */}
      {/* Filter Options */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Filter Options</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
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

      {/* Firmware Version Control Table */}
      <Card>
        <CardHeader>
          <CardTitle>Firmware Version Control</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-center">Node Location</TableHead>
                  <TableHead className="text-center">Node Type</TableHead>
                  <TableHead className="text-center">Node ID</TableHead>
                  <TableHead className="text-center">Description</TableHead>
                  <TableHead className="text-center">
                    Firmware Version
                  </TableHead>
                  <TableHead className="text-center">Last Updated</TableHead>
                  <TableHead className="text-center">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8">
                      <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2" />
                      Loading nodes...
                    </TableCell>
                  </TableRow>
                ) : nodes.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={7}
                      className="text-center py-8 text-muted-foreground"
                    >
                      No nodes found
                    </TableCell>
                  </TableRow>
                ) : (
                  nodes.map((node) => (
                    <TableRow key={node._id}>
                      <TableCell className="text-center">
                        {node.node_location}
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="secondary">{node.node_type}</Badge>
                      </TableCell>
                      <TableCell className="font-mono text-center">
                        {node.node_id}
                      </TableCell>
                      <TableCell className="max-w-xs">
                        {editingDescription[node.node_codename] ? (
                          <div className="flex items-center gap-2">
                            <Input
                              value={
                                editDescriptionValue[node.node_codename] || ""
                              }
                              onChange={(e) =>
                                setEditDescriptionValue((prev) => ({
                                  ...prev,
                                  [node.node_codename]: e.target.value,
                                }))
                              }
                              placeholder="Enter description..."
                              className="h-8 text-sm"
                            />
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() =>
                                    handleSaveDescription(node.node_codename)
                                  }
                                  disabled={
                                    actionLoading[
                                      `edit_description_${node.node_codename}`
                                    ]
                                  }
                                  className="h-8 w-8 p-0"
                                >
                                  <Check className="h-4 w-4 text-green-600" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Save Description</p>
                              </TooltipContent>
                            </Tooltip>

                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() =>
                                    handleCancelEdit(node.node_codename)
                                  }
                                  className="h-8 w-8 p-0"
                                >
                                  <X className="h-4 w-4 text-red-600" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Cancel Edit</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2">
                            <span className="text-sm truncate">
                              {node.description || "No description"}
                            </span>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() =>
                                    handleEditDescription(
                                      node.node_codename,
                                      node.description || "",
                                    )
                                  }
                                  className="h-6 w-6 p-0 opacity-60 hover:opacity-100"
                                >
                                  <Edit3 className="h-3 w-3" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p>Edit Description</p>
                              </TooltipContent>
                            </Tooltip>
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        <Select
                          value={
                            selectedVersions[node.node_codename] ||
                            node.firmware_version
                          }
                          onValueChange={(value) =>
                            handleVersionSelect(node.node_codename, value)
                          }
                        >
                          <SelectTrigger className="w-32 mx-auto">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {(
                              firmwareVersions[node.node_codename] || [
                                node.firmware_version,
                              ]
                            ).map((version) => (
                              <SelectItem key={version} value={version}>
                                {version}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground text-center">
                        {formatDate(node.latest_updated)}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1 justify-center">
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleViewDetail(node)}
                                className="h-8 w-8 p-0"
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>View Node Details</p>
                            </TooltipContent>
                          </Tooltip>

                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleDownload(node)}
                                disabled={
                                  actionLoading[
                                    `download_${node.node_codename}`
                                  ]
                                }
                                className="h-8 w-8 p-0"
                              >
                                <Download className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Download Firmware File</p>
                            </TooltipContent>
                          </Tooltip>

                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleMQTTPushClick(node)}
                                disabled={
                                  actionLoading[`mqtt_${node.node_codename}`] ||
                                  !mqttManager.getConnectionStatus()
                                }
                                className="h-8 w-8 p-0"
                              >
                                <Send
                                  className={`h-4 w-4 ${!mqttManager.getConnectionStatus() ? "text-gray-400" : ""}`}
                                />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>
                                {!mqttManager.getConnectionStatus()
                                  ? "MQTT Not Connected"
                                  : "Send Firmware Update"}
                              </p>
                            </TooltipContent>
                          </Tooltip>

                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleDeleteClick(node)}
                                className="h-8 w-8 p-0"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                              <p>Delete Node/Version</p>
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
          {!loading && nodes.length > 0 && (
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
      <NodeDetailDialog
        node={selectedNode}
        open={!!selectedNode}
        onOpenChange={() => setSelectedNode(null)}
      />

      <DeleteVersionDialog
        open={!!deleteTarget}
        onOpenChange={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        nodeCodename={deleteTarget?.node.node_codename || ""}
        selectedVersion={deleteTarget?.firmwareVersion || ""}
        hasMultipleVersions={deleteTarget?.hasMultipleVersions || false}
      />

      <EditDescriptionDialog
        open={!!editDescriptionTarget}
        onOpenChange={() => setEditDescriptionTarget(null)}
        onConfirm={handleDescriptionUpdateConfirm}
        nodeCodename={editDescriptionTarget?.nodeCodename || ""}
        currentDescription={editDescriptionTarget?.currentDescription || ""}
        selectedVersion={editDescriptionTarget?.selectedVersion || ""}
        hasMultipleVersions={
          editDescriptionTarget?.hasMultipleVersions || false
        }
      />

      <MQTTPushConfirmationDialog
        open={!!mqttPushTarget}
        onOpenChange={() => setMqttPushTarget(null)}
        onConfirm={handleMQTTPublishConfirm}
        nodeCodename={mqttPushTarget?.node.node_codename || ""}
        firmwareVersion={mqttPushTarget?.firmwareVersion || ""}
        firmwareUrl={mqttPushTarget?.firmwareUrl || ""}
        isConnected={mqttManager.getConnectionStatus()}
      />
    </div>
  );
}
