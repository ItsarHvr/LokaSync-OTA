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
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2 } from "lucide-react";
import { addNodeSchema, type AddNodeInput } from "@/schemas/nodeSchemas";
import { nodeController } from "@/controllers";
import { toast } from "@/utils/notifications";
import type { ApiError } from "@/types";

interface AddNodeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function AddNodeDialog({
  open,
  onOpenChange,
  onSuccess,
}: AddNodeDialogProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<AddNodeInput>({
    resolver: zodResolver(addNodeSchema),
  });

  const onSubmit = async (data: AddNodeInput) => {
    setIsLoading(true);
    setError("");

    try {
      await nodeController.createNode(data);

      toast.success("Node Created Successfully", {
        description: "Node created successfully",
      });

      reset();
      onOpenChange(false);
      onSuccess();
    } catch (error: unknown) {
      const errorMessage =
        (error as ApiError).message || "Failed to create node";
      setError(errorMessage);
      toast.error("Create Node Failed", {
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      reset();
      setError("");
    }
    onOpenChange(newOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Add New Node</DialogTitle>
          <DialogDescription>Create a new node in the system</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-2">
            <Label htmlFor="node_id">Node ID *</Label>
            <Input
              id="node_id"
              {...register("node_id")}
              placeholder="e.g., 1a / 2b / 3c"
              maxLength={10}
            />
            {errors.node_id && (
              <p className="text-sm text-destructive">
                {errors.node_id.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="node_location">Location *</Label>
            <Input
              id="node_location"
              {...register("node_location")}
              placeholder="e.g., Cibubur-SayuranPagi"
              maxLength={50}
            />
            {errors.node_location && (
              <p className="text-sm text-destructive">
                {errors.node_location.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="node_type">Type *</Label>
            <Input
              id="node_type"
              {...register("node_type")}
              placeholder="e.g., Penyemaian / Pembibitan"
              maxLength={30}
            />
            {errors.node_type && (
              <p className="text-sm text-destructive">
                {errors.node_type.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              {...register("description")}
              placeholder="Optional description..."
              className="h-20"
            />
            {errors.description && (
              <p className="text-sm text-destructive">
                {errors.description.message}
              </p>
            )}
          </div>

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
            <Button type="submit" className="flex-1" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Node
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
