"""Service used to send a POST request to a webhook URL with a
manifest as JSON payload."""
from __future__ import annotations

from dataclasses import dataclass

from ..entities import artefact


@dataclass
class Query:
    """Base class for all queries."""

    pass


@dataclass
class ApplicationQuery(Query):
    """Options allowed when querying applications."""

    application: list[str] | None
    """Query applications with any of the given names."""

    repository: list[str] | None
    """Query applications with images for any of the given repositories."""

    platform: list[str] | None
    """Query applications with images for any of the given platforms."""

    manifest_tag: list[str] | None
    """Query applications with images for any of the given manifest tags."""


@dataclass
class RepositoryQuery(Query):
    """Options allowed when querying repositories."""

    application: list[str] | None
    """Query repositories for applications with any of the given names."""

    platform: list[str] | None
    """Query repositories for images with any of the given platforms."""

    manifest_tag: list[str] | None
    """Query repositories for images with any of the given manifest tags."""


@dataclass
class TagQuery(Query):
    """Options allowed when querying tags."""

    application: list[str] | None
    """Query tags for applications with any of the given names."""

    repository: list[str] | None
    """Query tags for images with any of the given repositories."""

    platform: list[str] | None
    """Query tags for platform images with any of the given platforms."""

    manifest_tag: list[str] | None
    """Query tags for platform images with any of the given manifest tags."""

    no_platform: bool
    """Do not include platform tags in the result."""


@dataclass
class ImageQuery(Query):
    """Options allowed when querying images."""

    application: list[str] | None
    """Query images for applications with any of the given names."""

    repository: list[str] | None
    """Query images for any of the given repositories."""

    platform: list[str] | None
    """Query platform images for any of the given platforms."""

    manifest_tag: list[str] | None
    """Query platform images for any of the given manifest tags."""

    no_platform: bool
    """Do not include platform images in the result."""


@dataclass
class PlatformQuery(Query):
    """Options allowed when querying platforms."""

    application: list[str] | None
    """Query platforms for applications with any of the given names."""

    repository: list[str] | None
    """Query platforms for images with any of the given repositories."""

    manifest_tag: list[str] | None
    """Query platforms for images with any of the given manifest tags."""


@dataclass
class ManifestAnalyzer:
    """Service used to analyze manifest."""

    manifest: artefact.Manifest
    """The manifest to analyze."""

    def execute(self, query: Query) -> list[str]:
        """Execute query."""
        if isinstance(query, ApplicationQuery):
            return self._get_applications(query)
        if isinstance(query, RepositoryQuery):
            return self._get_repositories(query)
        if isinstance(query, ImageQuery):
            return self._get_images(query)
        if isinstance(query, TagQuery):
            return self._get_tags(query)
        if isinstance(query, PlatformQuery):
            return self._get_platforms(query)
        raise ValueError(f"Invalid query type: {type(query)}")

    def get_manifest(self) -> artefact.Manifest:
        """Get manifest."""
        return self.manifest

    def _get_applications(self, query: ApplicationQuery) -> list[str]:
        """Query applications."""
        applications: list[str] = []
        for app_name, app in self.manifest.get_apps(query.application).items():
            if query.repository and not app.contains_image_for_any_repository(
                *query.repository
            ):
                continue
            if query.platform and not app.contains_image_for_any_platform(
                *query.platform
            ):
                continue
            if query.manifest_tag and not app.contains_image_for_any_manifest_tag(
                *query.manifest_tag
            ):
                continue
            applications.append(app_name)
        return applications

    def _get_repositories(self, query: RepositoryQuery) -> list[str]:
        """Query image repositories."""
        repositories: list[str] = []
        for image in self.manifest.get_images(
            query.application, manifest_tags=query.manifest_tag
        ):
            if query.platform and not image.contains_image_for_any_platform(
                *query.platform
            ):
                continue
            repositories.append(image.repository)
        return list(set(repositories))

    def _get_images(self, query: ImageQuery) -> list[str]:
        """Query full image names."""
        images: list[str] = []
        for image in self.manifest.get_images(
            query.application, query.repository, query.manifest_tag
        ):
            if not (query.platform or query.manifest_tag) or query.no_platform:
                images.append(image.image)
            else:
                images.extend(
                    img.image for img in image.get_platform_images(query.platform)
                )
        return list(set(images))

    def _get_tags(self, query: TagQuery) -> list[str]:
        """Query image tags."""
        tags: list[str] = []
        for image_artefact in self.manifest.get_images(
            query.application, query.repository, query.manifest_tag
        ):
            if not (query.platform or query.manifest_tag) or query.no_platform:
                tags.append(image_artefact.tag)
            if not query.no_platform:
                tags.extend(image_artefact.get_platform_tags(query.platform))
        return list(set(tags))

    def _get_platforms(self, query: PlatformQuery) -> list[str]:
        """Query image platforms."""
        platforms: list[str] = []
        for image in self.manifest.get_images(
            query.application, query.repository, query.manifest_tag
        ):
            platforms.extend(image.platforms.keys())
        return list(set(platforms))
