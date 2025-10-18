# Batch Parallel Processing Guide

This guide shows you how to extract proteins from multiple genomes in parallel using the `--batch` and `--parallel` flags.

## Use Case: 150 Genomes

If you have 150 genomes with their respective coordinate files, you can process them all in parallel for massive speedups.

## Step 1: Create a Batch Job File

Create a CSV or TSV file with three columns: `genome`, `coords`, and `isolate`.

**Example: `my_genomes.csv`**

```csv
genome,coords,isolate
/path/to/genome1.fasta,/path/to/coords1.tsv,genome_001
/path/to/genome2.fasta,/path/to/coords2.tsv,genome_002
/path/to/genome3.fasta,/path/to/coords3.tsv,genome_003
...
/path/to/genome150.fasta,/path/to/coords150.tsv,genome_150
```

**Important Notes:**
- Use **absolute paths** (full paths) for genome and coordinate files
- On Windows: `C:\Users\YourName\genomes\genome1.fasta`
- On Linux/Mac: `/home/yourname/genomes/genome1.fasta`
- Column names are case-insensitive: `Genome`, `GENOME`, `genome` all work

## Step 2: Run Batch Parallel Extraction

### Basic Command

```bash
fasta_aa_extractor --batch my_genomes.csv \
                   --genes "acrA,acrB,tolC" \
                   --parallel \
                   --max-workers 8 \
                   --output-dir extracted_proteins \
                   --progress
```

### Command Options Explained

- `--batch my_genomes.csv`: Your batch job file
- `--genes "acrA,acrB,tolC"`: Comma-separated gene names to extract
- `--parallel`: Enable parallel processing
- `--max-workers 8`: Process 8 genomes simultaneously (adjust based on your CPU)
- `--output-dir extracted_proteins`: Output directory
- `--progress`: Show progress bar

### Using a Gene List File

If you have many genes, put them in a file (one gene per line):

**genes.txt:**
```
acrA
acrB
tolC
mdfA
emrE
oprM
mexB
```

Then use:

```bash
fasta_aa_extractor --batch my_genomes.csv \
                   --genes @genes.txt \
                   --parallel \
                   --max-workers 8 \
                   --output-dir extracted_proteins \
                   --progress
```

## Output Structure

The tool creates **per-genome FAA files** with the format `{isolate}_{gene}.faa`:

```
extracted_proteins/
├── genome_001_acrA.faa
├── genome_001_acrB.faa
├── genome_001_tolC.faa
├── genome_002_acrA.faa
├── genome_002_acrB.faa
├── genome_002_tolC.faa
├── ...
├── genome_150_acrA.faa
├── genome_150_acrB.faa
└── genome_150_tolC.faa
```

Each `.faa` file contains the protein sequences (amino acids) for that specific gene from that specific genome.

## Performance Tips

### Choosing --max-workers

The optimal number depends on your system:
- **4-8 workers**: Safe default for most systems
- **12-16 workers**: High-performance workstations
- **32+ workers**: HPC clusters

**Rule of thumb:** Use number of CPU cores - 2

```bash
# On Windows PowerShell
$cores = (Get-WmiObject Win32_Processor).NumberOfLogicalProcessors
$workers = $cores - 2

# On Linux/Mac
cores=$(nproc)
workers=$((cores - 2))
```

### Memory Considerations

Each worker loads one genome at a time using lazy loading (SeqIO.index), so memory usage is efficient:
- Small genomes (3-5 MB): ~50 MB RAM per worker
- Large genomes (10+ MB): ~100-200 MB RAM per worker

For 150 genomes with 8 workers:
- Expected memory: ~1-2 GB
- Processing time: ~5-10 minutes (depending on genome sizes and gene counts)

## Real-World Example

Let's say you have 150 *E. coli* genomes and want to extract 10 AMR genes:

### 1. Create the batch file using your actual paths:

```bash
# Generate batch file (Linux/Mac)
cd /path/to/your/data
for i in {1..150}; do
    echo "/path/to/input/CP$(printf "%06d" $i).1.fasta,/path/to/input/CP$(printf "%06d" $i).1.tsv,strain_$(printf "%03d" $i)"
done > batch_jobs.csv

# Add header
sed -i '1i genome,coords,isolate' batch_jobs.csv
```

```powershell
# Generate batch file (Windows PowerShell)
$header = "genome,coords,isolate"
$lines = @($header)

foreach ($i in 1..150) {
    $genomeID = "CP{0:D6}.1" -f $i
    $strain = "strain_{0:D3}" -f $i
    $genomePath = "C:\Users\Vihaan\Documents\FastaAAExtractor\input\${genomeID}.fasta"
    $coordPath = "C:\Users\Vihaan\Documents\FastaAAExtractor\input\${genomeID}.tsv"
    $lines += "${genomePath},${coordPath},${strain}"
}

$lines | Out-File -FilePath "batch_jobs.csv" -Encoding utf8
```

### 2. Create gene list:

```bash
echo "acrA
acrB
tolC
oprM
mexB
mdfA
emrE
mdtK
acrZ
oqxA" > amr_genes.txt
```

### 3. Run extraction:

```bash
fasta_aa_extractor --batch batch_jobs.csv \
                   --genes @amr_genes.txt \
                   --parallel \
                   --max-workers 8 \
                   --output-dir amr_proteins \
                   --progress \
                   --json-output extraction_stats.json
```

### 4. Check results:

```bash
# Count output files
ls amr_proteins/*.faa | wc -l
# Expected: 150 genomes × 10 genes = 1500 files (if all genes present)

# Check extraction statistics
cat extraction_stats.json
```

## Troubleshooting

### Problem: "No proteins extracted" for some genomes

**Cause:** The gene names in your coordinate files don't match the requested genes.

**Solution:** Check your coordinate files:
```bash
# See what genes are available
head -n 20 /path/to/coords1.tsv
```

Make sure the gene names match exactly (case-sensitive unless columns are normalized).

### Problem: "File not found" errors

**Cause:** Relative paths in batch file.

**Solution:** Use absolute paths in your batch CSV file.

### Problem: Process is slow

**Causes:**
1. Too few workers: Increase `--max-workers`
2. I/O bottleneck: Store genomes on SSD instead of HDD
3. Large genomes: This is expected, be patient

### Problem: Out of memory

**Cause:** Too many workers for available RAM.

**Solution:** Reduce `--max-workers` to 2-4.

## Pipeline Integration

### Output to Downstream Tools

The `.faa` files are standard FASTA format and can be used directly with:
- BLAST/Diamond
- HMMER
- Multiple sequence alignment (MUSCLE, MAFFT)
- Phylogenetic analysis
- Structure prediction (AlphaFold)

### Example: BLAST all extracted proteins

```bash
# Combine all acrA sequences
cat amr_proteins/*_acrA.faa > combined_acrA.faa

# Run BLAST
blastp -query combined_acrA.faa -db nr -out acrA_blast_results.txt -evalue 1e-5
```

### Example: Multiple sequence alignment

```bash
# Align all acrA proteins
mafft --auto amr_proteins/*_acrA.faa > acrA_alignment.fasta

# Build phylogenetic tree
iqtree -s acrA_alignment.fasta -m MFP -bb 1000
```

## Advanced: Python API

For custom pipelines, use the Python API:

```python
from fasta_aa_extractor.core import run_batch_parallel_extraction

# Prepare batch data
batch_data = [
    ("/path/to/genome1.fasta", "/path/to/coords1.tsv", "strain_001"),
    ("/path/to/genome2.fasta", "/path/to/coords2.tsv", "strain_002"),
    # ... add all 150 genomes
]

# Extract genes
stats = run_batch_parallel_extraction(
    batch_data=batch_data,
    gene_list=["acrA", "acrB", "tolC"],
    output_dir="extracted_proteins",
    max_workers=8,
    show_progress=True
)

print(f"Successfully extracted from {stats['successes']} genomes")
print(f"Total proteins: {stats['total_extracted']}")
```

## Summary

✅ **For 150 genomes with 10 genes:**
- Processing time: ~5-10 minutes with 8 workers
- Output: 1500 FAA files (one per genome-gene combination)
- Memory usage: ~1-2 GB

✅ **Key advantages:**
- Parallel processing: 5-10× faster than sequential
- Genome-centric output: Easy to track which genes came from which genome
- Memory efficient: Lazy loading prevents memory overflow
- Progress tracking: Real-time progress bar
- Pipeline-ready: JSON output for automation

✅ **Command to remember:**
```bash
fasta_aa_extractor --batch my_genomes.csv --genes @genes.txt --parallel --max-workers 8 --output-dir results --progress
```
