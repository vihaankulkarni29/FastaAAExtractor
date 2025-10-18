# Pipeline Integration Examples

This directory contains examples of integrating FastaAAExtractor into various bioinformatics pipelines.

## Available Examples

1. **Shell Script** (`simple_pipeline.sh`) - Basic bash script for batch processing
2. **Python Script** (`python_pipeline.py`) - Python API usage examples
3. **Nextflow** (`nextflow_pipeline.nf`) - Nextflow DSL2 workflow
4. **Snakemake** (`snakemake_pipeline.smk`) - Snakemake workflow

## Quick Start

### Shell Script Pipeline

```bash
bash examples/pipelines/simple_pipeline.sh
```

### Python API

```python
python examples/pipelines/python_pipeline.py
```

### Nextflow

```bash
nextflow run examples/pipelines/nextflow_pipeline.nf
```

### Snakemake

```bash
snakemake --snakefile examples/pipelines/snakemake_pipeline.smk --cores 1
```

## Integration Patterns

### Pattern 1: Simple Sequential Processing

Best for: Small number of genomes, simple workflows

```bash
for genome in *.fasta; do
    isolate=$(basename "$genome" .fasta)
    python -m fasta_aa_extractor.cli \
        --genome "$genome" \
        --coords "${isolate}.tsv" \
        --isolate "$isolate" \
        --quiet
done
```

### Pattern 2: JSON Output for Chaining

Best for: Multi-step pipelines, error tracking

```bash
python -m fasta_aa_extractor.cli \
    --genome genome.fasta \
    --coords genes.tsv \
    --isolate Sample1 \
    --json results.json \
    --quiet

# Check success in next step
if grep -q '"status": "success"' results.json; then
    echo "Proceeding to next analysis..."
fi
```

### Pattern 3: Python API Integration

Best for: Complex workflows, programmatic control

```python
from fasta_aa_extractor.api import FastaAAExtractor

extractor = FastaAAExtractor(output_dir="results/", quiet=True)

# Process multiple samples
for sample in samples:
    result = extractor.extract(
        genome=sample['genome'],
        coords=sample['coords'],
        isolate=sample['name'],
        json_output=f"results/{sample['name']}_result.json"
    )
    
    if result['status'] == 'success':
        # Continue with downstream analysis
        analyze_proteins(result['zip_path'])
```

### Pattern 4: Parallel Processing

Best for: Large datasets, cluster computing

See `nextflow_pipeline.nf` and `snakemake_pipeline.smk` for examples.

## Exit Codes

FastaAAExtractor uses standard exit codes for automation:

- `0`: Success
- `1`: General error
- `2`: File not found
- `3`: Invalid input format
- `4`: No proteins extracted

Example usage:

```bash
python -m fasta_aa_extractor.cli --genome g.fasta --coords c.tsv --isolate S1
if [ $? -eq 0 ]; then
    echo "Success!"
else
    echo "Failed with code $?"
fi
```

## Tips for Pipeline Integration

1. **Use --quiet mode** to reduce log noise in pipelines
2. **Enable --json output** for easy result parsing
3. **Check exit codes** for error handling
4. **Use --log-file** for debugging without cluttering stdout
5. **Set --output-dir** to organize results by sample/batch

## Need Help?

- See individual example files for detailed comments
- Check QUICKSTART.md for beginner-friendly guide
- Open an issue on GitHub for pipeline-specific questions
