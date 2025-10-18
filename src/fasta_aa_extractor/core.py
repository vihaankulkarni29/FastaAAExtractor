"""Core functionality for FastAAExtractor."""

import os
import shutil
import zipfile
import logging
from typing import Dict, List, Optional, cast

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import pandas as pd


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


def extract_proteins(
    genome: Dict[str, SeqRecord],
    coords_df: pd.DataFrame,
    isolate_name: str,
    output_dir: str = ".",
) -> str:
    """Extract amino acid sequences and return zip path."""
    extracted_dir = os.path.join(output_dir, "Extracted_Proteins")
    if os.path.exists(extracted_dir):
        shutil.rmtree(extracted_dir)
    os.makedirs(extracted_dir)

    seen_counts: Dict[str, int] = {}

    for idx, row in coords_df.iterrows():
        gene = row["gene"]
        start = int(row["start"])
        end = int(row["end"])
        strand = row["strand"]

        # Determine which sequence to use
        dna_seq_opt: Optional[Seq] = None
        if 'sequence' in row and row['sequence'] in genome:
            seqid = row['sequence']
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
        logging.info(f"Extracted: {filename}")

    # Create zip
    zip_path = os.path.join(output_dir, "Extracted_Proteins.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in os.listdir(extracted_dir):
            zipf.write(os.path.join(extracted_dir, file), arcname=file)

        logging.info(f"Extraction complete. Results saved to {zip_path}")
    return zip_path


def run_extraction(
    genome_file: str, coord_file: str, isolate_name: str, output_dir: str = "."
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

    return extract_proteins(genome, coords_df, isolate_name, output_dir)
