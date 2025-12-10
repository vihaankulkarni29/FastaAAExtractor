import hashlib
import shutil
from pathlib import Path
import csv

SRC_DIRS_ORDER = [
    "results_efflux_pumps",
    "results_5genomes",
    "results_resistance_genes",
    "results_ncbi",
    "results_resfinder",
]
DEST_DIR = Path("results_all_genes")
DEST_DIR.mkdir(exist_ok=True)

index_rows = []
seen_names = set()  # exact filename de-dup (prefer earlier dirs)

# helper to hash a file

def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

# Map to check content-duplicate collisions
content_hashes = {}

copied = 0
skipped_same_name = 0
renamed_due_conflict = 0

for src_dir in SRC_DIRS_ORDER:
    sdir = Path(src_dir)
    if not sdir.exists():
        continue
    for faa in sdir.glob('*.faa'):
        dest_name = faa.name  # default keep the same
        dest_path = DEST_DIR / dest_name

        # if same filename already copied, skip (respect priority order)
        if dest_name in seen_names:
            skipped_same_name += 1
            continue

        # if a file with same name already exists in DEST (unlikely except prior runs)
        if dest_path.exists():
            # compare content; if same, skip; else rename with suffix
            src_hash = file_sha256(faa)
            dst_hash = file_sha256(dest_path)
            if src_hash == dst_hash:
                skipped_same_name += 1
                continue
            # rename to include source tag before extension
            stem = dest_path.stem
            suffix = dest_path.suffix
            dest_name = f"{stem}__{sdir.name}{suffix}"
            dest_path = DEST_DIR / dest_name
            renamed_due_conflict += 1

        shutil.copy2(faa, dest_path)
        seen_names.add(dest_name)
        copied += 1

        # build index row (genome, gene)
        stem = dest_name[:-4] if dest_name.lower().endswith('.faa') else dest_name
        # genome is everything up to last underscore
        if '_' in stem:
            genome = stem.split('_')[0]
            gene = stem[len(genome)+1:]
        else:
            genome = stem
            gene = ''
        index_rows.append({
            'filename': dest_name,
            'genome': genome,
            'gene': gene,
            'source_dir': sdir.name,
            'original_path': str(faa),
        })

# write index CSV
with (DEST_DIR / 'index.csv').open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['filename','genome','gene','source_dir','original_path'])
    writer.writeheader()
    writer.writerows(index_rows)

print(f"Consolidation complete -> {DEST_DIR}")
print(f"  Copied: {copied}")
print(f"  Skipped same-name (priority kept): {skipped_same_name}")
print(f"  Renamed due to content conflicts: {renamed_due_conflict}")
print(f"  Index: {DEST_DIR / 'index.csv'}")
