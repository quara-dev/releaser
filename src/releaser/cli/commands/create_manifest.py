"""Create a release manifest."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from releaser.hexagon.errors import ReleaseStrategyNotFoundError
from releaser.hexagon.ports.json_writer import JsonWriter
from releaser.hexagon.services.manifest_generator import ManifestGenerator
from releaser.infra.git_reader.subprocess import GitSubprocessReader
from releaser.infra.json_writer.json_file import JsonFileWriter
from releaser.infra.json_writer.stdout import JsonStdoutWriter
from releaser.infra.strategy_reader.auto import AutoStrategyReader
from releaser.infra.version_reader.auto import AutoVersionReader

from ..context import GlobalOpts


@dataclass
class CreateManifestCommandOptions:
    """Options for the create-manifest command."""

    output: Path | None
    global_opts: GlobalOpts


class CreateManifestCommand:
    def __init__(self, subparser: argparse._SubParsersAction):  # type: ignore
        self._configure_parser(subparser)  # type: ignore[no-untyped-call]

    def run(self, opts: CreateManifestCommandOptions) -> int:
        """Run the create-manifest command."""
        service = self._create_service(opts)
        try:
            service.execute()
        except ReleaseStrategyNotFoundError as exc:
            print(f"🚨 ERROR: {str(exc)} 🚨", file=sys.stderr)
            return 1
        return 0

    def parse_opts(
        self, args: argparse.Namespace, opts: GlobalOpts
    ) -> CreateManifestCommandOptions:
        """Parse options for the create-manifest command."""
        output = Path(args.output).resolve() if args.output else None
        return CreateManifestCommandOptions(
            output=output,
            global_opts=opts,
        )

    def _configure_parser(self, subparser: argparse._SubParsersAction):  # type: ignore
        """Configure the parser for the create-manifest command."""
        self._parser = subparser.add_parser(  # type: ignore[reportUnknownMemberType]
            "create-manifest",
            help="Create a release manifest.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--output",
            "-o",
            metavar="FILE",
            default=None,
            help="Output file where release manifest will be written.",
        )

    def _create_service(
        self, options: CreateManifestCommandOptions
    ) -> ManifestGenerator:
        """Create the service used to generate the manifest."""
        global_opts = options.global_opts
        # Create the service dependencies
        writer = global_opts.get_writer(
            self._create_writer(options),
        )
        git_reader = global_opts.get_reader(
            GitSubprocessReader(),
        )
        strategy_reader = global_opts.get_strategy_reader(
            AutoStrategyReader(Path.cwd()),
        )
        version_reader = global_opts.get_version_reader(
            AutoVersionReader(Path.cwd()),
        )
        # Create the service
        service = ManifestGenerator(
            git_reader=git_reader,
            manifest_writer=writer,
            strategy_reader=strategy_reader,
            version_reader=version_reader,
        )
        return service

    def _create_writer(self, options: CreateManifestCommandOptions) -> JsonWriter:
        if options.output is None:
            if options.global_opts.debug:
                print("💡 Writing output to stdout 💡")
            return JsonStdoutWriter()
        else:
            if options.global_opts.debug:
                print(f"💡 Writing output to {options.output.as_posix()} 💡")
            return JsonFileWriter(options.output)
