from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .image import Image
from .policy import Rule


@dataclass
class Application:
    """An application within a development repository."""

    on: list[Rule] | None = None
    """The tags to match for the HEAD commit."""

    images: list[Image] | None = None
    """The images produced by the application.

    Images must be a list of OCI-compliant image repositories.
    """

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "Application":
        """Parse an application from a dictionary."""
        on = [Rule.parse_dict(rule) for rule in data.get("on", {}).values()]
        return cls(
            on=on,
            images=[_asimage(image) for image in data.get("images", [])],
        )


@dataclass
class ApplicationReleaseStrategy:
    name: str
    """The name of the application."""

    on: list[Rule]
    """The tags to match for the HEAD commit."""

    images: list[Image]
    """The images produced by the application.

    Images must be a list of OCI-compliant image repositories.
    """


@dataclass(frozen=True)
class ReleaseStrategy:
    """A release strategy for a development repository."""

    applications: dict[str, Application]
    """The applications in the repository. Each application may define a custom release strategy."""

    on: list[Rule] = field(default_factory=list)
    """The rules to set tags.
    These are global rules that apply to all applications.
    """

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "ReleaseStrategy":
        """Parse a release strategy from a dictionary."""
        strategy = cls(
            applications={
                name: Application.parse_dict(application)
                for name, application in data.get("applications", {}).items()
            },
            on=[Rule.parse_dict(rule) for rule in data.get("on", {}).values()],
        )
        for app in strategy.applications.values():
            if not app.on:
                app.on = strategy.on
        return strategy

    def get_release_strategy_for_application(
        self, name: str
    ) -> ApplicationReleaseStrategy:
        """Get the release strategy for an application."""
        for app_name, application in self.applications.items():
            if app_name == name:
                return ApplicationReleaseStrategy(
                    name=app_name,
                    on=_aslist(application.on) or self.on,
                    images=application.images or [],
                )
        raise ValueError(f"Application {name} not found in release strategy")


def _aslist(any: Any) -> list[Any]:
    """Convert a value to a list."""
    if any is None:
        return []
    if not isinstance(any, list):
        return [any]
    return any  # type: ignore


def _asimage(value: str | dict[str, Any]) -> Image:
    """Convert a value to an image."""
    if isinstance(value, str):
        return Image(repository=value)
    return Image.parse_dict(value)
