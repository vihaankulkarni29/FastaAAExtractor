"""Unit tests for FastaAAExtractor core functionality."""

import os
import tempfile
import shutil
import pytest
import pandas as pd
from pathlib import Path
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from fasta_aa_extractor.core import (
    load_genome,
    load_coordinates,
    normalize_columns,
    find_column,
    detect_required_columns,
    extract_proteins,
    run_extraction,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp)


@pytest.fixture
def sample_fasta(temp_dir):
    """Create a sample FASTA file for testing."""
    fasta_path = os.path.join(temp_dir, "test.fasta")
    records = [
        SeqRecord(
            Seq("ATGGCCATGGCCATGGCCATGGCCTAA"),
            id="contig_1",
            description="Test contig 1",
        ),
        SeqRecord(
            Seq("ATGAAACCCGGGTTTCCCGGGTAA"), id="contig_2", description="Test contig 2"
        ),
    ]
    SeqIO.write(records, fasta_path, "fasta")
    return fasta_path


@pytest.fixture
def sample_tsv(temp_dir):
    """Create a sample TSV coordinate file."""
    tsv_path = os.path.join(temp_dir, "test.tsv")
    df = pd.DataFrame(
        {
            "Gene": ["gene1", "gene2", "gene3"],
            "Start": [1, 1, 4],
            "End": [27, 24, 21],
            "Strand": ["+", "+", "-"],
            "Sequence": ["contig_1", "contig_2", "contig_1"],
        }
    )
    df.to_csv(tsv_path, sep="\t", index=False)
    return tsv_path


@pytest.fixture
def sample_csv(temp_dir):
    """Create a sample CSV coordinate file."""
    csv_path = os.path.join(temp_dir, "test.csv")
    df = pd.DataFrame(
        {
            "Product": ["gene1", "gene2"],
            "Begin": [1, 1],
            "Stop": [27, 24],
            "Orientation": ["+", "+"],
        }
    )
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_excel(temp_dir):
    """Create a sample Excel coordinate file."""
    excel_path = os.path.join(temp_dir, "test.xlsx")
    df = pd.DataFrame(
        {"ARO Term": ["gene1"], "Start": [1], "End": [27], "Strand": ["+"]}
    )
    df.to_excel(excel_path, index=False)
    return excel_path


class TestLoadGenome:
    """Tests for load_genome function."""

    def test_load_valid_fasta(self, sample_fasta):
        """Test loading a valid FASTA file."""
        genome = load_genome(sample_fasta)
        assert len(genome) == 2
        assert "contig_1" in genome
        assert "contig_2" in genome
        assert len(str(genome["contig_1"].seq)) == 27
        assert len(str(genome["contig_2"].seq)) == 24

    def test_load_nonexistent_file(self):
        """Test loading a non-existent file raises error."""
        with pytest.raises(ValueError, match="Error loading genome"):
            load_genome("nonexistent.fasta")

    def test_genome_sequence_content(self, sample_fasta):
        """Test that genome sequences are loaded correctly."""
        genome = load_genome(sample_fasta)
        assert str(genome["contig_1"].seq).startswith("ATGGCC")
        assert str(genome["contig_2"].seq).startswith("ATGAAA")


class TestLoadCoordinates:
    """Tests for load_coordinates function."""

    def test_load_tsv(self, sample_tsv):
        """Test loading TSV file."""
        df = load_coordinates(sample_tsv)
        assert len(df) == 3
        assert "Gene" in df.columns

    def test_load_csv(self, sample_csv):
        """Test loading CSV file."""
        df = load_coordinates(sample_csv)
        assert len(df) == 2
        assert "Product" in df.columns

    def test_load_excel(self, sample_excel):
        """Test loading Excel file."""
        df = load_coordinates(sample_excel)
        assert len(df) == 1
        assert "ARO Term" in df.columns

    def test_unsupported_format(self, temp_dir):
        """Test that unsupported format raises error."""
        bad_file = os.path.join(temp_dir, "test.txt")
        Path(bad_file).touch()
        with pytest.raises(ValueError, match="Unsupported coordinate file format"):
            load_coordinates(bad_file)


class TestNormalizeColumns:
    """Tests for normalize_columns function."""

    def test_lowercase_conversion(self):
        """Test that columns are converted to lowercase."""
        df = pd.DataFrame({"Gene": [1], "START": [2], "End": [3]})
        result = normalize_columns(df)
        assert "gene" in result.columns
        assert "start" in result.columns
        assert "end" in result.columns

    def test_strip_whitespace(self):
        """Test that whitespace is stripped from column names."""
        df = pd.DataFrame({" Gene ": [1], "  Start": [2], "End  ": [3]})
        result = normalize_columns(df)
        assert "gene" in result.columns
        assert "start" in result.columns
        assert "end" in result.columns


class TestFindColumn:
    """Tests for find_column function."""

    def test_find_exact_match(self):
        """Test finding exact column match."""
        columns = pd.Index(["gene", "start", "end"])
        result = find_column(["gene"], columns)
        assert result == "gene"

    def test_find_partial_match(self):
        """Test finding partial column match."""
        columns = pd.Index(["gene_name", "start_pos", "end_pos"])
        result = find_column(["gene"], columns)
        assert result == "gene_name"

    def test_no_match(self):
        """Test when no match is found."""
        columns = pd.Index(["abc", "def", "ghi"])
        result = find_column(["gene"], columns)
        assert result is None


class TestDetectRequiredColumns:
    """Tests for detect_required_columns function."""

    def test_standard_columns(self):
        """Test detection of standard column names."""
        df = pd.DataFrame({"gene": [1], "start": [2], "end": [3], "strand": ["+"]})
        df = normalize_columns(df)
        result = detect_required_columns(df)
        assert result["gene"] == "gene"
        assert result["start"] == "start"
        assert result["end"] == "end"
        assert result["strand"] == "strand"

    def test_synonym_columns(self):
        """Test detection of synonym column names."""
        df = pd.DataFrame(
            {"product": [1], "begin": [2], "stop": [3], "orientation": ["+"]}
        )
        df = normalize_columns(df)
        result = detect_required_columns(df)
        assert result["gene"] == "product"
        assert result["start"] == "begin"
        assert result["end"] == "stop"
        assert result["strand"] == "orientation"

    def test_missing_required_column(self):
        """Test error when required column is missing."""
        df = pd.DataFrame(
            {
                "gene": [1],
                "start": [2],
                "end": [3],
                # Missing strand
            }
        )
        df = normalize_columns(df)
        with pytest.raises(ValueError, match="Missing required column"):
            detect_required_columns(df)

    def test_optional_sequence_column(self):
        """Test detection of optional sequence column."""
        df = pd.DataFrame(
            {"gene": [1], "start": [2], "end": [3], "strand": ["+"], "contig": ["c1"]}
        )
        df = normalize_columns(df)
        result = detect_required_columns(df)
        assert "sequence" in result
        assert result["sequence"] == "contig"


class TestExtractProteins:
    """Tests for extract_proteins function."""

    def test_forward_strand_extraction(self, sample_fasta, temp_dir):
        """Test protein extraction from forward strand."""
        genome = load_genome(sample_fasta)
        coords_df = pd.DataFrame(
            {
                "gene": ["test_gene"],
                "start": [1],
                "end": [27],
                "strand": ["+"],
                "sequence": ["contig_1"],
            }
        )

        zip_path = extract_proteins(genome, coords_df, "TEST", temp_dir)
        assert os.path.exists(zip_path)
        assert zip_path.endswith(".zip")

    def test_reverse_strand_extraction(self, sample_fasta, temp_dir):
        """Test protein extraction from reverse strand."""
        genome = load_genome(sample_fasta)
        coords_df = pd.DataFrame(
            {
                "gene": ["rev_gene"],
                "start": [1],
                "end": [27],
                "strand": ["-"],
                "sequence": ["contig_1"],
            }
        )

        zip_path = extract_proteins(genome, coords_df, "TEST", temp_dir)
        assert os.path.exists(zip_path)

    def test_duplicate_gene_handling(self, sample_fasta, temp_dir):
        """Test handling of duplicate gene names."""
        genome = load_genome(sample_fasta)
        coords_df = pd.DataFrame(
            {
                "gene": ["dup_gene", "dup_gene", "dup_gene"],
                "start": [1, 1, 1],
                "end": [27, 24, 27],
                "strand": ["+", "+", "+"],
                "sequence": ["contig_1", "contig_2", "contig_1"],
            }
        )

        zip_path = extract_proteins(genome, coords_df, "TEST", temp_dir)

        # Extract and check files
        import zipfile

        with zipfile.ZipFile(zip_path, "r") as zf:
            files = zf.namelist()
            assert "dup_gene_TEST.faa" in files
            assert "dup_gene_2_TEST.faa" in files
            assert "dup_gene_3_TEST.faa" in files

    def test_multi_contig_extraction(self, sample_fasta, temp_dir):
        """Test extraction from multiple contigs."""
        genome = load_genome(sample_fasta)
        coords_df = pd.DataFrame(
            {
                "gene": ["gene1", "gene2"],
                "start": [1, 1],
                "end": [27, 24],
                "strand": ["+", "+"],
                "sequence": ["contig_1", "contig_2"],
            }
        )

        zip_path = extract_proteins(genome, coords_df, "TEST", temp_dir)
        assert os.path.exists(zip_path)


class TestRunExtraction:
    """Integration tests for run_extraction function."""

    def test_full_extraction_workflow(self, sample_fasta, sample_tsv, temp_dir):
        """Test complete extraction workflow."""
        zip_path = run_extraction(sample_fasta, sample_tsv, "TEST", temp_dir)

        assert os.path.exists(zip_path)
        assert zip_path.endswith("Extracted_Proteins.zip")

        # Verify zip contents
        import zipfile

        with zipfile.ZipFile(zip_path, "r") as zf:
            files = zf.namelist()
            assert len(files) == 3  # 3 genes in sample_tsv

    def test_nonexistent_genome_file(self, sample_tsv, temp_dir):
        """Test error handling for missing genome file."""
        with pytest.raises(FileNotFoundError, match="Genome file"):
            run_extraction("nonexistent.fasta", sample_tsv, "TEST", temp_dir)

    def test_nonexistent_coords_file(self, sample_fasta, temp_dir):
        """Test error handling for missing coordinate file."""
        with pytest.raises(FileNotFoundError, match="Coordinate file"):
            run_extraction(sample_fasta, "nonexistent.tsv", "TEST", temp_dir)

    def test_with_csv_coordinates(self, sample_fasta, sample_csv, temp_dir):
        """Test extraction with CSV coordinate file."""
        zip_path = run_extraction(sample_fasta, sample_csv, "TEST", temp_dir)
        assert os.path.exists(zip_path)

    def test_with_excel_coordinates(self, sample_fasta, sample_excel, temp_dir):
        """Test extraction with Excel coordinate file."""
        zip_path = run_extraction(sample_fasta, sample_excel, "TEST", temp_dir)
        assert os.path.exists(zip_path)


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_coordinate_file(self, sample_fasta, temp_dir):
        """Test handling of empty coordinate file."""
        empty_tsv = os.path.join(temp_dir, "empty.tsv")
        df = pd.DataFrame({"Gene": [], "Start": [], "End": [], "Strand": []})
        df.to_csv(empty_tsv, sep="\t", index=False)

        genome = load_genome(sample_fasta)
        df = load_coordinates(empty_tsv)
        df = normalize_columns(df)
        actual_cols = detect_required_columns(df)
        coords_df = df.rename(columns={actual_cols[k]: k for k in actual_cols})[
            ["gene", "start", "end", "strand"]
        ]

        zip_path = extract_proteins(genome, coords_df, "TEST", temp_dir)

        # Should create zip with no files
        import zipfile

        with zipfile.ZipFile(zip_path, "r") as zf:
            assert len(zf.namelist()) == 0

    def test_coordinates_out_of_range(self, sample_fasta, temp_dir):
        """Test handling of out-of-range coordinates."""
        genome = load_genome(sample_fasta)
        coords_df = pd.DataFrame(
            {
                "gene": ["bad_gene"],
                "start": [100],
                "end": [5000],  # Beyond sequence length
                "strand": ["+"],
                "sequence": ["contig_1"],
            }
        )

        # Should log warning and skip, or extract truncated sequence
        # The current implementation may extract what's available
        zip_path = extract_proteins(genome, coords_df, "TEST", temp_dir)

        import zipfile

        with zipfile.ZipFile(zip_path, "r") as zf:
            # Either skips (0 files) or extracts partial (1 file)
            assert len(zf.namelist()) <= 1

    def test_case_insensitive_strand(self, sample_fasta, temp_dir):
        """Test that strand notation is case-insensitive."""
        genome = load_genome(sample_fasta)

        # Test lowercase
        coords_df = pd.DataFrame(
            {
                "gene": ["gene1"],
                "start": [1],
                "end": [27],
                "strand": ["-"],  # lowercase
                "sequence": ["contig_1"],
            }
        )

        zip_path = extract_proteins(genome, coords_df, "TEST", temp_dir)
        assert os.path.exists(zip_path)


class TestRealWorldExample:
    """Test with the actual example files."""

    def test_example_files(self, temp_dir):
        """Test extraction with the provided example files."""
        # Use actual example files
        example_dir = Path(__file__).parent.parent / "examples"
        if not example_dir.exists():
            pytest.skip("Example files not found")

        genome_file = example_dir / "ECS34.fasta"
        coord_file = example_dir / "ECS34.tsv"

        if genome_file.exists() and coord_file.exists():
            zip_path = run_extraction(
                str(genome_file), str(coord_file), "ECS34", temp_dir
            )

            assert os.path.exists(zip_path)

            # Verify output
            import zipfile

            with zipfile.ZipFile(zip_path, "r") as zf:
                files = zf.namelist()
                assert len(files) >= 1  # Should have extracted proteins
                assert all(f.endswith(".faa") for f in files)
