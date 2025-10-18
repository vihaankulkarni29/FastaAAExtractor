#!/bin/bash
# Simple Pipeline Example for FastaAAExtractor
# This script demonstrates batch processing of multiple bacterial genomes

set -e  # Exit on error

echo "=== FastaAAExtractor Simple Pipeline ==="
echo ""

# Configuration
INPUT_DIR="data/genomes"
COORDS_DIR="data/coordinates"
OUTPUT_DIR="results/proteins"
LOG_DIR="logs"

# Create output directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$LOG_DIR"

# Counter for statistics
total=0
successful=0
failed=0

# Find all genome files
for genome_file in "$INPUT_DIR"/*.fasta; do
    # Extract isolate name from filename
    isolate=$(basename "$genome_file" .fasta)
    coords_file="$COORDS_DIR/${isolate}.tsv"
    
    # Check if coordinate file exists
    if [ ! -f "$coords_file" ]; then
        echo "⚠ Warning: Coordinate file not found for $isolate, skipping"
        ((failed++))
        continue
    fi
    
    echo "Processing: $isolate"
    ((total++))
    
    # Run extraction with JSON output for tracking
    python -m fasta_aa_extractor.cli \
        --genome "$genome_file" \
        --coords "$coords_file" \
        --isolate "$isolate" \
        --output-dir "$OUTPUT_DIR" \
        --json "$OUTPUT_DIR/${isolate}_result.json" \
        --log-file "$LOG_DIR/${isolate}.log" \
        --quiet
    
    # Check exit code
    if [ $? -eq 0 ]; then
        echo "✓ $isolate: Success"
        ((successful++))
    else
        echo "✗ $isolate: Failed (see logs/$isolate.log)"
        ((failed++))
    fi
    echo ""
done

# Summary
echo "=== Pipeline Complete ==="
echo "Total genomes: $total"
echo "Successful: $successful"
echo "Failed: $failed"
echo ""
echo "Results saved to: $OUTPUT_DIR"
echo "Logs saved to: $LOG_DIR"

# Generate summary report
echo "Generating summary report..."
python -c "
import json
import glob

results = []
for json_file in glob.glob('$OUTPUT_DIR/*_result.json'):
    with open(json_file) as f:
        results.append(json.load(f))

# Create summary
summary = {
    'total_isolates': len(results),
    'successful': sum(1 for r in results if r['status'] == 'success'),
    'total_proteins': sum(r.get('proteins_extracted', 0) for r in results),
    'isolates': results
}

with open('$OUTPUT_DIR/pipeline_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print(f\"Total proteins extracted: {summary['total_proteins']}\")
"

echo "Summary report: $OUTPUT_DIR/pipeline_summary.json"
