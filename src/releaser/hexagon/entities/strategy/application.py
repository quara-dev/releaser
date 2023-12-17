from dataclasses import dataclass
from typing import Any

from .image import Image
from .policy import CommitMsgMatchPolicy


@dataclass
class Application:
    """An application within a development repository."""

    on_commit_msg: list[CommitMsgMatchPolicy] | None = None
    """The tags to match for the HEAD commit."""

    images: list[Image] | None = None
    """The images produced by the application.

    Images must be a list of OCI-compliant image repositories.
    """

    @classmethod
    def parse_dict(cls, data: dict[str, Any]) -> "Application":
        """Parse an application from a dictionary."""
        policies: list[Any] | dict[str, Any] = data.get("on_commit_msg", [])
        if isinstance(policies, list):
            match_policies = [
                CommitMsgMatchPolicy.parse_dict(policy) for policy in policies
            ]
        else:
            match_policies = [CommitMsgMatchPolicy.parse_dict(policies)]
        return cls(
            on_commit_msg=match_policies,
            images=[_asimage(image) for image in data.get("images", [])],
        )


@dataclass
class ApplicationReleaseStrategy:
    name: str
    """The name of the application."""

    match_commit_msg: list[CommitMsgMatchPolicy]
    """The tags to match for the HEAD commit."""

    images: list[Image]
    """The images produced by the application.

    Images must be a list of OCI-compliant image repositories.
    """


def _asimage(value: str | dict[str, Any]) -> Image:
    """Convert a value to an image."""
    if isinstance(value, str):
        return Image(repository=value)
    return Image.parse_dict(value)
