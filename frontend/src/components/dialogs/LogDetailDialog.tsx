import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import type { FirmwareLog } from "@/types";

interface LogDetailDialogProps {
  log: FirmwareLog | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function LogDetailDialog({
  log,
  open,
  onOpenChange,
}: LogDetailDialogProps) {
  if (!log) return null;

  const formatDate = (dateString: string) => {
    if (!dateString) return "N/A";
    try {
      return new Date(dateString).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return "Invalid Date";
    }
  };

  const formatBytes = (bytes: number) => {
    if (!bytes || isNaN(bytes)) return "N/A";
    return `${(bytes / 1024).toFixed(1)} KB`;
  };

  const formatNumber = (
    value: number,
    decimals: number = 1,
    unit: string = "",
  ) => {
    if (value === null || value === undefined || isNaN(value)) return "N/A";
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Firmware Update Log Details</DialogTitle>
          <DialogDescription>
            Detailed information for firmware update session
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Basic Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Session ID
                </label>
                <p className="font-mono text-sm break-all">
                  {log.session_id || "N/A"}
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Created At
                </label>
                <p className="text-sm">{formatDate(log.created_at)}</p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Node Codename
                </label>
                <p className="font-mono text-sm">
                  {log.node_codename || "N/A"}
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Node MAC
                </label>
                <p className="font-mono text-sm break-all">
                  {log.node_mac || "N/A"}
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Node Location
                </label>
                <p className="text-sm">{log.node_location || "N/A"}</p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Node Type
                </label>
                <p className="text-sm">{log.node_type || "N/A"}</p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Node ID
                </label>
                <p className="font-mono text-sm break-all">
                  {log.node_id || "N/A"}
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Firmware Version
                </label>
                <Badge variant="outline" className="text-xs">
                  {log.firmware_version || "N/A"}
                </Badge>
              </div>
            </div>
          </div>

          <Separator />

          {/* Download Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Download Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Firmware Size
                </label>
                <p className="text-sm font-mono">
                  {formatNumber(log.firmware_size_kb, 1, " KB")}
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Bytes Written
                </label>
                <p className="text-sm font-mono">
                  {formatBytes(log.bytes_written)}
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Download Duration
                </label>
                <p className="text-sm font-mono">
                  {formatNumber(log.download_duration_sec, 2, "s")}
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Download Speed
                </label>
                <p className="text-sm font-mono">
                  {formatNumber(log.download_speed_kbps, 2, " Kbps")}
                </p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Download Started At
                </label>
                <p className="text-sm">{formatDate(log.download_started_at)}</p>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Download Completed At
                </label>
                <p className="text-sm">
                  {formatDate(log.download_completed_at)}
                </p>
              </div>
            </div>
          </div>

          <Separator />

          {/* Flash Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Flash Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Flash Status
                </label>
                <div>
                  <Badge
                    variant={getStatusBadgeVariant(log.flash_status)}
                    className="capitalize"
                  >
                    {log.flash_status || "unknown"}
                  </Badge>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Flash Completed At
                </label>
                <p className="text-sm">{formatDate(log.flash_completed_at)}</p>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
