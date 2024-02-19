"""Create a release manifest."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from releaser.hexagon.entities import artefact
from releaser.hexagon.services.manifest_analyzer import (
    ImageQuery,
    ManifestAnalyzer,
    PlatformQuery,
    RepositoryQuery,
    TagQuery,
)
from releaser.hexagon.services.manifest_generator import ManifestGenerator
from releaser.infra.git_reader.subprocess import GitSubprocessReader
from releaser.infra.json_writer.json_file import JsonFileWriter
from releaser.infra.json_writer.memory import InMemoryJsonWriter
from releaser.infra.strategy_reader.auto import AutoStrategyReader
from releaser.infra.version_reader.auto import AutoVersionReader

from ..context import GlobalOpts


@dataclass
class AnalyzeManifestCommandOptions:
    """Options for the create-manifest command."""

    manifest: Path | None
    global_opts: GlobalOpts
    query: TagQuery | ImageQuery | PlatformQuery | RepositoryQuery | None = None


class AnalyzeManifestCommand:
    def __init__(self, subparser: argparse._SubParsersAction):  # type: ignore
        self.configure_parser(subparser)  # type: ignore[no-untyped-call]

    def run(self, opts: AnalyzeManifestCommandOptions) -> int:
        """Run the analyze-manifest command."""
        service = self.create_service(opts)
        if opts.query is None:
            print(json.dumps(asdict(service.get_manifest()), separators=(",", ":")))
            return 0
        try:
            result = service.execute(opts.query)
        except ValueError:
            print("ERROR: No query provided.", file=sys.stderr)
            return 1
        print(json.dumps(result, separators=(",", ":")))
        return 0

    def configure_parser(self, subparser: argparse._SubParsersAction):  # type: ignore
        """Configure the parser for the create-manifest command."""
        self._parser = subparser.add_parser(  # type: ignore[reportUnknownMemberType]
            "analyze-manifest",
            help="Analyze a release manifest.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--input",
            "-i",
            metavar="FILE",
            default=None,
            help="Input file where release manifest will be read.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--app",
            "--application",
            metavar="APP",
            default=None,
            nargs="+",
            action="append",
            help="Filter by application.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--repository",
            "-r",
            metavar="IMAGE",
            default=None,
            nargs="+",
            action="append",
            help="Filter by image repository.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--platform",
            "-p",
            metavar="PLATFORM",
            default=None,
            nargs="+",
            action="append",
            help="Filter by platform.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--no-platform",
            action="store_true",
            default=False,
            help="Skip platform images.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--manifest-tag",
            metavar="TAG",
            default=None,
            nargs="+",
            action="append",
            help="Filter by manifest tag.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--list-tags", action="store_true", default=False, help="List tags."
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--list-images", action="store_true", default=False, help="List images."
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--list-platforms",
            action="store_true",
            default=False,
            help="List platforms.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--list-repositories",
            action="store_true",
            default=False,
            help="List repositories.",
        )

    def parse_opts(
        self, args: argparse.Namespace, opts: GlobalOpts
    ) -> AnalyzeManifestCommandOptions:
        """Parse options for the create-manifest command."""
        options = AnalyzeManifestCommandOptions(
            manifest=Path(args.input) if args.input else None,
            global_opts=opts,
        )
        if args.list_tags:
            if args.list_images or args.list_platforms:
                print(
                    "ERROR: Cannot combine --list-tags with --list-images or --list-platforms."
                )
                sys.exit(1)
            options.query = TagQuery(
                application=_flatten(args.app),
                platform=_flatten(args.platform),
                repository=_flatten(args.repository),
                no_platform=args.no_platform,
                manifest_tag=_flatten(args.manifest_tag),
            )
        elif args.list_images:
            if args.list_tags or args.list_platforms or args.list_repositories:
                print(
                    "ERROR: Cannot combine --list-images with --list-tags, --list-repositories or --list-platforms."
                )
                sys.exit(1)
            options.query = ImageQuery(
                application=_flatten(args.app),
                platform=_flatten(args.platform),
                repository=_flatten(args.repository),
                no_platform=args.no_platform,
                manifest_tag=_flatten(args.manifest_tag),
            )
        elif args.list_repositories:
            if args.list_tags or args.list_images or args.list_platforms:
                print(
                    "ERROR: Cannot combine --list-repositories with --list-tags, --list-images or --list-platforms."
                )
                sys.exit(1)
            options.query = RepositoryQuery(
                application=_flatten(args.app),
                manifest_tag=_flatten(args.manifest_tag),
                platform=_flatten(args.platform),
            )
        elif args.list_platforms:
            if args.list_tags or args.list_images or args.list_repositories:
                print(
                    "ERROR: Cannot combine --list-platforms with --list-tags, --list-repositories or --list-images."
                )
                sys.exit(1)
            if args.platform:
                print(
                    "ERROR: Cannot combine --list-platforms with --platform.",
                )
                sys.exit(1)
            if args.no_platform:
                print(
                    "ERROR: Cannot combine --list-platforms with --no-platform.",
                )
                sys.exit(1)
            options.query = PlatformQuery(
                application=_flatten(args.app),
                repository=args.repository,
                manifest_tag=_flatten(args.manifest_tag),
            )
        return options

    def create_service(
        self, options: AnalyzeManifestCommandOptions
    ) -> ManifestAnalyzer:
        """Create the service used to generate the manifest."""
        manifest = self._create_manifest(options)
        if not manifest:
            print("ERROR: No manifest found.", file=sys.stderr)
            sys.exit(1)
        service = ManifestAnalyzer(manifest)
        return service

    def _create_manifest(
        self, options: AnalyzeManifestCommandOptions
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
            strategy_reader = global_opts.get_strategy_reader(
                AutoStrategyReader(Path.cwd()),
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


def _flatten(arrays: list[list[str]]) -> list[str]:
    if not arrays:
        return []
    return [item for sublist in arrays for item in sublist]
