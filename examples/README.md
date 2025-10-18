# Example Data

This directory contains sample data for testing and demonstrating FastaAAExtractor.

## Files

### ECS34.fasta
A partial *Escherichia coli* strain ECS34 genome containing:
- **contig_1**: Main chromosome fragment (~784 bp)
- **contig_2**: Plasmid pECS34 fragment (~1,068 bp)

### ECS34.tsv
Coordinate table with 6 genes for protein extraction:

| Gene  | Description | Location |
|-------|-------------|----------|
| gfp   | Green Fluorescent Protein | contig_1:1-714 (+) |
| acrA  | Multidrug efflux pump (membrane fusion) | contig_2:1-1011 (+) |
| acrB  | Multidrug efflux pump (transporter) | contig_2:1015-3015 (-) |
| tolC  | Outer membrane protein | contig_1:50-500 (+) |
| mdfA  | Multidrug efflux pump | contig_1:200-650 (-) |
| emrE  | Small multidrug resistance protein | contig_2:300-600 (+) |

## Usage

```bash
# Basic extraction
fasta-aa-extractor --genome examples/ECS34.fasta --coords examples/ECS34.tsv --isolate ECS34

# Expected output
# Creates Extracted_Proteins.zip with 6 FASTA files
```

## What to Expect

This example demonstrates:
- ✅ Multi-contig genome handling
- ✅ Forward and reverse strand translation
- ✅ Flexible coordinate table format
- ✅ Proper protein extraction from bacterial genes

Expected proteins extracted: **6 proteins** (gfp, acrA, acrB, tolC, mdfA, emrE)
