# 🚀 QuickStart Guide - FastaAAExtractor

**Welcome!** This guide shows you how to extract protein sequences from many genomes in just a few minutes—no bioinformatics expertise required!

---

## What Does This Tool Do?

- Finds genes in your bacterial genomes using coordinate tables
- Translates DNA to protein (amino acid) sequences
- Saves each protein as a FASTA file, ready for BLAST, alignment, etc.

---

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

---

## Your First Extraction (Batch Mode)

**Step 1:** Place all your genome files (`.fasta` or `.fa`) in one folder, and all coordinate files (`.tsv`) in another folder. Make sure filenames match:
- `AP018572.2.fasta` → `AP018572.2.tsv`
- `CP029242.fasta` → `CP029242.tsv`

**Step 2:** Run the tool:
```bash
fasta_aa_extractor --genome-dir path/to/genomes/ --coords-dir path/to/coords/ --genes "acrA,acrB,tolC" --parallel --output-dir results/
```

**Step 3:** Check your results in the output folder. You'll see files like:
- `AP018572.2_acrA.faa`
- `AP018572.2_acrB.faa`
- `CP029242_tolC.faa`

---

## Common Use Cases
- Extract all resistance genes from 100+ genomes in one go
- Use a gene list file: `--genes @genes.txt`
- Works on Windows, Mac, Linux

---

## Troubleshooting
- **No output?** Check that genome and coordinate filenames match exactly
- **Missing genes?** Make sure gene names in your coordinate files match what you requested
- **Need help?** Run `fasta_aa_extractor --help` or ask on GitHub

---

**Simple. Fast. No CSVs. Just point and extract!**

