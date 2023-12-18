"""Create a release manifest."""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from releaser.hexagon.entities import artefact
from releaser.hexagon.ports import StrategyReader
from releaser.hexagon.services.manifest_analyzer import ManifestAnalyzer
from releaser.hexagon.services.manifest_baker import ManifestBaker
from releaser.hexagon.services.manifest_generator import ManifestGenerator
from releaser.infra.git_reader.subprocess import GitSubprocessReader
from releaser.infra.image_baker.buildx import BuildxImageBaker
from releaser.infra.json_writer.json_file import JsonFileWriter
from releaser.infra.json_writer.memory import InMemoryJsonWriter
from releaser.infra.strategy_reader.auto import AutoStrategyReader
from releaser.infra.version_reader.auto import AutoVersionReader

from ..context import GlobalOpts


@dataclass
class BakeManifestCommandOptions:
    """Options for the bake-manifest command."""

    manifest: Path | None
    application: str | None
    metadata_file: Path
    bake_file: Path
    push: bool
    global_opts: GlobalOpts


class BakeManifestCommand:
    def __init__(self, subparser: argparse._SubParsersAction):  # type: ignore
        self.configure_parser(subparser)  # type: ignore[no-untyped-call]

    def run(self, opts: BakeManifestCommandOptions) -> int:
        """Run the bake-manifest command."""
        service = self.create_service(opts)
        try:
            service.execute()
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        return 0

    def configure_parser(self, subparser: argparse._SubParsersAction):  # type: ignore
        """Configure the parser for the bake-manifest command."""
        self._parser = subparser.add_parser(  # type: ignore[reportUnknownMemberType]
            "bake-manifest",
            help="Bake manifest artefacts.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--input",
            "-i",
            metavar="FILE",
            help="Input file where release manifest will be read.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--push",
            action="store_true",
            default=False,
            help="Push the artefacts to their registries (by default images are loaded into local docker engine).",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--metadata-file",
            metavar="FILEPATH",
            default="bake.output.json",
            help="Write image metadata to file (default to bake.output.json).",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--bake-file",
            metavar="FILEPATH",
            default="bake.spec.json",
            help="Write bake file to file (default to bake.spec.json).",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            nargs="?",
            action="store",
            dest="app",
            metavar="NAME",
            default=None,
            help="Bake only given application.",
        )

    def parse_opts(
        self, args: argparse.Namespace, opts: GlobalOpts
    ) -> BakeManifestCommandOptions:
        """Parse options for the create-manifest command."""
        options = BakeManifestCommandOptions(
            application=args.app,
            manifest=Path(args.input) if args.input else None,
            push=args.push,
            metadata_file=Path(args.metadata_file),
            bake_file=Path(args.bake_file),
            global_opts=opts,
        )
        return options

    def create_service(self, options: BakeManifestCommandOptions) -> ManifestBaker:
        """Create the service used to upload the manifest."""
        strategy_reader = options.global_opts.get_strategy_reader(
            AutoStrategyReader(Path.cwd()),
        )
        release_strategy = strategy_reader.detect()
        if not release_strategy:
            print("ERROR: No release strategy found.", file=sys.stderr)
            sys.exit(1)
        manifest = self._create_manifest(options, strategy_reader)
        if not manifest:
            print("ERROR: No manifest found.", file=sys.stderr)
            sys.exit(1)
        service = ManifestBaker(
            analyzer=ManifestAnalyzer(manifest),
            release_strategy=release_strategy,
            image_baker=BuildxImageBaker(
                bake_file=options.bake_file,
                metadata_file=options.metadata_file,
                push=options.push,
                application=options.application,
            ),
        )
        return service

    def _create_manifest(
        self, options: BakeManifestCommandOptions, strategy_reader: StrategyReader
    ) -> artefact.Manifest | None:
        global_opts = options.global_opts
        if options.manifest:
            reader = global_opts.get_writer(
                JsonFileWriter(options.manifest),
            )
            return reader.read_manifest()
        else:
            writer = InMemoryJsonWriter()
            git_reader = global_opts.get_reader(
                GitSubprocessReader(),
            )
            version_reader = global_opts.get_version_reader(
                AutoVersionReader(Path.cwd()),
            )
            internal_service = ManifestGenerator(
                git_reader=git_reader,
                manifest_writer=writer,
                strategy_reader=strategy_reader,
                version_reader=version_reader,
            )
            internal_service.execute()
            return writer.read_manifest()
