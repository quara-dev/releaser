from __future__ import annotations

import pytest

from releaser.hexagon.entities import artefact, strategy
from releaser.hexagon.services.manifest_generator import ManifestGenerator

from ..stubs import GitReaderStub, JsonWriterStub, StrategyReaderStub, VersionReaderStub


class ManifestGeneratorSetup:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        git_reader: GitReaderStub,
        json_writer: JsonWriterStub,
        strategy_reader: StrategyReaderStub,
        version_reader: VersionReaderStub,
    ):
        self.git_reader = git_reader
        self.json_writer = json_writer
        self.strategy_reader = strategy_reader
        self.version_reader = version_reader
        self.service = ManifestGenerator(
            git_reader=git_reader,
            manifest_writer=json_writer,
            strategy_reader=strategy_reader,
            version_reader=version_reader,
        )


class TestManifestGenerator(ManifestGeneratorSetup):
    def test_without_application(
        self,
    ):
        # Arrange
        self.git_reader.set_is_dirty(False)
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={},
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {}


class TestManifestGeneratorWithSingleApplication(ManifestGeneratorSetup):
    def test_without_image(
        self,
    ):
        # Arrange
        self.git_reader.set_is_dirty(False)
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={"test-app": strategy.Application()},
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {}

    def test_with_single_image_and_literal_commit_msg_matcher(
        self,
    ):
        # Arrange
        self.git_reader.set_is_dirty(False)
        self.git_reader.set_history(["this is the latest commit message"])
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                        on_commit_msg=[
                            strategy.CommitMsgMatchPolicy(
                                match=["*"], tags=[strategy.LiteralTag(value="head")]
                            ),
                        ],
                    )
                },
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="head",
                        image="test-image:head",
                    )
                ]
            )
        }

    @pytest.mark.parametrize(
        "last_commit", ["the first pattern is ...", "the second pattern is ..."]
    )
    def test_with_single_image_and_git_sha_tag_policy_matcher_with_all_matcher(
        self, last_commit: str
    ):
        # Arrange
        self.git_reader.set_sha("1234567")
        self.git_reader.set_history([last_commit])
        self.git_reader.set_is_dirty(False)
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                        on_commit_msg=[
                            strategy.CommitMsgMatchPolicy(
                                match=["*"], tags=[strategy.LiteralTag(value="head")]
                            ),
                            strategy.CommitMsgMatchPolicy(
                                match=["*"], tags=[strategy.GitCommitShaTag(size=7)]
                            ),
                        ],
                    )
                },
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="head",
                        image="test-image:head",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="1234567",
                        image="test-image:1234567",
                    ),
                ]
            )
        }

    def test_with_single_image_and_git_sha_tag_policy_matcher_with_single_matcher(
        self,
    ):
        # Arrange
        self.git_reader.set_sha("1234567")
        self.git_reader.set_history(["this is the latest commit message"])
        self.git_reader.set_is_dirty(False)
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                        on_commit_msg=[
                            strategy.CommitMsgMatchPolicy(
                                match=["*"], tags=[strategy.LiteralTag(value="head")]
                            ),
                            strategy.CommitMsgMatchPolicy(
                                match=["this is the latest commit"],
                                tags=[strategy.GitCommitShaTag(size=7)],
                            ),
                        ],
                    )
                },
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="head",
                        image="test-image:head",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="1234567",
                        image="test-image:1234567",
                    ),
                ]
            )
        }

    def test_with_single_image_and_git_sha_tag_policy_matcher_with_single_matcher_no_match(
        self,
    ):
        # Arrange
        self.git_reader.set_sha("1234567")
        self.git_reader.set_history(["a message which does not match expected pattern"])
        self.git_reader.set_is_dirty(False)
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                        on_commit_msg=[
                            strategy.CommitMsgMatchPolicy(
                                match=["*"], tags=[strategy.LiteralTag(value="head")]
                            ),
                            strategy.CommitMsgMatchPolicy(
                                match=["the expected pattern"],
                                tags=[strategy.GitCommitShaTag(size=7)],
                            ),
                        ],
                    )
                },
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="head",
                        image="test-image:head",
                    ),
                ]
            )
        }

    @pytest.mark.parametrize(
        "last_commit", ["the first pattern is ...", "the second pattern is ..."]
    )
    def test_with_single_image_and_git_sha_tag_policy_matcher_with_many_matchers(
        self, last_commit: str
    ):
        # Arrange
        self.git_reader.set_sha("1234567")
        self.git_reader.set_history([last_commit])
        self.git_reader.set_is_dirty(False)
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                        on_commit_msg=[
                            strategy.CommitMsgMatchPolicy(
                                match=["*"], tags=[strategy.LiteralTag(value="head")]
                            ),
                            strategy.CommitMsgMatchPolicy(
                                match=["the first pattern", "the second pattern"],
                                tags=[strategy.GitCommitShaTag(size=7)],
                            ),
                        ],
                    )
                },
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="head",
                        image="test-image:head",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="1234567",
                        image="test-image:1234567",
                    ),
                ]
            )
        }

    def test_with_single_image_and_version_plus_git_tag_sha_policy_matcher_with_all_matcher(
        self,
    ) -> None:
        # Arrange
        self.git_reader.set_sha("1234567")
        self.git_reader.set_history(["the first pattern is ..."])
        self.git_reader.set_is_dirty(False)
        self.version_reader.set_version("1.2.3")
        self.version_reader.set_version("1.2.3")
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                        on_commit_msg=[
                            strategy.CommitMsgMatchPolicy(
                                match=["*"], tags=[strategy.LiteralTag(value="head")]
                            ),
                            strategy.CommitMsgMatchPolicy(
                                match=["*"],
                                tags=[
                                    strategy.VersionTag(),
                                    strategy.GitCommitShaTag(size=7),
                                ],
                            ),
                        ],
                    )
                },
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None

        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="head",
                        image="test-image:head",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="1.2.3",
                        image="test-image:1.2.3",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="1234567",
                        image="test-image:1234567",
                    ),
                ]
            )
        }

    def test_with_single_image_and_version_plus_git_sha_tag_policy_policy_matcher_with_single_matcher(
        self,
    ):
        # Arrange
        self.git_reader.set_sha("1234567")
        self.git_reader.set_history(["chore(release): bump to version 1.2.3"])
        self.git_reader.set_is_dirty(False)
        self.version_reader.set_version("1.2.3")
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                        on_commit_msg=[
                            strategy.CommitMsgMatchPolicy(
                                match=["*"], tags=[strategy.LiteralTag(value="head")]
                            ),
                            strategy.CommitMsgMatchPolicy(
                                match=["chore\\(release\\): bump to version"],
                                tags=[
                                    strategy.LiteralTag(value="edge"),
                                    strategy.VersionTag(),
                                    strategy.GitCommitShaTag(size=7),
                                ],
                            ),
                        ],
                    )
                },
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None

        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="head",
                        image="test-image:head",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="edge",
                        image="test-image:edge",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="1.2.3",
                        image="test-image:1.2.3",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="1234567",
                        image="test-image:1234567",
                    ),
                ]
            )
        }


class TestManifestGeneratorWithSingleApplicationInheritingStrategy(
    ManifestGeneratorSetup
):
    @pytest.mark.parametrize(
        "last_commit", ["the first pattern is ...", "the second pattern is ..."]
    )
    def test_with_single_image_and_git_sha_tag_policy_matcher_with_all_matcher(
        self, last_commit: str
    ):
        # Arrange
        self.git_reader.set_sha("1234567")
        self.git_reader.set_history([last_commit])
        self.git_reader.set_is_dirty(False)
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                    )
                },
                on_commit_msg=[
                    strategy.CommitMsgMatchPolicy(
                        match=["*"],
                        tags=[
                            strategy.LiteralTag(value="next"),
                            strategy.GitCommitShaTag(size=7),
                        ],
                    )
                ],
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="next",
                        image="test-image:next",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="1234567",
                        image="test-image:1234567",
                    ),
                ]
            )
        }

    def test_with_single_image_and_git_sha_tag_policy_matcher_with_single_matcher(
        self,
    ):
        # Arrange
        self.git_reader.set_sha("1234567")
        self.git_reader.set_history(["this is the latest commit message"])
        self.git_reader.set_is_dirty(False)
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                    )
                },
                on_commit_msg=[
                    strategy.CommitMsgMatchPolicy(
                        match=["*"], tags=[strategy.LiteralTag(value="next")]
                    ),
                    strategy.CommitMsgMatchPolicy(
                        match=["this is the latest commit"],
                        tags=[strategy.GitCommitShaTag(size=7)],
                    ),
                ],
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="next",
                        image="test-image:next",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="1234567",
                        image="test-image:1234567",
                    ),
                ]
            )
        }

    def test_with_single_image_and_git_sha_tag_policy_matcher_with_single_matcher_no_match(
        self,
    ):
        # Arrange
        self.git_reader.set_sha("1234567")
        self.git_reader.set_history(["a message which does not match expected pattern"])
        self.git_reader.set_is_dirty(False)
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                    )
                },
                on_commit_msg=[
                    strategy.CommitMsgMatchPolicy(
                        match=["*"], tags=[strategy.LiteralTag(value="next")]
                    ),
                    strategy.CommitMsgMatchPolicy(
                        match=["the expected pattern"],
                        tags=[strategy.GitCommitShaTag(size=7)],
                    ),
                ],
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="next",
                        image="test-image:next",
                    ),
                ]
            )
        }

    @pytest.mark.parametrize(
        "last_commit", ["the first pattern is ...", "the second pattern is ..."]
    )
    def test_with_single_image_and_git_sha_tag_policy_matcher_with_many_matchers(
        self, last_commit: str
    ):
        # Arrange
        self.git_reader.set_sha("1234567")
        self.git_reader.set_history([last_commit])
        self.git_reader.set_is_dirty(False)
        self.strategy_reader.set_strategy(
            strategy.ReleaseStrategy(
                applications={
                    "test-app": strategy.Application(
                        images=[strategy.Image("test-image")],
                    )
                },
                on_commit_msg=[
                    strategy.CommitMsgMatchPolicy(
                        match=["*"], tags=[strategy.LiteralTag(value="next")]
                    ),
                    strategy.CommitMsgMatchPolicy(
                        match=["the first pattern", "the second pattern"],
                        tags=[strategy.GitCommitShaTag(size=7)],
                    ),
                ],
            )
        )
        # Act
        self.service.execute()
        # Assert
        manifest = self.json_writer.read_manifest()
        assert manifest is not None
        assert manifest.applications == {
            "test-app": artefact.Application(
                images=[
                    artefact.Image(
                        repository="test-image",
                        tag="next",
                        image="test-image:next",
                    ),
                    artefact.Image(
                        repository="test-image",
                        tag="1234567",
                        image="test-image:1234567",
                    ),
                ]
            )
        }
