"""Standardized CLI argument parsing for all skill scripts.

Provides a consistent interface for skill scripts to parse arguments,
with standard flags and help text generation.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence  # noqa: TC003 (stdlib stable)


def create_base_parser(
    description: str,
    *,
    add_input: bool = False,
    add_output: bool = False,
    add_data: bool = False,
    add_config: bool = False,
) -> argparse.ArgumentParser:
    """Create a base argument parser with standard flags.

    Args:
        description: Script description for --help.
        add_input: Add --input argument for input file.
        add_output: Add --output argument for output file.
        add_data: Add --data argument for data file.
        add_config: Add --config argument for config file.

    Returns:
        Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    if add_input:
        parser.add_argument("input", nargs="?", help="Input file path")
    if add_output:
        parser.add_argument("output", nargs="?", help="Output file path")
    if add_data:
        parser.add_argument("--data", "-d", help="Data file path (JSON)")
    if add_config:
        parser.add_argument("--config", "-c", help="Configuration file path")
    return parser


def parse_args(argv: Sequence[str] | None = None, **kwargs: bool) -> argparse.Namespace:
    """Parse command-line arguments with standard configuration.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).
        **kwargs: Passed to create_base_parser.

    Returns:
        Parsed arguments namespace.
    """
    parser = create_base_parser(**kwargs)
    return parser.parse_args(argv)
