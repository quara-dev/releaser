from __future__ import annotations

import json
import subprocess
from pathlib import Path

from releaser.hexagon.entities import bakery
from releaser.hexagon.ports import ImageBaker


class BuildxImageBaker(ImageBaker):
    """An image baker that uses buildx."""

    def __init__(
        self,
        bake_file: Path,
        metadata_file: Path,
        push: bool,
        application: str | None,
    ) -> None:
        self.bake_file = bake_file
        self.metadata_file = metadata_file
        self.push = push
        self.application = application

    def bake(self, spec: bakery.ImagesSpec) -> None:
        self.write_bake_file(spec)
        dest: list[str] = []
        if self.push:
            dest = ["--push"]
        cmd = [
            "docker",
            "buildx",
            "bake",
            "--file",
            self.bake_file.as_posix(),
            "--metadata-file",
            self.metadata_file.as_posix(),
        ]
        cmd.extend(dest)
        if self.application:
            cmd.append(self.application)
        subprocess.check_call(cmd)

    def write_bake_file(self, spec: bakery.ImagesSpec) -> None:
        self.bake_file.write_text(self.generate_bake_file(spec))

    def generate_bake_file(self, spec: bakery.ImagesSpec) -> str:
        bakefile = {}
        bakefile["target"] = {
            target.name: {
                "context": target.context,
                "dockerfile": target.dockerfile,
                "args": target.args,
                "labels": target.labels,
                "tags": target.tags,
                "pull": target.pull,
                "platforms": target.platforms,
            }
            for target in spec.target
        }
        bakefile["group"] = {
            group.name: {
                "targets": group.targets,
            }
            for group in spec.group
        }
        return json.dumps(bakefile, separators=(",", ":"))
