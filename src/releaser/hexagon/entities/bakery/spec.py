from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ImageTarget:
    """A target is a docker image."""

    name: str
    context: str
    dockerfile: str
    tags: list[str]
    args: dict[str, str]
    labels: dict[str, str]
    pull: bool
    platforms: list[str]


@dataclass
class ImagesGroup:
    """A group of targets."""

    name: str
    targets: list[str]


@dataclass
class ImagesSpec:
    """Specification for a build."""

    group: list[ImagesGroup]
    target: list[ImageTarget]
