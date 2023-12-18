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

    dockerfile: str | None = None
    """The path to the image Dockerfile."""

    context: str | None = None
    """The path to the image build context."""

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "Image":
        """Parse an image from a dictionary."""
        return cls(
            repository=data["repository"],
            platforms=data.get("platforms"),
            dockerfile=data.get("dockerfile"),
            context=data.get("context"),
        )

    def get_dockerfile(self) -> str:
        """Get the path to the Dockerfile."""
        return self.dockerfile or "Dockerfile"

    def get_context(self) -> str:
        """Get the path to the build context."""
        return self.context or "."
