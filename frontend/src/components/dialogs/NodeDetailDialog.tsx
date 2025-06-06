import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import type { Node } from "@/types";

interface NodeDetailDialogProps {
  node: Node | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function NodeDetailDialog({
  node,
  open,
  onOpenChange,
}: NodeDetailDialogProps) {
  if (!node) return null;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg sm:max-w-xl lg:max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Node Details</DialogTitle>
          <DialogDescription>
            Detailed information about{" "}
            <span className="font-semibold">{node.node_codename}</span>.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium">Node Codename</Label>
                <p className="font-mono text-sm mt-1">{node.node_codename}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Node ID</Label>
                <p className="font-mono text-sm mt-1">{node.node_id}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Location</Label>
                <p className="text-sm mt-1">{node.node_location}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Type</Label>
                <div className="mt-1">
                  <Badge variant="secondary">{node.node_type}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Firmware Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label className="text-sm font-medium">Current Version</Label>
                <p className="text-sm mt-1">{node.firmware_version}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Firmware URL</Label>
                <p className="text-sm mt-1 break-all text-blue-600 hover:text-blue-800">
                  <a
                    href={node.firmware_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline"
                  >
                    {node.firmware_url}
                  </a>
                </p>
              </div>
              {node.description && (
                <div>
                  <Label className="text-sm font-medium">Description</Label>
                  <p className="text-sm mt-1">{node.description}</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Timestamps</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium">Created At</Label>
                <p className="text-sm mt-1">{formatDate(node.created_at)}</p>
              </div>
              <div>
                <Label className="text-sm font-medium">Last Updated</Label>
                <p className="text-sm mt-1">
                  {formatDate(node.latest_updated)}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
}
