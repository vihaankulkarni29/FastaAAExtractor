"""Command-line interface for FastAAExtractor."""

import argparse
import logging
import sys

from .core import run_extraction


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract amino acid sequences from bacterial genomes."
    )
    parser.add_argument(
        "--genome", required=True, help="Path to genome FASTA file (.fasta or .fa)"
    )
    parser.add_argument(
        "--coords",
        required=True,
        help="Path to coordinate file (.tsv, .tab, .csv, .xlsx)",
    )
    parser.add_argument("--isolate", required=True, help="Isolate name (e.g., ECS34)")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    setup_logging(args.verbose)

    try:
        zip_path = run_extraction(
            args.genome, args.coords, args.isolate, args.output_dir
        )
        print(f"Success! Results saved to: {zip_path}")
        return 0
    except Exception as e:
        logging.error(f"Extraction failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
