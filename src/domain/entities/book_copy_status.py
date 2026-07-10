from __future__ import annotations

from enum import StrEnum


class BookCopyStatus(StrEnum):
    """Enumeration of all valid physical-copy states."""

    AVAILABLE = "available"
    DAMAGED = "damaged"
    LOST = "lost"
