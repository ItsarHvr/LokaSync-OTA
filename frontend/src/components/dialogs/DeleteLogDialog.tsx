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

interface DeleteLogDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  nodeCodename: string;
  sessionId: string;
}

export function DeleteLogDialog({
  open,
  onOpenChange,
  onConfirm,
  nodeCodename,
  sessionId,
}: DeleteLogDialogProps) {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Delete Firmware Update Log</AlertDialogTitle>
          <AlertDialogDescription>
            You want to delete firmware update log for{" "}
            <strong>{nodeCodename}</strong>.
          </AlertDialogDescription>
        </AlertDialogHeader>

        <div className="space-y-3">
          <div className="text-sm text-muted-foreground">
            This will permanently delete the firmware update log with session
            ID: <span className="font-mono font-medium">{sessionId}</span>
          </div>
          <div className="text-sm text-muted-foreground">
            This action cannot be undone.
          </div>
        </div>

        <AlertDialogFooter className="gap-2">
          <AlertDialogCancel onClick={() => onOpenChange(false)}>
            Cancel
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            className="bg-red-600 hover:bg-red-700"
          >
            Delete Log
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
