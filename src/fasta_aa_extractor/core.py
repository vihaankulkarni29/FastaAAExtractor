"""Core functionality for FastAAExtractor."""

import os
import shutil
import zipfile
import logging
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import pandas as pd

try:
    from tqdm import tqdm  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    tqdm = None


def load_genome(genome_file: str) -> Dict[str, SeqRecord]:
    """Load genome FASTA file."""
    try:
        genome = SeqIO.to_dict(SeqIO.parse(genome_file, "fasta"))
        logging.info(f"Loaded genome with {len(genome)} sequences")
        return genome
    except Exception as e:
        raise ValueError(f"Error loading genome: {e}")


def load_coordinates(coord_file: str) -> pd.DataFrame:
    """Load coordinate table."""
    try:
        if coord_file.endswith((".tsv", ".tab")):
            df = pd.read_csv(coord_file, sep="\t")
        elif coord_file.endswith(".csv"):
            df = pd.read_csv(coord_file)
        elif coord_file.endswith(".xlsx"):
            df = pd.read_excel(coord_file)
        else:
            raise ValueError(
                "Unsupported coordinate file format. Use .tsv, .tab, .csv, or .xlsx"
            )
        logging.info(f"Loaded coordinates with {len(df)} entries")
        return df
    except Exception as e:
        raise ValueError(f"Error loading coordinates: {e}")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column headers."""
    df.columns = df.columns.str.strip().str.lower()
    return df


def find_column(possible_names: List[str], columns: pd.Index) -> Optional[str]:
    """Find column name from possible synonyms."""
    for synonym in possible_names:
        for col in columns:
            if synonym in col:
                return col
    return None


def detect_required_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Detect required columns with flexible naming."""
    synonyms = {
        "gene": ["gene", "product", "aro term", "gene name"],
        "start": ["start", "begin", "from", "coordinates"],
        "end": ["end", "stop", "to", "coordinates"],
        "strand": ["strand", "orientation"],
        "sequence": ["sequence", "contig", "seqid"],
    }

    actual_cols = {}
    for key, options in synonyms.items():
        found = find_column(options, df.columns)
        if found:
            actual_cols[key] = found
        elif key in ["gene", "start", "end", "strand"]:  # Required
            raise ValueError(f"Missing required column for '{key}'. Tried: {options}")

    return actual_cols


def extract_single_gene_from_genome(
    genome_file: str,
    coord_file: str,
    gene_name: str,
    isolate_name: str,
) -> Optional[Tuple[str, str, str, Dict]]:
    """
    Extract a single gene from a single genome (worker function for parallel processing).

    Uses lazy loading with SeqIO.index() to minimize memory usage.

    Returns:
        Tuple of (gene_name, isolate_name, protein_sequence, metadata_dict) or None if failed
    """
    try:
        # Lazy load genome (memory efficient)
        genome = SeqIO.index(genome_file, "fasta")

        # Load and normalize coordinates
        coords_df = load_coordinates(coord_file)
        coords_df = normalize_columns(coords_df)
        actual_cols = detect_required_columns(coords_df)

        # Filter for this specific gene (case-insensitive)
        gene_col = actual_cols["gene"]
        gene_rows = coords_df[
            coords_df[gene_col].astype(str).str.lower() == gene_name.lower()
        ]

        if gene_rows.empty:
            logging.warning(
                f"Gene '{gene_name}' not found in {coord_file} for {isolate_name}"
            )
            return None

        # Take first match if duplicates
        row = gene_rows.iloc[0]
        start = int(row[actual_cols["start"]])
        end = int(row[actual_cols["end"]])
        strand = row[actual_cols["strand"]]

        # Determine which sequence/contig to use
        if "sequence" in actual_cols and actual_cols["sequence"] in row:
            seq_id = row[actual_cols["sequence"]]
            if seq_id not in genome:
                logging.error(
                    f"Sequence '{seq_id}' not found in {genome_file} for {isolate_name}"
                )
                return None
        else:
            # Use first sequence that fits coordinates
            seq_id = None
            for sid in genome.keys():
                seq_rec = genome[sid]
                if seq_rec and seq_rec.seq:
                    seq_len = len(str(seq_rec.seq))
                    if start - 1 < seq_len and end <= seq_len:
                        seq_id = sid
                        break
            if not seq_id:
                logging.error(
                    f"No sequence fits coordinates {start}-{end} in {genome_file}"
                )
                return None

        # Extract DNA sequence
        seq_record = genome[seq_id]
        if not seq_record or not seq_record.seq:
            logging.error(f"Invalid sequence record for {seq_id}")
            return None
        dna_seq = Seq(str(seq_record.seq)[start - 1 : end])

        # Handle reverse strand
        if strand == "-":
            dna_seq = dna_seq.reverse_complement()

        # Translate to protein
        protein_seq = str(dna_seq.translate(to_stop=True))

        # Build metadata
        metadata = {
            "start": start,
            "end": end,
            "strand": strand,
            "length_aa": len(protein_seq),
            "contig": seq_id,
        }

        genome.close()  # Clean up file handle
        return (gene_name, isolate_name, protein_seq, metadata)

    except Exception as e:
        logging.error(f"Failed to extract {gene_name} from {isolate_name}: {e}")
        return None


def extract_gene_across_genomes(
    gene_name: str,
    genome_files: List[str],
    coord_files: List[str],
    isolate_names: List[str],
    max_workers: int = 4,
    show_progress: bool = False,
) -> List[Tuple[str, str, str, Dict]]:
    """
    Extract one gene from multiple genomes in parallel.

    Args:
        gene_name: Name of the gene to extract
        genome_files: List of genome FASTA file paths
        coord_files: List of coordinate file paths (matching genomes)
        isolate_names: List of isolate names (matching genomes)
        max_workers: Number of parallel workers
        show_progress: Show progress bar

    Returns:
        List of successful extraction results
    """
    results = []
    jobs = list(zip(genome_files, coord_files, isolate_names))

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        futures = {
            executor.submit(
                extract_single_gene_from_genome, gfile, cfile, gene_name, iso
            ): (gfile, iso)
            for gfile, cfile, iso in jobs
        }

        # Collect results with optional progress bar
        iterator = as_completed(futures)
        if show_progress and tqdm is not None:
            iterator = tqdm(
                iterator,
                total=len(futures),
                desc=f"Extracting {gene_name}",
                unit="genome",
            )

        for future in iterator:
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                gfile, iso = futures[future]
                logging.error(f"Worker crashed for {iso}: {e}")

    return results


def extract_proteins(
    genome: Dict[str, SeqRecord],
    coords_df: pd.DataFrame,
    isolate_name: str,
    output_dir: str = ".",
    show_progress: bool = False,
    combined_fasta: Optional[str] = None,
    summary_csv: Optional[str] = None,
    gene_filter: Optional[List[str]] = None,
) -> str:
    """Extract amino acid sequences and return zip path."""
    extracted_dir = os.path.join(output_dir, "Extracted_Proteins")
    if os.path.exists(extracted_dir):
        shutil.rmtree(extracted_dir)
    os.makedirs(extracted_dir)

    seen_counts: Dict[str, int] = {}
    combined_records: List[SeqRecord] = []
    summary_rows: List[Dict[str, object]] = []

    iterator = coords_df.iterrows()
    enumerator = enumerate(iterator)
    if show_progress and tqdm is not None:
        iterator = tqdm(iterator, total=len(coords_df), desc="Extracting", unit="gene")

    for i, item in enumerator:
        idx, row = item
        # Optional filtering by gene list (case-insensitive)
        if gene_filter is not None:
            gname = str(row["gene"]).lower()
            if gname not in {g.lower() for g in gene_filter}:
                continue
        gene = row["gene"]
        start = int(row["start"])
        end = int(row["end"])
        strand = row["strand"]

        # Determine which sequence to use
        dna_seq_opt: Optional[Seq] = None
        if "sequence" in row and row["sequence"] in genome:
            seqid = row["sequence"]
            # Ensure Seq type for mypy and safety
            seq_obj = genome[seqid].seq
            dna_seq_opt = Seq(str(seq_obj))[start - 1 : end]
        else:
            # Find any sequence that fits
            for seqid in genome:
                seq_obj = genome[seqid].seq
                seq_len = len(str(seq_obj))
                if start - 1 < seq_len and end <= seq_len:
                    dna_seq_opt = Seq(str(seq_obj))[start - 1 : end]
                    break
            if dna_seq_opt is None:
                logging.warning(
                    f"Coordinates {start}-{end} out of range for gene {gene}. Skipping."
                )
                continue

        assert dna_seq_opt is not None
        dna_seq: Seq = dna_seq_opt

        if strand == "-":
            dna_seq = dna_seq.reverse_complement()
        aa_seq = dna_seq.translate(to_stop=True)

        count = seen_counts.get(gene.lower(), 0) + 1
        seen_counts[gene.lower()] = count
        suffix = f"_{count}" if count > 1 else ""

        filename = f"{gene}{suffix}_{isolate_name}.faa"
        record = SeqRecord(aa_seq, id=gene, description=f"{gene}{suffix}")
        SeqIO.write(record, os.path.join(extracted_dir, filename), "fasta")
        combined_records.append(
            SeqRecord(aa_seq, id=f"{gene}{suffix}_{isolate_name}", description="")
        )
        summary_rows.append(
            {
                "gene": gene,
                "index": i,
                "start": start,
                "end": end,
                "strand": strand,
                "length_aa": len(str(aa_seq)),
                "file": filename,
            }
        )
        logging.info(f"Extracted: {filename}")

    # Create zip
    zip_path = os.path.join(output_dir, "Extracted_Proteins.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in os.listdir(extracted_dir):
            zipf.write(os.path.join(extracted_dir, file), arcname=file)

        logging.info(f"Extraction complete. Results saved to {zip_path}")
    # Write optional combined FASTA
    if combined_fasta and combined_records:
        SeqIO.write(combined_records, combined_fasta, "fasta")

    # Write optional CSV summary
    if summary_csv and summary_rows:
        pd.DataFrame(summary_rows).to_csv(summary_csv, index=False)

    return zip_path


def run_extraction(
    genome_file: str,
    coord_file: str,
    isolate_name: str,
    output_dir: str = ".",
    show_progress: bool = False,
    combined_fasta: Optional[str] = None,
    summary_csv: Optional[str] = None,
    gene_filter: Optional[List[str]] = None,
) -> str:
    """Main extraction workflow."""
    # Validate inputs
    if not os.path.isfile(genome_file):
        raise FileNotFoundError(f"Genome file '{genome_file}' not found.")
    if not os.path.isfile(coord_file):
        raise FileNotFoundError(f"Coordinate file '{coord_file}' not found.")

    genome = load_genome(genome_file)
    df = load_coordinates(coord_file)
    df = normalize_columns(df)

    actual_cols = detect_required_columns(df)
    coords_df = df.rename(columns={actual_cols[k]: k for k in actual_cols})[
        ["gene", "start", "end", "strand"]
    ]

    if "sequence" in actual_cols:
        coords_df["sequence"] = df[actual_cols["sequence"]]

    return extract_proteins(
        genome,
        coords_df,
        isolate_name,
        output_dir,
        show_progress,
        combined_fasta=combined_fasta,
        summary_csv=summary_csv,
        gene_filter=gene_filter,
    )


def validate_inputs(genome_file: str, coord_file: str) -> Dict[str, object]:
    """Validate inputs and return a summary dict.

    Performs fast checks: file existence, readable formats, column detection,
    and basic coordinate sanity (start<=end, positive integers).
    """
    if not os.path.isfile(genome_file):
        raise FileNotFoundError(f"Genome file '{genome_file}' not found.")
    if not os.path.isfile(coord_file):
        raise FileNotFoundError(f"Coordinate file '{coord_file}' not found.")

    genome = load_genome(genome_file)
    df = load_coordinates(coord_file)
    df_norm = normalize_columns(df)
    cols = detect_required_columns(df_norm)

    # Basic coordinate sanity
    issues: List[str] = []
    bad_types = df_norm[
        (~df_norm[cols["start"]].apply(lambda x: str(x).isdigit()))
        | (~df_norm[cols["end"]].apply(lambda x: str(x).isdigit()))
    ]
    if not bad_types.empty:
        issues.append(f"Non-integer coordinates in {len(bad_types)} row(s)")

    bad_order = df_norm[df_norm[cols["start"]] > df_norm[cols["end"]]]
    if not bad_order.empty:
        issues.append(f"Start > End in {len(bad_order)} row(s)")

    # Optional range check if sequence/contig provided
    out_of_range = 0
    if "sequence" in cols:
        seq_col = cols["sequence"]
        for _, r in df_norm.iterrows():
            try:
                s = int(r[cols["start"]])
                e = int(r[cols["end"]])
            except Exception:
                continue
            seqid = r.get(seq_col)
            if isinstance(seqid, str) and seqid in genome:
                seqlen = len(str(genome[seqid].seq))
                if not (1 <= s <= seqlen and 1 <= e <= seqlen):
                    out_of_range += 1
    if out_of_range:
        issues.append(f"Coordinates out of range in {out_of_range} row(s)")

    return {
        "genome_sequences": len(genome),
        "contig_names": list(genome.keys())[:10],
        "coords_rows": int(len(df)),
        "detected_columns": cols,
        "issues": issues,
        "ok": len(issues) == 0,
    }


def run_parallel_extraction(
    gene_list: List[str],
    genome_files: List[str],
    coord_files: List[str],
    isolate_names: List[str],
    output_dir: str,
    max_workers: int = 4,
    show_progress: bool = False,
    combined_fasta: Optional[str] = None,
    summary_csv: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run parallel extraction: one gene at a time across all genomes.

    Args:
        gene_list: List of gene names to extract
        genome_files: List of genome FASTA paths
        coord_files: List of coordinate file paths (matching genomes)
        isolate_names: List of isolate names (matching genomes)
        output_dir: Output directory for results
        max_workers: Number of parallel workers
        show_progress: Show progress bars
        combined_fasta: Optional path for combined FASTA output
        summary_csv: Optional path for summary CSV

    Returns:
        Summary dictionary with extraction statistics
    """
    all_results = []
    gene_stats = {}

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Process one gene at a time across all genomes
    for gene_name in gene_list:
        logging.info(f"Processing gene: {gene_name}")

        # Extract this gene from all genomes in parallel
        gene_results = extract_gene_across_genomes(
            gene_name,
            genome_files,
            coord_files,
            isolate_names,
            max_workers,
            show_progress,
        )

        # Write gene-specific directory
        gene_dir = output_path / gene_name
        gene_dir.mkdir(parents=True, exist_ok=True)

        # Write individual FAA files
        gene_combined_records = []
        for gene, isolate, protein, meta in gene_results:
            faa_file = gene_dir / f"{isolate}_{gene}.faa"
            with open(faa_file, "w") as f:
                f.write(f">{isolate}_{gene}\n{protein}\n")

            gene_combined_records.append(
                SeqRecord(
                    Seq(protein),
                    id=f"{isolate}_{gene}",
                    description=f"start={meta['start']} end={meta['end']} strand={meta['strand']}",
                )
            )

        # Write gene-specific combined FASTA
        if gene_combined_records:
            gene_combined_faa = gene_dir / f"{gene_name}_all.faa"
            SeqIO.write(gene_combined_records, gene_combined_faa, "fasta")

        gene_stats[gene_name] = {
            "extracted": len(gene_results),
            "total_genomes": len(genome_files),
            "success_rate": (
                len(gene_results) / len(genome_files) if genome_files else 0
            ),
        }

        all_results.extend(gene_results)

    # Write global combined FASTA if requested
    if combined_fasta and all_results:
        all_records = [
            SeqRecord(Seq(protein), id=f"{isolate}_{gene}", description="")
            for gene, isolate, protein, meta in all_results
        ]
        SeqIO.write(all_records, combined_fasta, "fasta")

    # Write summary CSV if requested
    if summary_csv and all_results:
        summary_data = [
            {
                "gene": gene,
                "isolate": isolate,
                "length_aa": meta["length_aa"],
                "start": meta["start"],
                "end": meta["end"],
                "strand": meta["strand"],
                "contig": meta["contig"],
            }
            for gene, isolate, protein, meta in all_results
        ]
        pd.DataFrame(summary_data).to_csv(summary_csv, index=False)

    return {
        "total_extracted": len(all_results),
        "genes_processed": len(gene_list),
        "genomes_processed": len(genome_files),
        "gene_stats": gene_stats,
    }
