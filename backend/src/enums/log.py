from enum import Enum


class LogStatus(str, Enum):
    """
    Enum for log status.
    """
    SUCCESS = "success"
    FAILED = "failed"

    def __str__(self) -> str:
        return self.value