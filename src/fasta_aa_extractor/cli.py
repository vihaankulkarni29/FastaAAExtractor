"""Command-line interface for FastaAAExtractor."""

import argparse
import json
import logging
import sys
import zipfile
from pathlib import Path
from typing import Optional

from .core import run_extraction, validate_inputs, run_parallel_extraction


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
        "--genome", help="Path to genome FASTA file (.fasta or .fa)"
    )
    parser.add_argument(
        "--coords",
        help="Path to coordinate file (.tsv, .tab, .csv, .xlsx)",
    )
    parser.add_argument("--isolate", help="Isolate name (e.g., ECS34)")
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
    parser.add_argument(
        "--log-json",
        action="store_true",
        help="Emit logs in JSON format (structured logging)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and columns without extracting or writing outputs",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bar during extraction (requires tqdm)",
    )
    parser.add_argument(
        "--combined-fasta",
        help="Write a combined FASTA file with all extracted proteins",
    )
    parser.add_argument(
        "--summary-csv",
        help="Write a CSV summary table of all extracted proteins",
    )
    parser.add_argument(
        "--genes",
        help="Filter to a list of genes (comma-separated) or @path/to/file with one gene per line",
    )
    parser.add_argument(
        "--batch",
        help="Process multiple jobs from a CSV/TSV with columns: genome,coords,isolate",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable parallel processing (gene-by-gene across all genomes)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)",
    )

    args = parser.parse_args()

    # Optional JSON logging formatter
    if args.log_json:
        fmt = "{\"level\": \"%(levelname)s\", \"msg\": \"%(message)s\"}"
        logging.basicConfig(level=logging.INFO, format=fmt)
    else:
        setup_logging(args.verbose, args.quiet, args.log_file)

    try:
        # Batch mode
        if args.batch:
            return run_batch(args)

        # Validate input files exist
        if not Path(args.genome).exists():
            logging.error(f"Genome file not found: {args.genome}")
            return EXIT_FILE_NOT_FOUND

        if not Path(args.coords).exists():
            logging.error(f"Coordinate file not found: {args.coords}")
            return EXIT_FILE_NOT_FOUND

        # Dry-run validation
        if args.dry_run:
            if not args.genome or not args.coords:
                logging.error("--dry-run requires --genome and --coords")
                return EXIT_INVALID_INPUT
            summary = validate_inputs(args.genome, args.coords)
            # Help static type checkers understand the shape
            issues = summary.get("issues") or []
            if not isinstance(issues, list):
                issues = [str(issues)]
            status = "ok" if summary.get("ok") else "issues"
            if not args.quiet:
                print(f"Validation: {status}")
                if issues:
                    for msg in issues:
                        print(f" - {msg}")
            if args.json_output:
                save_json_result(args, None, 0, "validation", json.dumps(summary))
            return EXIT_SUCCESS if summary.get("ok") else EXIT_INVALID_INPUT

        # Non-batch extraction requires all three
        if not args.genome or not args.coords or not args.isolate:
            logging.error("Missing required arguments: --genome, --coords, --isolate")
            return EXIT_INVALID_INPUT

        # Check files now that args are present
        if not Path(args.genome).exists():
            logging.error(f"Genome file not found: {args.genome}")
            return EXIT_FILE_NOT_FOUND

        if not Path(args.coords).exists():
            logging.error(f"Coordinate file not found: {args.coords}")
            return EXIT_FILE_NOT_FOUND

        # Parse genes filter
        gene_filter = None
        if args.genes:
            if args.genes.startswith("@"):
                list_path = Path(args.genes[1:])
                if not list_path.exists():
                    logging.error(f"Gene list file not found: {list_path}")
                    return EXIT_FILE_NOT_FOUND
                gene_filter = [
                    line.strip()
                    for line in list_path.read_text().splitlines()
                    if line.strip()
                ]
            else:
                gene_filter = [g.strip() for g in args.genes.split(",") if g.strip()]

        # Parallel mode: only works with --genes and single genome currently
        if args.parallel and gene_filter:
            if not args.quiet:
                print(
                    f"Running parallel extraction for {len(gene_filter)} genes "
                    f"with {args.max_workers} workers..."
                )

            stats = run_parallel_extraction(
                gene_list=gene_filter,
                genome_files=[args.genome],
                coord_files=[args.coords],
                isolate_names=[args.isolate],
                output_dir=args.output_dir,
                max_workers=args.max_workers,
                show_progress=args.progress,
                combined_fasta=args.combined_fasta,
                summary_csv=args.summary_csv,
            )

            protein_count = stats.get("total_extracted", 0)
            if isinstance(protein_count, int):
                pass  # Already int
            else:
                protein_count = 0

            if not args.quiet:
                print(f"✓ Extracted {protein_count} protein(s) in parallel mode")
                print(f"  Output directory: {args.output_dir}")
                if args.combined_fasta:
                    print(f"  Combined FASTA: {args.combined_fasta}")
                if args.summary_csv:
                    print(f"  Summary CSV: {args.summary_csv}")

            if args.json_output:
                with open(args.json_output, "w") as f:
                    json.dump(stats, f, indent=2)

            return EXIT_SUCCESS if protein_count > 0 else EXIT_NO_PROTEINS_EXTRACTED

        # Standard sequential extraction
        zip_path = run_extraction(
            args.genome,
            args.coords,
            args.isolate,
            args.output_dir,
            args.progress,
            combined_fasta=args.combined_fasta,
            summary_csv=args.summary_csv,
            gene_filter=gene_filter,
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


def run_batch(args) -> int:
    """Run batch mode from a CSV/TSV file with genome,coords,isolate columns."""
    import pandas as pd
    jobs_file = Path(args.batch)
    if not jobs_file.exists():
        logging.error(f"Batch file not found: {jobs_file}")
        return EXIT_FILE_NOT_FOUND

    # Auto delimiter detection: try tab first then comma
    try:
        df = (
            pd.read_csv(jobs_file, sep="\t")
            if "\t" in jobs_file.read_text()
            else pd.read_csv(jobs_file)
        )
    except Exception as e:
        logging.error(f"Failed to read batch file: {e}")
        return EXIT_INVALID_INPUT

    required = {"genome", "coords", "isolate"}
    missing = required - set(map(str.lower, df.columns))
    if missing:
        logging.error(f"Batch file missing columns: {', '.join(sorted(missing))}")
        return EXIT_INVALID_INPUT

    successes = 0
    failures = 0
    details = []

    for _, row in df.iterrows():
        genome = row[[c for c in df.columns if c.lower() == "genome"][0]]
        coords = row[[c for c in df.columns if c.lower() == "coords"][0]]
        isolate = row[[c for c in df.columns if c.lower() == "isolate"][0]]

        try:
            zip_path = run_extraction(
                str(genome), str(coords), str(isolate), args.output_dir, args.progress
            )
            with zipfile.ZipFile(zip_path, "r") as zf:
                protein_count = len(zf.namelist())
            successes += 1
            details.append(
                {
                    "isolate": isolate,
                    "status": "success",
                    "proteins_extracted": protein_count,
                    "zip_path": zip_path,
                }
            )
        except Exception as e:
            failures += 1
            details.append({"isolate": isolate, "status": "error", "error": str(e)})

    if args.json_output:
        summary = {
            "status": "batch",
            "successes": successes,
            "failures": failures,
            "details": details,
        }
        with open(args.json_output, "w") as f:
            json.dump(summary, f, indent=2)

    if not args.quiet:
        print(f"Batch complete: {successes} success, {failures} failed")

    return EXIT_SUCCESS if failures == 0 else EXIT_GENERAL_ERROR


if __name__ == "__main__":
    sys.exit(main())
