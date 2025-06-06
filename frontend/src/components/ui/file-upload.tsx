import React, { useCallback, useState } from "react";
import { Upload, File, X, CheckCircle, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "./button";

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  accept?: string;
  maxSize?: number;
  selectedFile?: File | null;
  uploadProgress?: number;
  uploadStatus?: "idle" | "uploading" | "success" | "error";
  errorMessage?: string;
  disabled?: boolean;
  className?: string;
}

export function FileUpload({
  onFileSelect,
  onFileRemove,
  accept = ".bin",
  maxSize = 3,
  selectedFile,
  uploadStatus = "idle",
  errorMessage,
  disabled = false,
  className,
}: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFileSelection = useCallback(
    (file: File) => {
      // Validate file size
      if (file.size > maxSize * 1024 * 1024) {
        return;
      }

      // Validate file type - only .bin files
      const fileExtension = "." + file.name.split(".").pop()?.toLowerCase();
      if (fileExtension !== ".bin") {
        return;
      }

      onFileSelect(file);
    },
    [maxSize, onFileSelect],
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (!disabled) {
        setIsDragOver(true);
      }
    },
    [disabled],
  );

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);

      if (disabled) return;

      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0) {
        handleFileSelection(files[0]);
      }
    },
    [disabled, handleFileSelection],
  );

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFileSelection(file);
      }
    },
    [handleFileSelection],
  );

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case "uploading":
        return <Upload className="h-4 w-4 animate-pulse text-blue-500" />;
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <File className="h-4 w-4" />;
    }
  };

  // If file is selected, show file info
  if (selectedFile) {
    return (
      <div className={cn("space-y-2", className)}>
        <div className="flex items-center justify-between p-3 border rounded-lg bg-muted/20">
          <div className="flex items-center gap-3">
            {getStatusIcon()}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {selectedFile.name}
              </p>
              <p className="text-xs text-muted-foreground">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
          </div>
          {uploadStatus !== "uploading" && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onFileRemove}
              className="h-8 w-8 p-0"
              disabled={disabled}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>

        {/* Remove duplicate progress bar - it's already shown in the dialog */}
        {/* Progress bar removed from here */}

        {/* Error Message */}
        {uploadStatus === "error" && errorMessage && (
          <div className="mt-2 text-xs text-red-500">{errorMessage}</div>
        )}
      </div>
    );
  }

  return (
    <div className={cn("space-y-2", className)}>
      {/* Upload Area */}
      <div
        className={cn(
          "border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer",
          isDragOver
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-muted-foreground/50",
          disabled && "opacity-50 cursor-not-allowed",
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => {
          if (!disabled) {
            document.getElementById("file-upload-input")?.click();
          }
        }}
      >
        <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
        <p className="text-sm font-medium">
          Drop your firmware file here, or{" "}
          <span className="text-primary">click to browse</span>
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          Only .bin files up to {maxSize}MB are supported
        </p>
      </div>

      {/* Hidden File Input */}
      <input
        id="file-upload-input"
        type="file"
        accept={accept}
        onChange={handleFileInput}
        className="hidden"
        disabled={disabled}
      />
    </div>
  );
}
