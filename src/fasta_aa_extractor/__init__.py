"""FastaAAExtractor - Extract amino acid sequences from bacterial genomes."""

__version__ = "1.0.0"
__author__ = "Vihaan"
__email__ = "vihaankulkarni29@gmail.com"

# Export main API functions
from .api import FastaAAExtractor, extract_proteins
from .core import run_extraction

__all__ = ["FastaAAExtractor", "extract_proteins", "run_extraction"]
