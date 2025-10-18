"""Interactive setup script for FastaAAExtractor.

This script verifies Python version, installs dependencies, validates installation,
and runs a quick test extraction using the bundled example data.

Usage:
    python scripts/setup_fasta_aa_extractor.py
"""

import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def check_python_version():
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 6):
        print("[ERROR] Python 3.6+ is required.")
        sys.exit(1)
    print(f"[OK] Python version: {major}.{minor}")


def pip_install(requirements_file: str):
    print(f"[INFO] Installing dependencies from {requirements_file}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    print("[OK] Dependencies installed")


def verify_cli():
    print("[INFO] Verifying CLI...")
    try:
        subprocess.check_call([sys.executable, "-m", "fasta_aa_extractor.cli", "--help"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[OK] CLI is available")
    except subprocess.CalledProcessError:
        print("[ERROR] CLI not available. Ensure the package is installed correctly.")
        sys.exit(1)


def run_smoke_test():
    print("[INFO] Running a quick extraction test with example data...")
    examples = PROJECT_ROOT / "examples"
    genome = str(examples / "ECS34.fasta")
    coords = str(examples / "ECS34.tsv")
    cmd = [
        sys.executable, "-m", "fasta_aa_extractor.cli",
        "--genome", genome,
        "--coords", coords,
        "--isolate", "SETUP_TEST",
        "--quiet"
    ]
    subprocess.check_call(cmd)
    print("[OK] Test extraction completed successfully")


def main():
    print("=== FastaAAExtractor Setup ===")
    os.chdir(PROJECT_ROOT)
    check_python_version()
    
    # Install runtime dependencies
    pip_install(str(PROJECT_ROOT / "requirements.txt"))
    
    # Optional: install dev dependencies if present
    dev_req = PROJECT_ROOT / "requirements-dev.txt"
    if dev_req.exists():
        choice = input("Install development tools (pytest/black/flake8)? [Y/n]: ").strip().lower()
        if choice in ("", "y", "yes"):
            pip_install(str(dev_req))
    
    verify_cli()
    
    choice = input("Run a quick test extraction using example data? [Y/n]: ").strip().lower()
    if choice in ("", "y", "yes"):
        run_smoke_test()
    
    print("\n✅ Setup complete! You're ready to use FastaAAExtractor.")
    print("Next steps:")
    print("  - Read QUICKSTART.md for a guided tour")
    print("  - Try: python -m fasta_aa_extractor.cli --genome examples/ECS34.fasta --coords examples/ECS34.tsv --isolate ECS34")


if __name__ == "__main__":
    main()