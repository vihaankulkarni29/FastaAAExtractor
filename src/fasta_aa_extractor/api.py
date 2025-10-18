"""API module for programmatic access to FastaAAExtractor."""

import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

from .core import run_extraction


class FastaAAExtractor:
    """
    Python API for FastaAAExtractor.

    This class provides a programmatic interface for extracting amino acid
    sequences from bacterial genomes, suitable for integration into pipelines
    and automated workflows.

    Examples:
        Basic usage:
        >>> extractor = FastaAAExtractor()
        >>> result = extractor.extract(
        ...     genome="genome.fasta",
        ...     coords="genes.tsv",
        ...     isolate="Strain123"
        ... )
        >>> print(result['status'])  # 'success'
        >>> print(result['proteins_extracted'])  # 42

        With custom options:
        >>> extractor = FastaAAExtractor(output_dir="results/", quiet=True)
        >>> result = extractor.extract(
        ...     genome="genome.fasta",
        ...     coords="genes.tsv",
        ...     isolate="Strain123",
        ...     return_metadata=True
        ... )
        >>> print(result['metadata'])  # Detailed extraction info
    """

    def __init__(
        self, output_dir: str = ".", quiet: bool = False, log_file: Optional[str] = None
    ):
        """
        Initialize the FastaAAExtractor API.

        Args:
            output_dir: Directory for output files (default: current directory)
            quiet: Suppress console output (default: False)
            log_file: Path to log file (default: None, logs to console)
        """
        self.output_dir = output_dir
        self.quiet = quiet
        self.log_file = log_file

        # Configure logging
        if quiet:
            logging.basicConfig(level=logging.ERROR)
        elif log_file:
            logging.basicConfig(
                level=logging.INFO,
                filename=log_file,
                format="%(asctime)s - %(levelname)s - %(message)s",
            )

    def extract(
        self,
        genome: Union[str, Path],
        coords: Union[str, Path],
        isolate: str,
        return_metadata: bool = False,
        json_output: Optional[str] = None,
    ) -> Dict:
        """
        Extract amino acid sequences from a bacterial genome.

        Args:
            genome: Path to genome FASTA file
            coords: Path to coordinate table (TSV/CSV/Excel)
            isolate: Isolate/strain name
            return_metadata: Include detailed metadata in result (default: False)
            json_output: Path to save results as JSON (default: None)

        return {
            Dictionary containing:
                - status: 'success' or 'error'
            'genome_contigs': len(genome_dict),
            'total_genome_length': sum(len(str(rec.seq)) for rec in genome_dict.values()),
                - error: Error message (if status='error')
                - metadata: Detailed info (if return_metadata=True)

        Raises:
            FileNotFoundError: If genome or coords file doesn't exist
            ValueError: If file format is invalid
        """
        try:
            # Run extraction
            zip_path = run_extraction(
                str(genome), str(coords), isolate, self.output_dir
            )

            # Count extracted proteins
            import zipfile

            with zipfile.ZipFile(zip_path, "r") as zf:
                protein_count = len(zf.namelist())

            # Build result
            result = {
                "status": "success",
                "zip_path": zip_path,
                "proteins_extracted": protein_count,
                "isolate": isolate,
            }

            # Add metadata if requested
            if return_metadata:
                result["metadata"] = self._get_metadata(
                    genome, coords, isolate, zip_path
                )

            # Save as JSON if requested
            if json_output:
                self._save_json(result, json_output)

            if not self.quiet:
                logging.info(f"Successfully extracted {protein_count} proteins")

            return result

        except Exception as e:
            result = {"status": "error", "error": str(e), "isolate": isolate}

            if json_output:
                self._save_json(result, json_output)

            logging.error(f"Extraction failed: {e}")
            return result

    def batch_extract(
        self, jobs: List[Dict], continue_on_error: bool = True
    ) -> List[Dict]:
        """
        Extract proteins from multiple genomes in batch.

        Args:
            jobs: List of job dictionaries, each containing:
                - genome: Path to genome file
                - coords: Path to coordinate file
                - isolate: Isolate name
            continue_on_error: Continue if one job fails (default: True)

        Returns:
            List of result dictionaries (one per job)

        Example:
            >>> jobs = [
            ...     {'genome': 'strain1.fasta', 'coords': 'strain1.tsv', 'isolate': 'Strain1'},
            ...     {'genome': 'strain2.fasta', 'coords': 'strain2.tsv', 'isolate': 'Strain2'},
            ... ]
            >>> results = extractor.batch_extract(jobs)
            >>> successful = [r for r in results if r['status'] == 'success']
        """
        results = []

        for i, job in enumerate(jobs, 1):
            if not self.quiet:
                logging.info(f"Processing job {i}/{len(jobs)}: {job['isolate']}")

            try:
                result = self.extract(
                    genome=job["genome"], coords=job["coords"], isolate=job["isolate"]
                )
                results.append(result)

            except Exception as e:
                result = {"status": "error", "error": str(e), "isolate": job["isolate"]}
                results.append(result)

                if not continue_on_error:
                    raise

        # Summary
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful

        if not self.quiet:
            logging.info(f"Batch complete: {successful} successful, {failed} failed")

        return results

    def _get_metadata(
        self,
        genome: Union[str, Path],
        coords: Union[str, Path],
        isolate: str,
        zip_path: str,
    ) -> Dict:
        """Gather detailed metadata about the extraction."""
        import os
        from .core import load_genome, load_coordinates

        genome_dict = load_genome(str(genome))
        coords_df = load_coordinates(str(coords))

        return {
            "genome_file": str(genome),
            "coords_file": str(coords),
            "genome_contigs": len(genome_dict),
            "total_genome_length": sum(len(str(rec.seq)) for rec in genome_dict.values()),
            "genes_in_table": len(coords_df),
            "output_zip": zip_path,
            "output_size_bytes": os.path.getsize(zip_path),
        }

    def _save_json(self, data: Dict, filepath: str):
        """Save result data as JSON."""
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)


def extract_proteins(
    genome: str, coords: str, isolate: str, output_dir: str = ".", quiet: bool = False
) -> Dict:
    """
    Convenience function for single extraction.

    This is a simple wrapper around the FastaAAExtractor class for
    quick one-off extractions.

    Args:
        genome: Path to genome FASTA file
        coords: Path to coordinate table
        isolate: Isolate/strain name
        output_dir: Output directory (default: current directory)
        quiet: Suppress output (default: False)

    Returns:
        Result dictionary with status and output info

    Example:
        >>> result = extract_proteins(
        ...     genome="genome.fasta",
        ...     coords="genes.tsv",
        ...     isolate="MyStrain"
        ... )
        >>> if result['status'] == 'success':
        ...     print(f"Extracted {result['proteins_extracted']} proteins")
    """
    extractor = FastaAAExtractor(output_dir=output_dir, quiet=quiet)
    return extractor.extract(genome, coords, isolate)
