from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Image:
    """An image defined in a release strategy"""

    repository: str
    """The image repository."""

    platforms: list[str] | None = None
    """The platforms supported by this image."""

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "Image":
        """Parse an image from a dictionary."""
        return cls(
            repository=data["repository"],
            platforms=data.get("platforms"),
        )
