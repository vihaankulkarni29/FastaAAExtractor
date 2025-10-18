#!/usr/bin/env python3
"""
Python Pipeline Example for FastaAAExtractor
Demonstrates using the Python API for batch processing and workflow integration.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict

from fasta_aa_extractor.api import FastaAAExtractor


def setup_directories(base_dir: str = "results"):
    """Create output directories."""
    base = Path(base_dir)
    (base / "proteins").mkdir(parents=True, exist_ok=True)
    (base / "logs").mkdir(parents=True, exist_ok=True)
    (base / "reports").mkdir(parents=True, exist_ok=True)
    return base


def load_sample_manifest(manifest_file: str) -> List[Dict]:
    """
    Load sample information from a manifest file.
    
    Manifest JSON format:
    [
        {
            "isolate": "Strain1",
            "genome": "data/genomes/strain1.fasta",
            "coords": "data/coordinates/strain1.tsv"
        },
        ...
    ]
    """
    with open(manifest_file) as f:
        return json.load(f)


def run_pipeline(samples: List[Dict], output_dir: Path):
    """Run extraction pipeline for all samples."""
    
    # Initialize extractor
    extractor = FastaAAExtractor(
        output_dir=str(output_dir / "proteins"),
        quiet=True,
        log_file=str(output_dir / "logs" / "pipeline.log")
    )
    
    print("=== FastaAAExtractor Python Pipeline ===\n")
    
    results = []
    
    for i, sample in enumerate(samples, 1):
        print(f"[{i}/{len(samples)}] Processing: {sample['isolate']}")
        
        # Extract proteins
        result = extractor.extract(
            genome=sample['genome'],
            coords=sample['coords'],
            isolate=sample['isolate'],
            return_metadata=True,
            json_output=str(output_dir / "proteins" / f"{sample['isolate']}_result.json")
        )
        
        results.append(result)
        
        # Print status
        if result['status'] == 'success':
            print(f"  ✓ Extracted {result['proteins_extracted']} proteins")
        else:
            print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
        print()
    
    return results


def generate_summary_report(results: List[Dict], output_file: str):
    """Generate a comprehensive summary report."""
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']
    
    total_proteins = sum(r.get('proteins_extracted', 0) for r in successful)
    
    report = {
        'pipeline_summary': {
            'total_samples': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'total_proteins_extracted': total_proteins,
            'average_proteins_per_sample': total_proteins / len(successful) if successful else 0
        },
        'successful_samples': [
            {
                'isolate': r['isolate'],
                'proteins_extracted': r['proteins_extracted'],
                'output': r['zip_path']
            }
            for r in successful
        ],
        'failed_samples': [
            {
                'isolate': r['isolate'],
                'error': r.get('error', 'Unknown')
            }
            for r in failed
        ]
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report


def main():
    """Main pipeline entry point."""
    
    # Setup
    output_dir = setup_directories("results")
    
    # Example: Create a sample manifest programmatically
    # In practice, you'd load this from a file or database
    samples = [
        {
            'isolate': 'ECS34',
            'genome': 'examples/ECS34.fasta',
            'coords': 'examples/ECS34.tsv'
        }
    ]
    
    # Or load from manifest file:
    # samples = load_sample_manifest("samples_manifest.json")
    
    # Run pipeline
    results = run_pipeline(samples, output_dir)
    
    # Generate report
    report_file = output_dir / "reports" / "pipeline_summary.json"
    report = generate_summary_report(results, str(report_file))
    
    # Print summary
    print("=== Pipeline Complete ===")
    print(f"Total samples: {report['pipeline_summary']['total_samples']}")
    print(f"Successful: {report['pipeline_summary']['successful']}")
    print(f"Failed: {report['pipeline_summary']['failed']}")
    print(f"Total proteins: {report['pipeline_summary']['total_proteins_extracted']}")
    print(f"\nSummary report: {report_file}")


if __name__ == "__main__":
    main()
