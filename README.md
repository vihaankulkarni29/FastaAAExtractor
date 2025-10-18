# 🧬 FastAAExtractor

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg)](https://bioconda.github.io/)

**FastAAExtractor** is a lightweight, efficient bioinformatics tool for extracting amino acid sequences from bacterial genomes. It translates DNA sequences to proteins using coordinate data from various formats, making it ideal for analyzing resistance genes, efflux pumps, and other genomic features.

## ✨ Features

- **Flexible Input Formats**: Supports FASTA genomes and coordinate tables in TSV, CSV, or Excel formats
- **Intelligent Column Detection**: Automatically recognizes column names with synonyms (e.g., "Gene", "Product", "ARO Term")
- **Multi-Contig Support**: Handles genomes with multiple contigs or sequences
- **Strand-Aware Translation**: Correctly processes forward and reverse strands
- **Duplicate Handling**: Adds suffixes for multiple entries of the same gene
- **Cross-Platform**: Runs on CLI or in Google Colab
- **Zipped Output**: Packages results in a convenient ZIP archive

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/FastaAAExtractor.git
cd FastaAAExtractor
pip install -e .
```

### Basic Usage

```bash
fasta-aa-extractor --genome examples/ECS34.fasta --coords examples/ECS34.tsv --isolate ECS34
```

Or run as module:

```bash
python -m fasta_aa_extractor.cli --genome examples/ECS34.fasta --coords examples/ECS34.tsv --isolate ECS34
```

This extracts 43 multidrug efflux proteins from the example *E. coli* isolate.

## 📖 Usage

### Command Line

```bash
python src/fasta_aa_extractor.py [OPTIONS]
```

#### Required Arguments
- `--genome PATH`: Path to genome FASTA file (.fasta or .fa)
- `--coords PATH`: Path to coordinate file (.tsv, .tab, .csv, .xlsx)
- `--isolate NAME`: Isolate name for output files (e.g., ECS34)

#### Optional Arguments
- `--output-dir PATH`: Output directory (default: current directory)
- `-h, --help`: Show help message

#### Example with Custom Output

```bash
python src/fasta_aa_extractor.py \
  --genome data/my_genome.fasta \
  --coords data/genes.xlsx \
  --isolate MyIsolate \
  --output-dir results/
```

### Google Colab

The original Jupyter notebook (`FastaAAExtractor.ipynb`) is available for interactive use in Google Colab. Upload your files and execute the cells.

## 📋 Input Formats

### Genome File
- **Format**: FASTA (.fasta, .fa)
- **Content**: Bacterial genome sequences (single or multi-contig)

### Coordinate File
Supported formats: TSV, CSV, Excel (.xlsx)

**Required Columns** (case-insensitive, flexible naming):
- **Gene/Product**: Gene identifier (e.g., "acrA", "ARO Term")
- **Start**: Start coordinate (1-based)
- **End**: End coordinate (1-based)
- **Strand**: Orientation ("+" or "-")

**Optional Columns**:
- **Sequence**: Contig/sequence ID (for multi-contig genomes)

#### Example Coordinate Table

| Gene  | Start | End | Strand | Sequence  |
|-------|-------|-----|--------|-----------|
| acrA  | 12345 | 12950 | +     | contig_1 |
| acrB  | 56700 | 58950 | -     | contig_1 |

## 🏗️ Project Structure

```
FastaAAExtractor/
├── src/
│   └── fasta_aa_extractor.py    # Main CLI script
├── examples/                    # Example input files
│   ├── ECS34.fasta
│   └── ECS34.tsv
├── FastaAAExtractor.ipynb       # Google Colab notebook
├── requirements.txt             # Python dependencies
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🧪 Testing

Run the tool with provided examples:

```bash
python src/fasta_aa_extractor.py --genome examples/ECS34.fasta --coords examples/ECS34.tsv --isolate ECS34
```

Expected output: `Extracted_Proteins.zip` with 43 .faa files.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Citation

If you use FastAAExtractor in your research, please cite:

```
[Your Name]. FastAAExtractor: A tool for extracting amino acid sequences from bacterial genomes.
https://github.com/yourusername/FastaAAExtractor
```

## 🆘 Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/yourusername/FastaAAExtractor/issues)
- **Discussions**: Join community discussions on [GitHub Discussions](https://github.com/yourusername/FastaAAExtractor/discussions)

---

*Developed with ❤️ for the bioinformatics community*
