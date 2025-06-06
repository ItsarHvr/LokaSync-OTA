import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Wifi, AlertTriangle, ExternalLink } from "lucide-react";

interface MQTTPushConfirmationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  nodeCodename: string;
  firmwareVersion: string;
  firmwareUrl: string;
  isConnected: boolean;
}

export function MQTTPushConfirmationDialog({
  open,
  onOpenChange,
  onConfirm,
  nodeCodename,
  firmwareVersion,
  firmwareUrl,
  isConnected,
}: MQTTPushConfirmationDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent className="max-w-md">
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center gap-2">
            <Wifi className="h-5 w-5" />
            MQTT Firmware Push
          </AlertDialogTitle>
          <AlertDialogDescription>
            You are about to send firmware update command to{" "}
            <strong>{nodeCodename}</strong>
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="space-y-4">
          {/* Firmware Details */}
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-2 text-sm">
              <span className="font-medium">Node:</span>
              <span className="col-span-2 font-mono">{nodeCodename}</span>

              <span className="font-medium">Firmware Version:</span>
              <span className="col-span-2">
                <Badge variant="outline">{firmwareVersion}</Badge>
              </span>

              <span className="font-medium">Firmware URL:</span>
              <span className="col-span-2 text-xs">
                <a
                  href={firmwareUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline break-all inline-flex items-start gap-1 group"
                >
                  <span className="break-all">{firmwareUrl}</span>
                  <ExternalLink className="h-3 w-3 flex-shrink-0 mt-0.5 opacity-70 group-hover:opacity-100 transition-opacity" />
                </a>
              </span>
            </div>
          </div>

          <Separator />

          {/* Key Notes */}
          <div className="space-y-3">
            <h4 className="font-medium text-sm flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-500" />
              Important Notes:
            </h4>

            <div className="text-xs space-y-2 text-muted-foreground">
              <div className="flex gap-2">
                <span className="font-medium min-w-4">1.</span>
                <span>
                  Ensure the firmware URL you want to upload is accessible.
                </span>
              </div>
              <div className="flex gap-2">
                <span className="font-medium min-w-4">2.</span>
                <span>
                  Verify that constant values like{" "}
                  <code className="bg-muted px-1 rounded">node_codename</code>,{" "}
                  <code className="bg-muted px-1 rounded">
                    firmware_version
                  </code>
                  , and{" "}
                  <code className="bg-muted px-1 rounded">firmware_url</code>{" "}
                  are correct.
                </span>
              </div>
            </div>
          </div>

          <Separator />

          {/* Warning Alert */}
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="text-xs">
              <strong>Warning:</strong>
              <p className="inline">
                If there are errors in your firmware and it has already been
                published, this is not a program error, but a
                <strong className="font-semibold inline">
                  {" "}
                  developer (human) error
                </strong>
                . You or other team members at the node location must perform
                manual reflashing!
              </p>
            </AlertDescription>
          </Alert>

          {/* MQTT Connection Status */}
          {/* <div className="flex items-center gap-2 text-xs">
            <div
              className={`w-2 h-2 rounded-full ${isConnected ? "bg-green-500" : "bg-red-500"}`}
            />
            <span className={isConnected ? "text-green-600" : "text-red-600"}>
              MQTT {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div> */}
        </div>

        <AlertDialogFooter className="gap-2">
          <AlertDialogCancel onClick={() => onOpenChange(false)}>
            Cancel
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            disabled={!isConnected}
            className="bg-blue-600 hover:bg-blue-700"
          >
            Send Firmware Update
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
