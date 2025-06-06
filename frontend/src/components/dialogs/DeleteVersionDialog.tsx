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

interface DeleteVersionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (deleteAllVersions: boolean) => void;
  nodeCodename: string;
  selectedVersion: string;
  hasMultipleVersions: boolean;
}

export function DeleteVersionDialog({
  open,
  onOpenChange,
  onConfirm,
  nodeCodename,
  selectedVersion,
  hasMultipleVersions,
}: DeleteVersionDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {hasMultipleVersions ? "Delete Scope" : "Delete Node"}
          </AlertDialogTitle>
          <AlertDialogDescription>
            You want to delete <strong>{nodeCodename}</strong>.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="space-y-3">
          {hasMultipleVersions ? (
            <div className="text-sm text-muted-foreground">
              This node has multiple firmware versions. Do you want to delete
              the current version ({selectedVersion}) only, or delete the entire
              node with all its firmware versions?
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">
              This will permanently delete the node and all its data. This
              action cannot be undone.
            </div>
          )}
        </div>

        <AlertDialogFooter className="gap-2">
          <AlertDialogCancel onClick={() => onOpenChange(false)}>
            Cancel
          </AlertDialogCancel>

          {hasMultipleVersions ? (
            <>
              <AlertDialogAction
                onClick={() => onConfirm(false)}
                className="bg-orange-600 hover:bg-orange-700"
              >
                Delete Version Only ({selectedVersion})
              </AlertDialogAction>
              <AlertDialogAction
                onClick={() => onConfirm(true)}
                className="bg-red-600 hover:bg-red-700"
              >
                Delete All
              </AlertDialogAction>
            </>
          ) : (
            <AlertDialogAction
              onClick={() => onConfirm(true)}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete Node
            </AlertDialogAction>
          )}
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
