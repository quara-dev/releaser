from __future__ import annotations

import argparse
import sys

from releaser.__about__ import __version__
from releaser.cli.commands.upload_manifest import UploadManifestCommand
from releaser.cli.context import GlobalOpts

from . import testing
from .commands.analyze_manifest import AnalyzeManifestCommand
from .commands.create_manifest import CreateManifestCommand


def main() -> None:
    """Entry point for the application."""
    app = Application()
    sys.exit(app.execute())


class Application:
    """A command line application written using argparse.

    This class is responsible for parsing command line arguments and
    executing the appropriate command.
    """

    def __init__(
        self, testing_dependencies: testing.Dependencies | None = None
    ) -> None:
        """Initialize the application.

        When testing_dependencies is provided, the application commands
        will use them instead of creating new ones.
        """

        self.testing_dependencies = testing_dependencies
        self.parser = argparse.ArgumentParser(
            prog="releaser",
            description="A tool for creating release manifests.",
        )

        self.parser.add_argument(
            "--version",
            action="version",
            version=__version__,
        )

        self.parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug output.",
        )

        subparsers = self.parser.add_subparsers(dest="command")

        self.create_manifest = CreateManifestCommand(subparsers)
        self.analyze_manifest = AnalyzeManifestCommand(subparsers)
        self.upload_manifest = UploadManifestCommand(subparsers)

    def execute(self, command_line_args: list[str] | None = None) -> int:
        """Execute the application.

        When command_line_args is provided, it will be used instead of
        sys.argv. This is useful for testing.
        """
        args = self.parser.parse_args(command_line_args)
        command: str | None = args.command
        global_opts = GlobalOpts(
            debug=args.debug, _testing_dependencies=self.testing_dependencies
        )
        if command == "create-manifest":
            opts = self.create_manifest.parse_opts(args, global_opts)
            return self.create_manifest.run(opts)
        elif command == "analyze-manifest":
            opts = self.analyze_manifest.parse_opts(args, global_opts)
            return self.analyze_manifest.run(opts)
        elif command == "upload-manifest":
            opts = self.upload_manifest.parse_opts(args, global_opts)
            return self.upload_manifest.run(opts)
        elif command:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
        else:
            self.parser.print_help()
            return 0
