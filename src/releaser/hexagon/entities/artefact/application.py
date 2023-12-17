from dataclasses import dataclass

from .image import Image, PlatformImage


@dataclass(frozen=True)
class Application:
    """An application in the repository."""

    images: list[Image]
    """The images produced by the application."""

    @classmethod
    def parse_dict(cls, data: dict[str, list[dict[str, str]]]) -> "Application":
        """Parse an application from a dictionary."""
        return cls(
            images=[Image.parse_dict(image) for image in data["images"]],
        )

    def contains_image_for_any_repository(self, *repositories: str) -> bool:
        """Check if the application contains any of the repositories."""
        return any(
            repository in image.repository
            for image in self.images
            for repository in repositories
        )

    def contains_image_for_any_platform(self, *platforms: str) -> bool:
        """Check if the application contains any of the platforms."""
        return any(
            platform in image.get_platforms()
            for image in self.images
            for platform in platforms
        )

    def contains_image_for_any_manifest_tag(self, *manifest_tags: str) -> bool:
        """Check if the application contains any of the manifest tags."""
        return any(
            image.tag
            for image in self.images
            for manifest_tag in manifest_tags
            if image.contains_manifest_tag(manifest_tag)
        )

    def get_images(
        self,
        repositories: list[str] | None = None,
        manifest_tags: list[str] | None = None,
    ) -> list[Image]:
        """Get images.

        If `repositories` is specified, only images for those repositories are returned.
        If `manifest_tags` is specified, only images for those manifest tags are returned.
        """
        images = iter(self.images)
        if repositories:
            images = (
                image for image in self.images if image.repository in repositories
            )
        if manifest_tags:
            images = (
                image
                for image in images
                if any(image.contains_manifest_tag(tag) for tag in manifest_tags)
            )
        return list(images)

    def get_repositories(
        self,
        repositories: list[str] | None = None,
        manifest_tags: list[str] | None = None,
    ) -> list[str]:
        """Get repositories.

        If `repositories` is specified, only images for those repositories are returned.
        If `manifest_tags` is specified, only images for those manifest tags are returned.
        """
        images = self.get_images(repositories, manifest_tags)
        return [image.repository for image in images]

    def get_platform_images(
        self,
        repositories: list[str] | None = None,
        platforms: list[str] | None = None,
        manifest_tags: list[str] | None = None,
    ) -> list[PlatformImage]:
        """Get platform images.

        If `repositories` is specified, only platform images for those repositories are returned.
        If `platforms` is specified, only platform images for those platforms are returned.
        If `manifest_tags` is specified, only platform images for those manifest tags are returned.
        """
        images = self.get_images(repositories, manifest_tags)
        return [
            platform_image
            for image in images
            for platform_image in image.get_platform_images(platforms)
        ]

    def get_platform_tags(
        self,
        repositories: list[str] | None = None,
        platforms: list[str] | None = None,
        manifest_tags: list[str] | None = None,
    ) -> list[str]:
        """Get platform tags.

        If `repositories` is specified, only platform tags for those repositories are returned.
        If `platforms` is specified, only platform tags for those platforms are returned.
        If `manifest_tags` is specified, only platform tags for those manifest tags are returned.
        """
        images = self.get_images(repositories, manifest_tags)
        return [tag for image in images for tag in image.get_platform_tags(platforms)]

    def get_platforms(
        self,
        repositories: list[str] | None = None,
        platforms: list[str] | None = None,
        manifest_tags: list[str] | None = None,
    ) -> list[str]:
        """Get platforms.

        If `repositories` is specified, only platforms for those repositories are returned.
        If `platforms` is specified, only platforms for those platforms are returned.
        If `manifest_tags` is specified, only platforms for those manifest tags are returned.
        """
        images = self.get_images(repositories, manifest_tags)
        return [
            platform for image in images for platform in image.get_platforms(platforms)
        ]
