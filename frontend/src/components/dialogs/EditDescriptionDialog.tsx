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

interface EditDescriptionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (updateAllVersions: boolean) => void;
  nodeCodename: string;
  currentDescription: string;
  selectedVersion: string;
  hasMultipleVersions: boolean;
}

export function EditDescriptionDialog({
  open,
  onOpenChange,
  onConfirm,
  nodeCodename,
  currentDescription,
  selectedVersion,
  hasMultipleVersions,
}: EditDescriptionDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {hasMultipleVersions
              ? "Update Description Scope"
              : "Update Description"}
          </AlertDialogTitle>
          <AlertDialogDescription>
            You want to update the description for{" "}
            <strong>{nodeCodename}</strong>:
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="space-y-3">
          <div className="text-sm bg-muted p-3 rounded-md italic border-l-4 border-blue-500">
            "{currentDescription}"
          </div>

          {hasMultipleVersions ? (
            <div className="text-sm text-muted-foreground">
              This node has multiple firmware versions. Do you want to update
              this description for the current version ({selectedVersion}) only,
              or for all versions of this node?
            </div>
          ) : (
            <div className="text-sm text-muted-foreground">
              This will update the description for this node.
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
                className="bg-blue-600 hover:bg-blue-700"
              >
                Edit Version Only ({selectedVersion})
              </AlertDialogAction>
              <AlertDialogAction
                onClick={() => onConfirm(true)}
                className="bg-orange-600 hover:bg-orange-700"
              >
                Edit All
              </AlertDialogAction>
            </>
          ) : (
            <AlertDialogAction
              onClick={() => onConfirm(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Update Description
            </AlertDialogAction>
          )}
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
