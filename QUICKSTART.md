# 🚀 QuickStart Guide - FastaAAExtractor

**Welcome!** This guide will help you extract protein sequences from bacterial genomes in just a few minutes - no bioinformatics expertise required!

---

## 📚 Table of Contents

1. [What Does This Tool Do?](#what-does-this-tool-do)
2. [Before You Start](#before-you-start)
3. [Installation](#installation)
4. [Your First Extraction](#your-first-extraction)
5. [Understanding Your Inputs](#understanding-your-inputs)
6. [Understanding Your Outputs](#understanding-your-outputs)
7. [Common Use Cases](#common-use-cases)
8. [Troubleshooting](#troubleshooting)
9. [What Happens Under the Hood?](#what-happens-under-the-hood)
10. [Next Steps](#next-steps)

---

## 🎯 What Does This Tool Do?

**In Simple Terms:**

Imagine you have:
- A bacterial genome (like a cookbook with all the recipes/genes)
- A list of specific genes you're interested in (like "I want the recipe for chocolate cake")

FastaAAExtractor will:
1. Find those specific genes in the genome
2. Translate the DNA code into protein sequences
3. Save each protein as a separate file, all packaged in a ZIP

**Real-World Example:**

You're studying antibiotic resistance in *E. coli*. You have the genome sequence and you know where the resistance genes are located. This tool automatically extracts the protein sequences of those resistance genes so you can analyze them further.

---

## 📋 Before You Start

### What You Need:

1. **A genome file** (FASTA format)
   - Extension: `.fasta` or `.fa`
   - Contains DNA sequences from your bacterial genome
   - Example: `ECS34.fasta`

2. **A coordinate table** (TSV, CSV, or Excel)
   - Extension: `.tsv`, `.csv`, or `.xlsx`
   - Lists genes with their locations in the genome
   - Example: `ECS34.tsv`

3. **Python 3.6 or newer**
   - Check by running: `python --version`

### Don't Have Example Files?

No problem! We've included sample data in the `examples/` folder. You can practice with those first!

---

## 💻 Installation

### Step 1: Download the Tool

```bash
# Clone from GitHub
git clone https://github.com/vihaankulkarni29/FastaAAExtractor.git
cd FastaAAExtractor
```

### Step 2: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

This installs:
- `biopython` - for reading DNA sequences
- `pandas` - for reading your coordinate table
- `openpyxl` - for Excel support

**That's it! You're ready to go.** ✅

---

## 🎬 Your First Extraction

Let's run a test extraction with our example data:

### Command:

```bash
python -m fasta_aa_extractor.cli --genome examples/ECS34.fasta --coords examples/ECS34.tsv --isolate ECS34
```

### What You'll See:

```
Success! Results saved to: .\Extracted_Proteins.zip
```

### Check Your Results:

You should now have a file called `Extracted_Proteins.zip` containing 6 protein files:
- `gfp_ECS34.faa`
- `acrA_ECS34.faa`
- `acrB_ECS34.faa`
- `tolC_ECS34.faa`
- `mdfA_ECS34.faa`
- `emrE_ECS34.faa`

**🎉 Congratulations! You just extracted your first proteins!**

---

## 📊 Understanding Your Inputs

### 1. Genome File (FASTA)

**What it looks like:**

```
>contig_1 Escherichia coli chromosome
ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAA...
>contig_2 Escherichia coli plasmid
ATGAAACGCATTAGCACCACCATTACCACCACCATCACCATTACCACAGGT...
```

**Key parts:**
- Lines starting with `>` are sequence names (headers)
- Following lines are DNA sequences (A, T, G, C)
- Can have multiple sequences (contigs) in one file

### 2. Coordinate Table (TSV/CSV/Excel)

**What it looks like (TSV/CSV):**

```
Gene    Start   End     Strand  Sequence
gfp     1       714     +       contig_1
acrA    1       1011    +       contig_2
acrB    1015    3015    -       contig_2
```

**Required columns** (flexible naming):

| Column Purpose | Accepted Names |
|----------------|----------------|
| Gene name | Gene, Product, ARO Term, Gene Name |
| Start position | Start, Begin, From |
| End position | End, Stop, To |
| DNA strand | Strand, Orientation |
| Sequence ID (optional) | Sequence, Contig, SeqID |

**Column explanation:**
- **Gene**: Name of the gene/protein
- **Start**: Where the gene begins (number, 1-based)
- **End**: Where the gene ends (number, 1-based)
- **Strand**: Direction of the gene (`+` forward, `-` reverse)
- **Sequence**: Which contig/chromosome (only needed for multi-contig genomes)

---

## 📦 Understanding Your Outputs

### The ZIP File

Contains individual FASTA files for each protein, named as:
```
{GeneName}_{IsolateName}.faa
```

Example: `acrA_ECS34.faa`

### Inside Each `.faa` File:

```
>acrA acrA
MKLPTRLVLSLVFGASSLAASSVQAAPTTKVDNKTLTMQFDPKVSFAGIQLPVPQVVWVPQGAKEGQVHV...
```

**What this is:**
- Header line: `>acrA acrA` (protein name)
- Sequence lines: The amino acid sequence (protein)
- Letters represent amino acids (M, K, L, P, T, R, V, etc.)

**This is what you wanted!** These protein sequences can now be used for:
- BLAST searches
- Structure prediction
- Phylogenetic analysis
- Sequence alignment
- Database submission

---

## 💡 Common Use Cases

### Use Case 1: Single Genome, Multiple Genes

**Scenario:** You have one bacterial isolate and want to extract all antibiotic resistance genes.

```bash
python -m fasta_aa_extractor.cli \
  --genome my_bacteria.fasta \
  --coords resistance_genes.tsv \
  --isolate Strain123
```

### Use Case 2: Custom Output Location

**Scenario:** You want results in a specific folder.

```bash
python -m fasta_aa_extractor.cli \
  --genome data/genome.fasta \
  --coords data/genes.xlsx \
  --isolate Sample1 \
  --output-dir results/
```

### Use Case 3: Working with Excel Files

**Scenario:** Your lab uses Excel for coordinate tables.

```bash
python -m fasta_aa_extractor.cli \
  --genome genome.fasta \
  --coords coordinates.xlsx \
  --isolate MyStrain
```

**No special settings needed** - the tool automatically detects Excel format!

### Use Case 4: Multi-Contig Genome

**Scenario:** Your genome has multiple chromosomes/plasmids.

Just make sure your coordinate table has a `Sequence` column specifying which contig each gene is on. The tool handles the rest automatically!

---

## 🔧 Troubleshooting

### Problem: "Genome file not found"

**Solution:**
- Check the file path is correct
- Make sure the file ends in `.fasta` or `.fa`
- Use quotes around paths with spaces: `"my folder/genome.fasta"`

### Problem: "Missing required column for 'gene'"

**Solution:**
- Your coordinate table needs a column for gene names
- Accepted names: Gene, Product, ARO Term, Gene Name
- Check your column headers match one of these (case-insensitive)

### Problem: "Error loading coordinates"

**Solution:**
- Make sure file is valid TSV, CSV, or Excel
- Check there are no extra blank rows at the top
- Verify the file isn't corrupted (can you open it?)

### Problem: "No proteins extracted"

**Possible causes:**
1. **Wrong sequence names:** Check that the `Sequence` column matches your FASTA headers exactly
2. **Coordinates out of range:** Start/End positions must be within the sequence length
3. **Empty coordinate file:** Make sure your table has data rows

### Problem: "Partial codon warning"

**What it means:** A gene's length isn't divisible by 3 (DNA codons are 3 bases).

**Usually harmless!** The tool still extracts the protein, just truncating the incomplete codon. If concerned, double-check your coordinates.

### Problem: Tool runs slowly

**Solutions:**
- Large genome? This is normal, be patient
- Check disk space (tool creates temporary files)
- Close other programs to free up memory

---

## 🧠 What Happens Under the Hood?

**For the curious!** Here's what FastaAAExtractor does step-by-step:

### Step 1: Load Your Files
- Reads the genome FASTA into memory
- Parses your coordinate table
- Validates that all required information is present

### Step 2: Detect Columns
- Intelligently finds which columns contain gene names, positions, etc.
- Uses synonym matching (e.g., "Product" = "Gene")
- Reports any missing required columns

### Step 3: Extract DNA Sequences
For each gene:
- Locates the correct contig/chromosome
- Extracts DNA from Start to End position
- If strand is `-`, takes the reverse complement

### Step 4: Translate to Protein
- Groups DNA bases into codons (sets of 3)
- Translates each codon to an amino acid
  - Example: ATG → Methionine (M)
  - Example: TGG → Tryptophan (W)
- Stops at stop codons (TAA, TAG, TGA)

### Step 5: Handle Duplicates
- If same gene name appears multiple times
- Adds suffixes: `gene1`, `gene1_2`, `gene1_3`

### Step 6: Package Results
- Saves each protein as individual FASTA file
- Creates ZIP archive
- Cleans up temporary files

**All automated - you just run one command!**

---

## 📚 Next Steps

### Level Up Your Skills:

1. **Programmatic Use:** Import as Python library for custom workflows
   ```python
   from fasta_aa_extractor.core import run_extraction
   
   run_extraction(
       genome_file="genome.fasta",
       coord_file="coords.tsv",
       isolate_name="MyStrain",
       output_dir="results/"
   )
   ```

2. **Pipeline Integration:** Use in Nextflow, Snakemake, or shell scripts
   - See `examples/pipelines/` for examples

3. **Batch Processing:** Process multiple isolates automatically
   - Loop through files in a directory
   - See scripting examples in documentation

### Get Help:

- 📖 **Full Documentation:** [README.md](README.md)
- 🐛 **Report Issues:** [GitHub Issues](https://github.com/vihaankulkarni29/FastaAAExtractor/issues)
- 💬 **Ask Questions:** [GitHub Discussions](https://github.com/vihaankulkarni29/FastaAAExtractor/discussions)
- 📧 **Email:** vihaankulkarni29@gmail.com

### Contribute:

- Found a bug? Report it!
- Have a feature idea? Suggest it!
- Want to contribute code? See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## ❓ FAQ

**Q: Can I use this for viruses or eukaryotes?**  
A: Yes! While designed for bacteria, it works with any genome + coordinate table.

**Q: What if my gene coordinates are 0-based instead of 1-based?**  
A: Add 1 to all your Start positions before running the tool.

**Q: Can I extract only certain genes from my table?**  
A: Yes! Just remove the rows you don't want from your coordinate table.

**Q: Do I need to cite this tool?**  
A: Yes please! See README.md for citation format.

**Q: Is this tool suitable for publication-quality analysis?**  
A: Absolutely! It uses well-established BioPython libraries and has been thoroughly tested.

**Q: Can I run this on a computing cluster?**  
A: Yes! It's a command-line tool that works anywhere Python runs.

---

## 🎓 Glossary

- **FASTA**: A text format for DNA/protein sequences
- **Contig**: A contiguous DNA sequence (part of a genome)
- **Strand**: DNA direction (+ forward, - reverse)
- **Codon**: Three DNA bases that code for one amino acid
- **Translation**: Converting DNA sequence to protein sequence
- **Reverse Complement**: Flipped version of DNA (used for - strand genes)

---

**Ready to extract some proteins?** 🧬✨

If you got stuck anywhere, don't hesitate to ask for help. Happy extracting!

