from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlatformImage:
    """An image for a specific platform."""

    image: str
    """The full image name."""

    tag: str
    """The tag of the image."""


@dataclass
class Image:
    """An image produced by a development repository release.

    When no platform is specified, manifest_tag and platform_tag are the same,
    and manifest_image and platform_image are the same.
    """

    repository: str
    """The image repository."""

    image: str
    """The full image name."""

    tag: str
    """The tag of the image."""

    platforms: dict[str, PlatformImage] = field(default_factory=dict)
    """The platform specific images used by this image manifest (if any)."""

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "Image":
        """Parse an image from a dictionary."""
        image = cls(
            repository=data["repository"],
            tag=data["tag"],
            image=data["image"],
        )
        if platforms := data.get("platforms"):
            for platform, platform_image in platforms.items():
                image.platforms[platform] = PlatformImage(
                    image=platform_image["image"],
                    tag=platform_image["tag"],
                )
        return image

    def contains_image_for_any_platform(self, *platforms: str) -> bool:
        """Check if the image contains the platform."""
        return any(platform in self.platforms for platform in platforms)

    def contains_manifest_tag(
        self,
        manifest_tag: str,
    ) -> bool:
        """Check if the image has the manifest tag."""
        return self.platforms != {} and self.tag == manifest_tag

    def get_platform_images(
        self,
        platforms: list[str] | None = None,
    ) -> list[PlatformImage]:
        """Get platform images.

        If `platforms` is specified, only platform images for those platforms are returned.
        """
        if not platforms:
            return list(self.platforms.values())
        return [
            self.platforms[platform]
            for platform in platforms
            if platform in self.platforms
        ]

    def get_platform_tags(
        self,
        platforms: list[str] | None = None,
    ) -> list[str]:
        """Get platform tags.

        If `platforms` is specified, only platform tags for those platforms are returned.
        """
        if not platforms:
            return [platform_image.tag for platform_image in self.platforms.values()]
        return [
            platform_image.tag
            for platform, platform_image in self.platforms.items()
            if platform in platforms
        ]

    def get_platforms(
        self,
        platforms: list[str] | None = None,
    ) -> list[str]:
        """Get platforms.

        If `platforms` is specified, only platforms for within given platforms are returned.
        """
        if not platforms:
            return list(self.platforms.keys())
        return [platform for platform in platforms if platform in self.platforms]
