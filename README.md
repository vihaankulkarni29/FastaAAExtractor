# FastaAAExtractor

# 🧬 FastAAExtractor 

FastAAExtractor is a Google Colab-based tool for extracting amino acid sequences from bacterial genomes using only a FASTA file and a flexible coordinate table.

### 🧪 Features:
- Accepts `.fasta` + `.tsv`, `.tab`, `.csv`, or `.xlsx` as input
- Robust column detection (`Gene`, `Start`, `End`, `Strand`)
- Handles column name variations like "ARO Term" or "Coordinates"
- Output `.faa` sequences saved in a zipped folder for download

### 🔧 How to Use:
1. Upload your genome FASTA file and coordinate file
2. Enter your isolate name
3. Download the zipped folder of protein sequences

### 💡 Example Coordinate File

| Gene | Start | End | Strand |
|------|-------|-----|--------|
| acrA | 12345 | 12950 | + |
| acrB | 56700 | 58950 | - |

---

Built and tested in **Google Colab** for ease of use and reproducibility.
