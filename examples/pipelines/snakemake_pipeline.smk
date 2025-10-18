# FastaAAExtractor Snakemake Pipeline
# 
# This Snakemake workflow demonstrates integration of FastaAAExtractor
# for parallel, reproducible protein extraction.
#
# Usage:
#   snakemake --snakefile snakemake_pipeline.smk --cores 4

import pandas as pd
from pathlib import Path

# Configuration
configfile: "config.yaml"

# Load sample manifest
SAMPLES = pd.read_csv(config.get("manifest", "samples.csv"))
ISOLATES = SAMPLES["isolate"].tolist()

# Output directory
OUTDIR = config.get("outdir", "results")

# Rule: Final target
rule all:
    input:
        expand(f"{OUTDIR}/proteins/{{isolate}}_proteins.zip", isolate=ISOLATES),
        f"{OUTDIR}/pipeline_summary.json"

# Rule: Extract proteins from one genome
rule extract_proteins:
    input:
        genome = lambda wildcards: SAMPLES[SAMPLES["isolate"] == wildcards.isolate]["genome"].values[0],
        coords = lambda wildcards: SAMPLES[SAMPLES["isolate"] == wildcards.isolate]["coords"].values[0]
    output:
        zip = f"{OUTDIR}/proteins/{{isolate}}_proteins.zip",
        json = f"{OUTDIR}/proteins/{{isolate}}_result.json"
    log:
        f"{OUTDIR}/logs/{{isolate}}.log"
    params:
        isolate = "{isolate}",
        outdir = f"{OUTDIR}/proteins"
    shell:
        """
        python -m fasta_aa_extractor.cli \
            --genome {input.genome} \
            --coords {input.coords} \
            --isolate {params.isolate} \
            --output-dir {params.outdir} \
            --json {output.json} \
            --log-file {log} \
            --quiet
        
        # Rename default output
        mv {params.outdir}/Extracted_Proteins.zip {output.zip}
        """

# Rule: Generate pipeline summary
rule generate_summary:
    input:
        json_files = expand(f"{OUTDIR}/proteins/{{isolate}}_result.json", isolate=ISOLATES)
    output:
        summary = f"{OUTDIR}/pipeline_summary.json",
        report = f"{OUTDIR}/pipeline_report.txt"
    run:
        import json
        
        # Load all results
        results = []
        for json_file in input.json_files:
            with open(json_file) as f:
                results.append(json.load(f))
        
        # Calculate statistics
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] != 'success']
        total_proteins = sum(r.get('proteins_extracted', 0) for r in successful)
        
        # Create summary
        summary = {
            'total_samples': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'total_proteins_extracted': total_proteins,
            'average_proteins_per_sample': total_proteins / len(successful) if successful else 0,
            'samples': results
        }
        
        # Save JSON
        with open(output.summary, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Generate text report
        with open(output.report, 'w') as f:
            f.write("FastaAAExtractor Pipeline Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total samples: {len(results)}\n")
            f.write(f"Successful: {len(successful)}\n")
            f.write(f"Failed: {len(failed)}\n")
            f.write(f"Total proteins: {total_proteins}\n")
            f.write(f"Average proteins/sample: {summary['average_proteins_per_sample']:.1f}\n\n")
            
            if successful:
                f.write("Successful samples:\n")
                for r in successful:
                    f.write(f"  - {r['isolate']}: {r['proteins_extracted']} proteins\n")
            
            if failed:
                f.write("\nFailed samples:\n")
                for r in failed:
                    f.write(f"  - {r['isolate']}: {r.get('error', 'Unknown error')}\n")

# Optional: Clean intermediate files
rule clean:
    shell:
        f"rm -rf {OUTDIR}"
