# 🧬 FastAAExtractor 2.0

**FastAAExtractor** is a lightweight, Google Colab–ready tool that extracts amino acid sequences from bacterial genomes using only a FASTA file and a coordinate table.

---

## 🧪 Key Features

- 🧬 Accepts genome in FASTA format
- 📄 Accepts gene coordinates from `.tsv`, `.tab`, `.csv`, or `.xlsx` files
- 🧠 Automatically detects flexible column names (`Gene`, `ARO Term`, `Coordinates`, etc.)
- 🔁 Handles multiple entries of the same gene (with suffixing)
- 💾 Outputs amino acid sequences in `.faa` format, zipped for download

---

## 📂 Input Requirements

### 1. Genome File
- Format: `.fasta` or `.fa`
- Must contain full genome or contig sequences

### 2. Coordinate File (any of the following):
- `.tsv`, `.tab`, `.csv`, or `.xlsx`
- Required columns (case-insensitive, flexible matching):
  - `Gene` → Gene name or product/ARO term
  - `Start` → Start coordinate
  - `End` → End coordinate
  - `Strand` → `+` or `-`

### Example (TSV format):

| Gene | Start | End | Strand |
|------|-------|-----|--------|
| acrA | 12345 | 12950 | + |
| acrB | 56700 | 58950 | - |


## 🚀 How to Use (in Google Colab)

1. Open the notebook: [👉 Launch in Colab](#) *(insert link)*
2. Upload your FASTA and coordinate file when prompted
3. Enter your isolate name (e.g., `ECS34`)
4. Automatically download a ZIP of extracted `.faa` files

---

## 📦 Installation (Local Testing)

For users running this outside Colab:

```bash
git clone https://github.com/yourusername/FastAAExtractor.git
cd FastAAExtractor
pip install -r requirements.txt
