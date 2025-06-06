import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { FileUpload } from "@/components/ui/file-upload";
import { Loader2, Link as LinkIcon } from "lucide-react";
import {
  addFirmwareSchema,
  type AddFirmwareInput,
} from "@/schemas/nodeSchemas";
import { nodeController } from "@/controllers";
import { toast } from "@/utils/notifications";
import type { Node, ApiError } from "@/types";

interface AddFirmwareDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
  existingNodes: Node[];
}

type UploadMethod = "file" | "url";

export function AddFirmwareDialog({
  open,
  onOpenChange,
  onSuccess,
  existingNodes,
}: AddFirmwareDialogProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedNodeCodename, setSelectedNodeCodename] = useState("");
  const [uploadMethod, setUploadMethod] = useState<UploadMethod>("file");

  // File upload states
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<
    "idle" | "uploading" | "success" | "error"
  >("idle");

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
    clearErrors,
  } = useForm<AddFirmwareInput>({
    resolver: zodResolver(addFirmwareSchema),
  });

  const firmwareUrl = watch("firmware_url");

  const onSubmit = async (data: AddFirmwareInput) => {
    if (!selectedNodeCodename) {
      setError("Please select a node");
      return;
    }

    // Validate based on upload method
    if (uploadMethod === "file" && !selectedFile) {
      setError("Please upload a firmware file");
      return;
    }

    if (uploadMethod === "url" && !data.firmware_url) {
      setError("Please enter a firmware URL");
      return;
    }

    setIsLoading(true);
    setUploadStatus("uploading");
    setUploadProgress(0);
    setError("");

    try {
      const firmwareData = {
        firmware_version: data.firmware_version,
        ...(uploadMethod === "file"
          ? { firmware_file: selectedFile! }
          : { firmware_url: data.firmware_url! }),
      };

      await nodeController.addFirmware(
        selectedNodeCodename,
        firmwareData,
        (progress) => {
          setUploadProgress(progress);
        },
      );

      setUploadStatus("success");

      toast.success("Firmware Added Successfully", {
        description: `Firmware version ${data.firmware_version} added successfully`,
      });

      handleDialogClose();
      onSuccess();
    } catch (error: unknown) {
      setUploadStatus("error");
      const errorMessage =
        (error as ApiError).message || "Failed to add firmware version";
      setError(errorMessage);
      toast.error("Add Firmware Failed", {
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setUploadStatus("idle");
    setError("");
    clearErrors();
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setUploadStatus("idle");
    setUploadProgress(0);
    clearErrors();
  };

  const handleDialogClose = () => {
    reset();
    setSelectedNodeCodename("");
    setSelectedFile(null);
    setUploadStatus("idle");
    setUploadProgress(0);
    setUploadMethod("file");
    setError("");
    onOpenChange(false);
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      handleDialogClose();
    } else {
      onOpenChange(newOpen);
    }
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setValue("firmware_url", url);
    setError("");
    clearErrors();
  };

  const getMaxFileSize = () => {
    return parseInt(import.meta.env.VITE_MAX_FILE_SIZE_MB) || 3;
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Firmware Version</DialogTitle>
          <DialogDescription>
            Add a new firmware version to an existing node
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="node">Select Node *</Label>
            <Select
              value={selectedNodeCodename}
              onValueChange={setSelectedNodeCodename}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Choose a node..." />
              </SelectTrigger>
              <SelectContent>
                {existingNodes.map((node) => (
                  <SelectItem key={node._id} value={node.node_codename}>
                    <div className="flex flex-col text-left w-full">
                      <span className="font-mono text-sm">
                        {node.node_codename}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {node.node_location} - {node.node_type} ({node.node_id})
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Upload Method Selection */}
          <div className="space-y-3">
            <Label>Firmware Source *</Label>
            <div className="flex gap-2">
              <Button
                type="button"
                variant={uploadMethod === "file" ? "default" : "outline"}
                size="sm"
                onClick={() => setUploadMethod("file")}
                className="flex-1"
              >
                Upload File
              </Button>
              <Button
                type="button"
                variant={uploadMethod === "url" ? "default" : "outline"}
                size="sm"
                onClick={() => setUploadMethod("url")}
                className="flex-1"
              >
                <LinkIcon className="h-4 w-4 mr-1" />
                Use URL
              </Button>
            </div>
          </div>

          {/* File Upload */}
          {uploadMethod === "file" && (
            <div className="space-y-2">
              <Label>Firmware File *</Label>
              <FileUpload
                onFileSelect={handleFileSelect}
                onFileRemove={handleFileRemove}
                selectedFile={selectedFile}
                uploadProgress={uploadProgress}
                uploadStatus={uploadStatus}
                errorMessage={error}
                disabled={isLoading}
                accept=".bin"
                maxSize={getMaxFileSize()}
              />
              <p className="text-xs text-muted-foreground">
                Only .bin files are supported (max {getMaxFileSize()}MB)
              </p>
            </div>
          )}

          {/* URL Input */}
          {uploadMethod === "url" && (
            <div className="space-y-2">
              <Label htmlFor="firmware_url">Firmware URL *</Label>
              <Input
                id="firmware_url"
                {...register("firmware_url")}
                onChange={handleUrlChange}
                placeholder="https://example.com/firmware.bin"
                className="w-full"
              />
              {errors.firmware_url && (
                <p className="text-sm text-destructive">
                  {errors.firmware_url.message}
                </p>
              )}
              <p className="text-xs text-muted-foreground">
                Enter a direct URL to a .bin firmware file
              </p>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="firmware_version">Firmware Version *</Label>
            <Input
              id="firmware_version"
              {...register("firmware_version")}
              placeholder="e.g., 1.0.0"
              className="w-full"
            />
            {errors.firmware_version && (
              <p className="text-sm text-destructive">
                {errors.firmware_version.message}
              </p>
            )}
          </div>

          {/* Progress Indicator */}
          {uploadStatus === "uploading" && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Uploading firmware...</span>
                <span>{Math.round(uploadProgress)}%</span>
              </div>
              <div className="w-full bg-muted-foreground/20 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              className="flex-1"
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={
                isLoading ||
                (uploadMethod === "file" && !selectedFile) ||
                (uploadMethod === "url" && !firmwareUrl)
              }
            >
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {uploadStatus === "uploading" ? "Uploading..." : "Add Firmware"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
