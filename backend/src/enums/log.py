from enum import Enum


class LogStatus(str, Enum):
    """
    Enum for log status.
    """
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in progress"

    def __str__(self) -> str:
        return self.value