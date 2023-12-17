from dataclasses import dataclass, field
from typing import Any

from .application import Application, ApplicationReleaseStrategy
from .policy import CommitMsgMatchPolicy


@dataclass(frozen=True)
class ReleaseStrategy:
    """A release strategy for a development repository."""

    applications: dict[str, Application]
    """The applications in the repository. Each application may define a custom release strategy."""

    on_commit_msg: list[CommitMsgMatchPolicy] = field(default_factory=list)
    """The tags to match for the HEAD commit message.
    These are global policies that apply to all applications.
    """

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "ReleaseStrategy":
        """Parse a release strategy from a dictionary."""
        return cls(
            applications={
                name: Application.parse_dict(application)
                for name, application in data.get("applications", {}).items()
            },
            on_commit_msg=[
                CommitMsgMatchPolicy.parse_dict(policy)
                for policy in data.get("on_commit_msg", [])
            ],
        )

    def get_release_strategy_for_application(
        self, name: str
    ) -> ApplicationReleaseStrategy:
        """Get the release strategy for an application."""
        for app_name, application in self.applications.items():
            if app_name == name:
                return ApplicationReleaseStrategy(
                    name=app_name,
                    match_commit_msg=_aslist(application.on_commit_msg)
                    or self.on_commit_msg,
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
