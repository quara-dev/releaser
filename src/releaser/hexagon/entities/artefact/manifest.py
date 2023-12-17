from dataclasses import dataclass
from typing import Any, Dict

from .application import Application
from .image import Image


@dataclass
class Manifest:
    """A manifest file."""

    applications: Dict[str, Application]
    """The applications artefacts."""

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "Manifest":
        """Parse a manifest from a dictionary."""
        return cls(
            applications={
                app: Application.parse_dict(artefacts)
                for app, artefacts in data["applications"].items()
            }
        )

    def get_apps(
        self,
        applications: list[str] | None = None,
    ) -> dict[str, Application]:
        """Get applications.

        If `applications` is specified, only applications with any of given names are returned.
        """
        if not applications:
            return self.applications
        return {
            app_name: app
            for app_name, app in self.applications.items()
            if app_name in applications
        }

    def get_images(
        self,
        applications: list[str] | None = None,
        repositories: list[str] | None = None,
        manifest_tags: list[str] | None = None,
    ) -> list[Image]:
        """Get images.

        If `applications` is specified, only images for those applications are returned.
        If `repositories` is specified, only images for those repositories are returned.
        If `manifest_tags` is specified, only images for those manifest tags are returned.
        """
        return [
            image
            for app in self.get_apps(applications).values()
            for image in app.get_images(repositories, manifest_tags)
        ]
