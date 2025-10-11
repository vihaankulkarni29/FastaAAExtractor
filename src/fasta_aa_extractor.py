#!/usr/bin/env python3
"""
FastAAExtractor - Extract amino acid sequences from bacterial genomes using coordinate tables.

Usage:
    python fasta_aa_extractor.py --genome <fasta_file> --coords <coord_file> --isolate <name> [--output-dir <dir>]

Author: Your Name
"""

import argparse
import os
import sys
import zipfile
import shutil
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description="Extract amino acid sequences from bacterial genomes.")
    parser.add_argument('--genome', required=True, help='Path to genome FASTA file (.fasta or .fa)')
    parser.add_argument('--coords', required=True, help='Path to coordinate file (.tsv, .tab, .csv, .xlsx)')
    parser.add_argument('--isolate', required=True, help='Isolate name (e.g., ECS34)')
    parser.add_argument('--output-dir', default='.', help='Output directory (default: current directory)')

    args = parser.parse_args()

    genome_file = args.genome
    coord_file = args.coords
    isolate_name = args.isolate
    output_dir = args.output_dir

    # Validate inputs
    if not os.path.isfile(genome_file):
        print(f"Error: Genome file '{genome_file}' not found.")
        sys.exit(1)
    if not os.path.isfile(coord_file):
        print(f"Error: Coordinate file '{coord_file}' not found.")
        sys.exit(1)

    # Create output directory if it doesn't exist
    extracted_dir = os.path.join(output_dir, "Extracted_Proteins")
    if os.path.exists(extracted_dir):
        shutil.rmtree(extracted_dir)
    os.makedirs(extracted_dir)

    print("Loading genome FASTA...")
    try:
        genome = SeqIO.to_dict(SeqIO.parse(genome_file, "fasta"))
    except Exception as e:
        print(f"Error loading genome: {e}")
        sys.exit(1)

    print("Loading coordinate table...")
    try:
        if coord_file.endswith((".tsv", ".tab")):
            df = pd.read_csv(coord_file, sep="\t")
        elif coord_file.endswith(".csv"):
            df = pd.read_csv(coord_file)
        elif coord_file.endswith(".xlsx"):
            df = pd.read_excel(coord_file)
        else:
            print("Error: Unsupported coordinate file format. Use .tsv, .tab, .csv, or .xlsx")
            sys.exit(1)
    except Exception as e:
        print(f"Error loading coordinates: {e}")
        sys.exit(1)

    # Normalize column headers
    df.columns = df.columns.str.strip().str.lower()

    # Flexible column name mapping
    synonyms = {
        'gene': ['gene', 'product', 'aro term', 'gene name'],
        'start': ['start', 'begin', 'from', 'coordinates'],
        'end': ['end', 'stop', 'to', 'coordinates'],
        'strand': ['strand', 'orientation'],
        'sequence': ['sequence', 'contig', 'seqid']  # Added for contig
    }

    def find_column(possible_names, columns):
        for synonym in possible_names:
            for col in columns:
                if synonym in col:
                    return col
        return None

    # Detect required columns
    actual_cols = {}
    for key, options in synonyms.items():
        found = find_column(options, df.columns)
        if found:
            actual_cols[key] = found
        else:
            if key in ['gene', 'start', 'end', 'strand']:  # Required
                print(f"Error: Missing required column for '{key}'. Tried: {options}")
                sys.exit(1)

    # Standardize columns
    coords_df = df.rename(columns={actual_cols[k]: k for k in actual_cols})[['gene', 'start', 'end', 'strand']]

    # Add sequence if available
    if 'sequence' in actual_cols:
        coords_df['sequence'] = df[actual_cols['sequence']]

    print("Extracting protein sequences...")
    seen_counts = {}

    for idx, row in coords_df.iterrows():
        gene = row['gene']
        start = int(row['start'])
        end = int(row['end'])
        strand = row['strand']

        # Determine which sequence to use
        if 'sequence' in row:
            seqid = row['sequence']
            if seqid not in genome:
                print(f"Warning: Sequence '{seqid}' not found in genome for gene {gene}. Skipping.")
                continue
            dna_seq = genome[seqid].seq[start-1:end]
        else:
            # Assume single sequence or find any
            for seqid in genome:
                if start-1 < len(genome[seqid].seq) and end <= len(genome[seqid].seq):
                    dna_seq = genome[seqid].seq[start-1:end]
                    break
            else:
                print(f"Warning: Coordinates {start}-{end} out of range for gene {gene}. Skipping.")
                continue

        if strand == "-":
            dna_seq = dna_seq.reverse_complement()
        aa_seq = dna_seq.translate(to_stop=True)

        count = seen_counts.get(gene.lower(), 0) + 1
        seen_counts[gene.lower()] = count
        suffix = f"_{count}" if count > 1 else ""

        filename = f"{gene}{suffix}_{isolate_name}.faa"
        record = SeqRecord(aa_seq, id=gene, description=f"{gene}{suffix}")
        SeqIO.write(record, os.path.join(extracted_dir, filename), "fasta")
        print(f"Extracted: {filename}")

    # Zip the results
    zip_path = os.path.join(output_dir, "Extracted_Proteins.zip")
    print("Creating zip archive...")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(extracted_dir):
            zipf.write(os.path.join(extracted_dir, file), arcname=file)

    print(f"Extraction complete. Results saved to {zip_path}")

if __name__ == "__main__":
    main()