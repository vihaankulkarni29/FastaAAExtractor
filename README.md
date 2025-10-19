# 🧬 FastAAExtractor

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FastAAExtractor** is a simple, fast tool for extracting amino acid sequences from bacterial genomes using coordinate tables.

## Features
- Easy batch processing: just point to your genome and coordinate folders
- Automatic matching: genome and coordinate files are paired by name
- Parallel extraction for speed
- Flexible gene selection
- Works on Windows, Mac, Linux

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Extract from a folder of genomes
```bash
fasta_aa_extractor --genome-dir input/genomes/ --coords-dir input/coords/ --genes "acrA,acrB,tolC" --parallel --max-workers 8 --output-dir results/
```
- `--genome-dir`: folder with `.fasta` or `.fa` files
- `--coords-dir`: folder with `.tsv` files (named to match genomes)
- `--genes`: comma-separated list or `@genes.txt` file
- `--parallel`: enables fast parallel processing
- `--max-workers`: number of parallel jobs (default: 4)
- `--output-dir`: where to save results

### 3. Output
- Creates one `.faa` file per genome-gene pair: `GenomeName_GeneName.faa`
- Standard FASTA format, ready for BLAST, alignment, etc.

## Example
```bash
fasta_aa_extractor --genome-dir input/ --coords-dir input/ --genes "acrA,acrB" --parallel --output-dir proteins/
```

## Need help?
- See QUICKSTART.md for more details
- For advanced options, run: `fasta_aa_extractor --help`

---

**Simple. Fast. No CSVs. Just point and extract!**
