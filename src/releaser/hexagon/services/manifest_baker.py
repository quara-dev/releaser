"""Service used to build manfest artefacts."""

from dataclasses import dataclass

from ..entities import bakery, strategy
from ..ports import ImageBaker
from .manifest_analyzer import ImageQuery, ManifestAnalyzer
from .manifest_generator import ManifestGenerator


@dataclass
class ManifestBaker:
    """Service used to build manfest artefacts."""

    analyzer: ManifestAnalyzer
    release_strategy: strategy.ReleaseStrategy
    image_baker: ImageBaker

    def execute(self) -> None:
        """Build the manifest artefact."""
        spec = self.create_bake_spec()
        self.image_baker.bake(spec)

    def create_bake_spec(self) -> bakery.ImagesSpec:
        """Create the bake spec."""
        manifest = self.analyzer.get_manifest()
        spec = bakery.ImagesSpec(group=[], target=[])
        for app_name in manifest.applications:
            app_strategy = self.release_strategy.applications[app_name]
            if not app_strategy.images:
                continue
            for image in app_strategy.images:
                image_artefact = manifest.get_image(app_name, image.repository)
                if not image_artefact:
                    continue
                if not image.platforms:
                    tags = self.analyzer.get_images(
                        ImageQuery(
                            application=[app_name],
                            repository=[image.repository],
                            platform=None,
                            manifest_tag=None,
                            no_platform=True,
                        )
                    )
                    spec.target.append(
                        bakery.ImageTarget(
                            name=image.repository.split("/")[-1],
                            dockerfile=image.get_dockerfile(),
                            context=image.get_context(),
                            tags=tags,
                            args={},
                            labels={},
                            pull=True,
                            platforms=[],
                        )
                    )
                else:
                    for platform in image.platforms:
                        tags = self.analyzer.get_images(
                            ImageQuery(
                                application=[app_name],
                                repository=[image.repository],
                                platform=[platform],
                                manifest_tag=None,
                                no_platform=False,
                            )
                        )
                        spec.target.append(
                            bakery.ImageTarget(
                                name=image.repository.split("/")[-1]
                                + ManifestGenerator.get_platform_suffix(platform),
                                dockerfile=image.get_dockerfile(),
                                context=image.get_context(),
                                tags=tags,
                                args={},
                                labels={},
                                pull=True,
                                platforms=[platform],
                            )
                        )
        spec.group.append(
            bakery.ImagesGroup(
                name="default",
                targets=[target.name for target in spec.target],
            )
        )
        return spec
