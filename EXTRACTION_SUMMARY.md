# Extraction Summary - 5 Genomes

## Date
December 1, 2025

## Genomes Analyzed
1. NZ_CP107120
2. NZ_CP107134.1
3. NZ_CP107164
4. NZ_CP107178.1
5. NZ_HG941718

## Extraction Results

### ✅ Successfully Extracted (31 proteins total: 20 efflux/regulatory + 11 resistance genes)

#### Efflux Pump Genes (3 per genome = 15 total)
- **Escherichia_coli_acrA** (Adapter protein) - 5 genomes
- **acrB** (Pump subunit) - 5 genomes  
- **tolC** (Outer channel) - 5 genomes

#### Regulatory Genes (1 per genome = 5 total)
- **marA** (Global regulator) - 5 genomes

#### Beta-Lactamase Resistance Genes (11 proteins from 4 genomes)
- **CTX-M-15** (ESBL - Ceftriaxone resistance) - 3 genomes (NZ_CP107120, NZ_CP107134.1, NZ_CP107178.1)
- **OXA-1** (Beta-lactamase) - 3 genomes (NZ_CP107120, NZ_CP107134.1, NZ_CP107178.1)
- **CMY-59** (AmpC Beta-lactamase) - 1 genome (NZ_HG941718)

#### Aminoglycoside Resistance Genes
- **AAC(6')-Ib-cr** (Aminoglycoside + Quinolone resistance) - 3 genomes (NZ_CP107120, NZ_CP107134.1, NZ_CP107178.1)
- **AAC(3)-IIe** (Aminoglycoside resistance) - 1 genome (NZ_CP107120)

**Output locations:**
- Efflux/regulatory genes: `results_5genomes/` (20 files)
- Beta-lactamase/resistance genes: `results_resistance_genes/` (11 files)

### ❌ Genes NOT Found in These Genomes

#### Beta-Lactamases (Carbapenemases)
- **blaTEM** (Penicillinase) - NOT FOUND
- **blaNDM** (Carbapenemase - Meropenem resistance) - NOT FOUND
- **blaKPC** (Carbapenemase) - NOT FOUND

#### Tetracycline and Colistin Resistance
- **tet(A)** (Tetracycline efflux) - NOT FOUND
- **mcr-1** (Colistin/Polymyxin resistance) - NOT FOUND

#### Additional Efflux/Regulatory Genes
- **acrR** (Local repressor of AcrAB) - NOT FOUND
- **marR** (Global regulator repressor) - NOT FOUND

#### Quinolone Resistance Genes
- **gyrA** (Fluoroquinolone resistance, S83L/D87N mutations) - NOT FOUND
- **parC** (Fluoroquinolone resistance, S80I mutation) - NOT FOUND

## Analysis

### Why Are Beta-Lactamases Missing?
These 5 genomes likely represent:
1. **Wild-type or susceptible E. coli strains** without acquired beta-lactamase resistance genes
2. **Non-clinical isolates** that haven't been exposed to beta-lactam antibiotics
3. Strains from environments where beta-lactam resistance hasn't been selected for

The beta-lactamase genes (blaCTX-M, blaTEM, blaNDM, blaKPC) are **acquired resistance genes** often found on plasmids or mobile genetic elements. They are not core chromosomal genes.

### Why Are gyrA and parC Missing?
The CARD database (used by ABRicate) focuses on **acquired resistance genes** and known resistance mutations. The chromosomal genes `gyrA` and `parC` are present in all E. coli but:
- ABRicate may only report them if **specific resistance mutations** (S83L, D87N, S80I) are detected
- Wild-type sequences without resistance mutations may not be annotated

### Why Is marR Missing but marA Present?
- **marA** is annotated because it's the **activator** that directly causes multidrug resistance
- **marR** (the repressor) may not be in the CARD database as a primary resistance determinant
- CARD focuses on genes that confer resistance, not their negative regulators

## Recommendations

### To Find Beta-Lactamase Genes:
1. **Analyze clinical MDR isolates** from hospitals (especially ICU patients)
2. Look for genomes from regions with high carbapenem resistance (India, China, Mediterranean)
3. Search for genomes annotated as "ESBL-producing" or "carbapenem-resistant"

### To Find Quinolone Resistance:
1. Use tools like **PointFinder** (detects point mutations in chromosomal genes)
2. Run whole-genome alignment to reference sequences
3. Extract gyrA/parC directly from genome assemblies and look for specific codons

### Alternative Gene Names in CARD:
- Note that `acrA` is annotated as `Escherichia_coli_acrA` in these genomes
- Always check CARD database naming conventions for your organism

## Output Location
All extracted protein sequences are in: `results_5genomes/`

## Next Steps
If you need beta-lactamase genes or quinolone resistance genes:
1. Provide genomes that are known MDR/ESBL/carbapenem-resistant strains
2. Or I can help you extract gyrA/parC directly from the genome assemblies (they're core genes)
3. Run PointFinder or similar tools to detect resistance-conferring mutations
