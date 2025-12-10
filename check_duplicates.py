import pandas as pd

# Check Excel for duplicates
df = pd.read_excel('MASTER_Gene_Presence_Absence.xlsx', sheet_name='Complete_Gene_Matrix')

print(f'Total rows in Excel: {len(df)}')
print(f'Unique genes: {df["Gene"].nunique()}')

# Check for duplicate gene names
dupes = df[df.duplicated(subset=['Gene'], keep=False)]

if len(dupes) > 0:
    print(f'\nDUPLICATE GENES FOUND: {len(dupes)} rows')
    print('\nDuplicate gene details:')
    print(dupes[['Gene', 'Database', 'Category']].sort_values('Gene').to_string(index=False))
    
    # Show which genes are duplicated
    dupe_genes = dupes['Gene'].unique()
    print(f'\n{len(dupe_genes)} genes appear multiple times:')
    for gene in sorted(dupe_genes):
        count = len(df[df['Gene'] == gene])
        print(f'  {gene}: {count} times')
else:
    print('\n✓ No duplicate genes in Excel.')

# Also check the CSV index
print('\n--- Checking results_all_genes/index.csv ---')
csv_df = pd.read_csv('results_all_genes/index.csv')
print(f'Total files in index: {len(csv_df)}')
print(f'Unique filenames: {csv_df["filename"].nunique()}')

csv_dupes = csv_df[csv_df.duplicated(subset=['filename'], keep=False)]
if len(csv_dupes) > 0:
    print(f'\nDUPLICATE FILENAMES IN INDEX: {len(csv_dupes)} rows')
    print(csv_dupes[['filename', 'source_dir']].to_string(index=False))
else:
    print('\n✓ No duplicate filenames in index.')
