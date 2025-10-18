"""Command-line interface for FastaAAExtractor."""

import argparse
import json
import logging
import sys
import zipfile
from pathlib import Path
from typing import Optional

from .core import run_extraction


# Exit codes for automation
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_FILE_NOT_FOUND = 2
EXIT_INVALID_INPUT = 3
EXIT_NO_PROTEINS_EXTRACTED = 4


def setup_logging(verbose: bool = False, quiet: bool = False, log_file: Optional[str] = None):
    """Set up logging configuration."""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    if log_file:
        logging.basicConfig(
            level=level,
            filename=log_file,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
    else:
        logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Extract amino acid sequences from bacterial genomes.",
        epilog="For detailed help, see QUICKSTART.md or visit: https://github.com/vihaankulkarni29/FastaAAExtractor",
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
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress all output except errors (useful for pipelines)",
    )
    parser.add_argument(
        "--json", dest="json_output", help="Save results metadata as JSON file"
    )
    parser.add_argument("--log-file", help="Write logs to file instead of console")

    args = parser.parse_args()

    setup_logging(args.verbose, args.quiet, args.log_file)

    try:
        # Validate input files exist
        if not Path(args.genome).exists():
            logging.error(f"Genome file not found: {args.genome}")
            return EXIT_FILE_NOT_FOUND

        if not Path(args.coords).exists():
            logging.error(f"Coordinate file not found: {args.coords}")
            return EXIT_FILE_NOT_FOUND

        # Run extraction
        zip_path = run_extraction(
            args.genome, args.coords, args.isolate, args.output_dir
        )

        # Count extracted proteins
        with zipfile.ZipFile(zip_path, "r") as zf:
            protein_count = len(zf.namelist())

        # Check if any proteins were extracted
        if protein_count == 0:
            logging.warning("No proteins were extracted. Check your coordinates.")
            if args.json_output:
                save_json_result(
                    args, zip_path, protein_count, "warning", "No proteins extracted"
                )
            return EXIT_NO_PROTEINS_EXTRACTED

        # Success!
        if not args.quiet:
            print(f"✓ Success! Extracted {protein_count} protein(s)")
            print(f"  Output: {zip_path}")

        # Save JSON if requested
        if args.json_output:
            save_json_result(args, zip_path, protein_count, "success")

        return EXIT_SUCCESS

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        if args.json_output:
            save_json_result(args, None, 0, "error", str(e))
        return EXIT_FILE_NOT_FOUND

    except ValueError as e:
        logging.error(f"Invalid input: {e}")
        if args.json_output:
            save_json_result(args, None, 0, "error", str(e))
        return EXIT_INVALID_INPUT

    except Exception as e:
        logging.error(f"Extraction failed: {e}")
        if args.json_output:
            save_json_result(args, None, 0, "error", str(e))
        return EXIT_GENERAL_ERROR


def save_json_result(args, zip_path, protein_count, status, error=None):
    """Save extraction results as JSON for pipeline integration."""
    result = {
        "status": status,
        "isolate": args.isolate,
        "genome_file": args.genome,
        "coords_file": args.coords,
        "proteins_extracted": protein_count,
        "output_zip": zip_path,
    }

    if error:
        result["error"] = error

    with open(args.json_output, "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    sys.exit(main())
