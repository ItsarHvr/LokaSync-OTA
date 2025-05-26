from enum import Enum


class NodeLocation(str, Enum):
    """Enum for node locations."""
    JAKARTA_GREENHOUSE = "Jakarta Greenhouse"
    DEPOK_GREENHOUSE = "Depok Greenhouse"

    def __str__(self):
        return self.value