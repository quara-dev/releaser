"""Service used to generate manifest during a release."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator

from releaser.hexagon.entities.strategy.policy import CommitMsgMatchPolicy

from ..entities import artefact, strategy
from ..errors import ReleaseStrategyNotFoundError
from ..ports import GitReader, JsonWriter, StrategyReader, VersionReader


@dataclass
class ManifestGenerator:
    """Service used to generate manifest during a release."""

    git_reader: GitReader
    """A GitReader implementation used to read git SHA and git commit history."""

    manifest_writer: JsonWriter
    """A JsonWriter implementation used to write the generated manifest."""

    strategy_reader: StrategyReader
    """A StrategyReader implementation used to read the release strategy."""

    version_reader: VersionReader
    """A VersionReader implementation used to read the application versions."""

    def execute(self) -> None:
        """Generate the manifest."""

        strategy = self.strategy_reader.detect()
        if not strategy:
            raise ReleaseStrategyNotFoundError()
        manifest = artefact.Manifest(applications={})
        for app_name in strategy.applications:
            application_strategy = strategy.get_release_strategy_for_application(
                app_name
            )
            images = list(self._generate_application_images(application_strategy))
            if not images:
                continue
            manifest.applications[app_name] = artefact.Application(images=images)
        self.manifest_writer.write_manifest(manifest)

    def _generate_application_images(
        self,
        application_strategy: strategy.ApplicationReleaseStrategy,
    ) -> Iterator[artefact.Image]:
        """Generate the list of images to release for an application."""
        if not application_strategy.images:
            return
        tags = list(self._generate_application_tags(application_strategy))
        for image in application_strategy.images:
            for tag in tags:
                image_artefact = artefact.Image(
                    repository=image.repository,
                    tag=tag,
                    image=f"{image.repository}:{tag}",
                )
                if image.platforms:
                    for platform in image.platforms:
                        platform_tag = self._transform_tag_to_platform_tag(
                            tag, platform
                        )
                        image_artefact.platforms[platform] = artefact.PlatformImage(
                            image=f"{image.repository}:{platform_tag}",
                            tag=platform_tag,
                        )
                yield image_artefact

    def _generate_application_tags(
        self, application: strategy.ApplicationReleaseStrategy
    ) -> Iterator[str]:
        """Generate the list of tags to release for an application."""
        for policy in application.match_commit_msg:
            msg = self.git_reader.read_last_commit_message(policy.depth, policy.filter)
            if not msg:
                continue
            if self._verify_commit_msg_match_against_policy(msg, policy):
                for tag in policy.tags:
                    yield self._get_value_for_tag(tag)

    def _verify_commit_msg_match_against_policy(
        self, commit_msg: str, policy: CommitMsgMatchPolicy
    ) -> bool:
        """Check if the commit message match the policy."""
        for match_pattern in policy.match:
            if match_pattern == "*":
                return True
            try:
                regexp = re.compile(match_pattern)
            except re.error as exc:
                raise ValueError(
                    f"Invalid regexp: {match_pattern} (patterns={policy.match})"
                ) from exc
            if regexp.match(commit_msg):
                return True
        return False

    def _get_value_for_tag(
        self, tag: strategy.GitCommitShaTag | strategy.VersionTag | strategy.LiteralTag
    ) -> str:
        """Get the value of a tag."""
        if isinstance(tag, strategy.GitCommitShaTag):
            sha = self.git_reader.read_most_recent_commit_sha()
            return sha[: tag.size]
        elif isinstance(tag, strategy.VersionTag):
            version = self.version_reader.read_version_tag(tag)
            if version is None:
                raise ValueError("Version not found")
            return version
        elif isinstance(tag, strategy.LiteralTag):  # type: ignore
            return tag.value
        else:
            raise ValueError(f"Unknown tag type {tag}")

    def _transform_tag_to_platform_tag(self, tag: str, platform: str | None) -> str:
        if not platform:
            return tag
        suffix = self.get_platform_suffix(platform)
        return f"{tag}{suffix}"

    @staticmethod
    def get_platform_suffix(platform: str):
        if platform == "linux/amd64":
            suffix = "amd64"
        elif platform == "linux/arm64":
            suffix = "arm64"
        elif platform == "linux/arm/v7":
            suffix = "armv7"
        elif platform == "linux/arm/v6":
            suffix = "armv6"
        else:
            raise ValueError(f"Platform not supported: {platform}")
        return "-" + suffix
