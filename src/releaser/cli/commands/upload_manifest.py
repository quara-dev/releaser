"""Create a release manifest."""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from releaser.adapters import (
    GitSubprocessReader,
    HttpsWebhookClient,
    InMemoryJsonWriter,
    JsonFileWriter,
    MagicStrategyReader,
    MagicVersionReader,
)
from releaser.hexagon.entities import artefact
from releaser.hexagon.services.manifest_generator import ManifestGenerator
from releaser.hexagon.services.manifest_notifier import ManifestNotifier

from ..context import GlobalOpts


@dataclass
class UploadManifestCommandOptions:
    """Options for the create-manifest command."""

    manifest: Path | None
    webhook_url: str
    global_opts: GlobalOpts


class UploadManifestCommand:
    def __init__(self, subparser: argparse._SubParsersAction):  # type: ignore
        self.configure_parser(subparser)  # type: ignore[no-untyped-call]

    def run(self, opts: UploadManifestCommandOptions) -> int:
        """Run the upload-manifest command."""
        service = self.create_service(opts)
        service.execute()
        return 0

    def configure_parser(self, subparser: argparse._SubParsersAction):  # type: ignore
        """Configure the parser for the create-manifest command."""
        self._parser = subparser.add_parser(  # type: ignore[reportUnknownMemberType]
            "upload-manifest",
            help="Upload a release manifest.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--input",
            "-i",
            metavar="FILE",
            help="Input file where release manifest will be read.",
        )
        self._parser.add_argument(  # type: ignore[reportUnknownMemberType]
            "--webhook-url",
            "-w",
            metavar="URL",
            help="Webhook URL to notify.",
        )

    def parse_opts(
        self, args: argparse.Namespace, opts: GlobalOpts
    ) -> UploadManifestCommandOptions:
        """Parse options for the create-manifest command."""
        options = UploadManifestCommandOptions(
            manifest=Path(args.input) if args.input else None,
            webhook_url=args.webhook_url,
            global_opts=opts,
        )
        return options

    def create_service(self, options: UploadManifestCommandOptions) -> ManifestNotifier:
        """Create the service used to upload the manifest."""
        manifest = self._create_manifest(options)
        if not manifest:
            print("ERROR: No manifest found.", file=sys.stderr)
            sys.exit(1)
        service = ManifestNotifier(
            manifest=manifest,
            webhook_url=options.webhook_url,
            webhook_client=options.global_opts.get_webhook_client(HttpsWebhookClient()),
        )
        return service

    def _create_manifest(
        self, options: UploadManifestCommandOptions
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
                MagicStrategyReader(Path.cwd()),
            )
            version_reader = global_opts.get_version_reader(
                MagicVersionReader(Path.cwd()),
            )
            internal_service = ManifestGenerator(
                git_reader=git_reader,
                manifest_writer=writer,
                strategy_reader=strategy_reader,
                version_reader=version_reader,
            )
            internal_service.execute()
            return writer.read_manifest()
