#!/usr/bin/env nextflow

/*
 * FastaAAExtractor Nextflow Pipeline
 * 
 * This pipeline demonstrates integration of FastaAAExtractor into a
 * Nextflow workflow for scalable, parallel protein extraction.
 * 
 * Usage:
 *   nextflow run nextflow_pipeline.nf --input samples.csv --outdir results
 */

nextflow.enable.dsl=2

// Parameters
params.input = "samples.csv"  // CSV with columns: isolate,genome,coords
params.outdir = "results"
params.publishDir = "${params.outdir}/proteins"

// Process: Extract proteins from one genome
process extractProteins {
    tag "$isolate"
    publishDir params.publishDir, mode: 'copy'
    
    input:
    tuple val(isolate), path(genome), path(coords)
    
    output:
    tuple val(isolate), path("${isolate}_proteins.zip"), path("${isolate}_result.json")
    
    script:
    """
    python -m fasta_aa_extractor.cli \\
        --genome ${genome} \\
        --coords ${coords} \\
        --isolate ${isolate} \\
        --output-dir . \\
        --json ${isolate}_result.json \\
        --quiet
    
    # Rename output to include isolate name
    mv Extracted_Proteins.zip ${isolate}_proteins.zip
    """
}

// Process: Generate summary report
process generateSummary {
    publishDir params.outdir, mode: 'copy'
    
    input:
    path json_files
    
    output:
    path "pipeline_summary.json"
    path "pipeline_report.txt"
    
    script:
    """
    #!/usr/bin/env python3
    import json
    import glob
    
    # Load all result JSONs
    results = []
    for json_file in glob.glob("*_result.json"):
        with open(json_file) as f:
            results.append(json.load(f))
    
    # Create summary
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    total_proteins = sum(r.get('proteins_extracted', 0) for r in successful)
    
    summary = {
        'total_samples': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'total_proteins_extracted': total_proteins,
        'samples': results
    }
    
    # Save JSON summary
    with open('pipeline_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Generate text report
    with open('pipeline_report.txt', 'w') as f:
        f.write("FastaAAExtractor Pipeline Report\\n")
        f.write("=" * 50 + "\\n\\n")
        f.write(f"Total samples: {len(results)}\\n")
        f.write(f"Successful: {len(successful)}\\n")
        f.write(f"Failed: {len(failed)}\\n")
        f.write(f"Total proteins extracted: {total_proteins}\\n\\n")
        
        if successful:
            f.write("Successful samples:\\n")
            for r in successful:
                f.write(f"  - {r['isolate']}: {r['proteins_extracted']} proteins\\n")
        
        if failed:
            f.write("\\nFailed samples:\\n")
            for r in failed:
                f.write(f"  - {r['isolate']}: {r.get('error', 'Unknown error')}\\n")
    """
}

// Workflow
workflow {
    // Read input CSV
    Channel
        .fromPath(params.input)
        .splitCsv(header: true)
        .map { row -> tuple(row.isolate, file(row.genome), file(row.coords)) }
        .set { samples_ch }
    
    // Extract proteins
    extractProteins(samples_ch)
    
    // Collect all JSON results
    extractProteins.out
        .map { isolate, zip, json -> json }
        .collect()
        .set { json_files_ch }
    
    // Generate summary
    generateSummary(json_files_ch)
}

workflow.onComplete {
    println "Pipeline completed!"
    println "Results: ${params.publishDir}"
}
