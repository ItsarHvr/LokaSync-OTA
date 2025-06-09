import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Download, Loader2 } from "lucide-react";
import type { FirmwareLog } from "@/types";
import { logController } from "@/controllers";
import { toast } from "@/utils/notifications";

interface ExportLogDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  logs: FirmwareLog[];
  totalCount: number;
  filters: {
    node_location: string;
    node_type: string;
    flash_status: string;
  };
}

export function ExportLogDialog({
  open,
  onOpenChange,
  logs,
  totalCount,
  filters,
}: ExportLogDialogProps) {
  const [filename, setFilename] = useState("");
  const [withDatetime, setWithDatetime] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [exportingType, setExportingType] = useState<"csv" | "pdf" | null>(
    null,
  );

  // Calculate summary from current logs
  const summary = {
    total: logs.length,
    successful: logs.filter((log) => log.flash_status === "success").length,
    failed: logs.filter((log) => log.flash_status === "failed").length,
    inProgress: logs.filter((log) => log.flash_status === "in progress").length,
    successRate:
      logs.length > 0
        ? (
            (logs.filter((log) => log.flash_status === "success").length /
              logs.length) *
            100
          ).toFixed(1)
        : "0",
  };

  // Generate preview filename for display
  const getPreviewFilename = (type: "csv" | "pdf") => {
    const baseFilename = filename.trim() || "firmware_logs";

    if (withDatetime) {
      const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
      return `${baseFilename}_${today}.${type}`;
    } else {
      return `${baseFilename}.${type}`;
    }
  };

  const handleExport = async (type: "csv" | "pdf") => {
    setIsExporting(true);
    setExportingType(type);

    try {
      // Create export parameters with explicit defaults
      const exportParams: Record<string, string> = {
        type,
        auto_gen_fname: "true",
        with_datetime: "false",
      };

      // Override with user choices
      if (filename.trim()) {
        exportParams.auto_gen_fname = "false";
        exportParams.filename = filename.trim();
      }

      exportParams.with_datetime = withDatetime ? "true" : "false";

      // Add filters if they have values
      if (filters.node_location) {
        exportParams.node_location = filters.node_location;
      }
      if (filters.node_type) {
        exportParams.node_type = filters.node_type;
      }
      if (filters.flash_status) {
        exportParams.flash_status = filters.flash_status;
      }

      // Call the backend export API
      await logController.exportLogs(exportParams);

      toast.success("Export Successful", {
        description: `${type.toUpperCase()} file downloaded successfully`,
      });

      onOpenChange(false);
    } catch (error) {
      toast.error("Export Failed", {
        description:
          error instanceof Error ? error.message : "Failed to export file",
      });
    } finally {
      setIsExporting(false);
      setExportingType(null);
    }
  };

  const resetForm = () => {
    setFilename("");
    setWithDatetime(true);
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      resetForm();
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="w-[95vw] max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Export Logs</DialogTitle>
          <DialogDescription>
            Download firmware update logs with current filters applied
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Export Summary */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Export Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Records (Current):</span>
                <span className="font-medium">{logs.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Records (Total):</span>
                <span className="font-medium">{totalCount}</span>
              </div>

              {/* Status breakdown */}
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>✅ Successful:</span>
                  <span className="text-green-600 font-medium">
                    {summary.successful}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>❌ Failed:</span>
                  <span className="text-red-600 font-medium">
                    {summary.failed}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>⏳ In Progress:</span>
                  <span className="text-orange-600 font-medium">
                    {summary.inProgress}
                  </span>
                </div>
              </div>

              {/* Success Rate */}
              <div className="flex justify-between text-sm border-t pt-2">
                <span>Success Rate:</span>
                <Badge variant="outline" className="text-xs">
                  {summary.successRate}%
                </Badge>
              </div>

              {/* Active Filters */}
              {(filters.node_location ||
                filters.node_type ||
                filters.flash_status) && (
                <div className="border-t pt-2">
                  <p className="text-xs font-medium text-muted-foreground mb-1">
                    Active Filters:
                  </p>
                  <div className="space-y-1">
                    {filters.node_location && (
                      <div className="flex justify-between text-xs">
                        <span>Location:</span>
                        <Badge variant="secondary" className="text-xs">
                          {filters.node_location}
                        </Badge>
                      </div>
                    )}
                    {filters.node_type && (
                      <div className="flex justify-between text-xs">
                        <span>Type:</span>
                        <Badge variant="secondary" className="text-xs">
                          {filters.node_type}
                        </Badge>
                      </div>
                    )}
                    {filters.flash_status && (
                      <div className="flex justify-between text-xs">
                        <span>Status:</span>
                        <Badge variant="secondary" className="text-xs">
                          {filters.flash_status}
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Export Options */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Export Options</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="filename" className="text-sm">
                  Custom Filename (optional)
                </Label>
                <Input
                  id="filename"
                  placeholder="e.g., firmware_report"
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  disabled={isExporting}
                />
                <p className="text-xs text-muted-foreground">
                  Leave empty for auto-generated filename
                </p>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="datetime"
                  checked={withDatetime}
                  onCheckedChange={(checked: boolean) =>
                    setWithDatetime(checked)
                  }
                  disabled={isExporting}
                />
                <Label htmlFor="datetime" className="text-sm">
                  Include date in filename (YYYY-MM-DD)
                </Label>
              </div>
            </CardContent>
          </Card>

          {/* Preview */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Preview Filenames</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>CSV:</span>
                <span className="font-mono text-xs text-gray-300">
                  📄 {getPreviewFilename("csv")}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>PDF:</span>
                <span className="font-mono text-xs text-gray-300">
                  📋 {getPreviewFilename("pdf")}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Export Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Button
              onClick={() => handleExport("csv")}
              disabled={isExporting}
              variant="outline"
              className="w-full"
            >
              {isExporting && exportingType === "csv" ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <FileText className="h-4 w-4 mr-2" />
              )}
              Export CSV
            </Button>

            <Button
              onClick={() => handleExport("pdf")}
              disabled={isExporting}
              className="w-full"
            >
              {isExporting && exportingType === "pdf" ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Download className="h-4 w-4 mr-2" />
              )}
              Export PDF
            </Button>
          </div>

          {/* Format Information */}
          <div className="text-xs text-muted-foreground text-center space-y-1 border-t pt-3">
            <p>
              <strong>CSV:</strong> Spreadsheet format for data analysis
            </p>
            <p>
              <strong>PDF:</strong> Document format for reports and sharing
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
