"""Unit tests for FastaAAExtractor CLI."""

import sys
import pytest
from unittest.mock import patch

from fasta_aa_extractor.cli import main, setup_logging


class TestCLI:
    """Tests for command-line interface."""

    def test_main_success(self, tmp_path):
        """Test successful CLI execution."""
        # Create test files
        genome = tmp_path / "test.fasta"
        genome.write_text(">seq1\nATGTAA\n")

        coords = tmp_path / "test.tsv"
        coords.write_text("Gene\tStart\tEnd\tStrand\ngene1\t1\t6\t+\n")

        testargs = [
            "prog",
            "--genome",
            str(genome),
            "--coords",
            str(coords),
            "--isolate",
            "TEST",
            "--output-dir",
            str(tmp_path),
        ]

        with patch.object(sys, "argv", testargs):
            result = main()
            assert result == 0

    def test_main_missing_genome(self):
        """Test CLI with missing genome file."""
        testargs = [
            "prog",
            "--genome",
            "missing.fasta",
            "--coords",
            "test.tsv",
            "--isolate",
            "TEST",
        ]

        with patch.object(sys, "argv", testargs):
            result = main()
            assert result == 2

    def test_verbose_logging(self, capsys):
        """Test verbose logging mode."""
        testargs = [
            "prog",
            "--genome",
            "test.fasta",
            "--coords",
            "test.tsv",
            "--isolate",
            "TEST",
            "--verbose",
        ]

        with patch.object(sys, "argv", testargs):
            # Will fail due to missing files, but test verbose flag
            result = main()
            assert result == 2

    def test_help_message(self):
        """Test --help flag."""
        testargs = ["prog", "--help"]

        with patch.object(sys, "argv", testargs):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0


class TestLogging:
    """Tests for logging setup."""

    def test_setup_logging_verbose(self):
        """Test verbose logging setup."""
        setup_logging(verbose=True)
        # Logger should be configured at INFO level

    def test_setup_logging_quiet(self):
        """Test quiet logging setup."""
        setup_logging(verbose=False)
        # Logger should be configured at WARNING level
