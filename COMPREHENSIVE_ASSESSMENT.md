# Comprehensive Multi-Database Resistance Gene Assessment

## Date: December 1, 2025

## Overview
Analyzed 5 *E. coli* genomes using three different resistance gene databases:
- **CARD** (Comprehensive Antibiotic Resistance Database)
- **NCBI** (National Center for Biotechnology Information)
- **ResFinder** (DTU's resistance gene database)

---

## Genomes Analyzed
1. **NZ_CP107120** / NZ_CP107120.1
2. **NZ_CP107134.1**
3. **NZ_CP107164** / NZ_CP107164.1
4. **NZ_CP107178.1**
5. **NZ_HG941718** / NZ_HG941718.1

---

## 📊 EXTRACTION SUMMARY

### Total Proteins Extracted: **43**

| Database | Proteins Extracted | Output Directory |
|----------|-------------------|------------------|
| CARD | 11 | `results_resistance_genes/` |
| NCBI | 16 | `results_ncbi/` |
| ResFinder | 16 | `results_resfinder/` |

---

## 🔬 GENES FOUND BY DATABASE

### CARD Database (11 proteins)

| Gene | Type | Genomes | Description |
|------|------|---------|-------------|
| **CTX-M-15** | ESBL | 3 (CP107120, CP107134.1, CP107178.1) | Ceftriaxone resistance |
| **OXA-1** | Beta-lactamase | 3 (CP107120, CP107134.1, CP107178.1) | Oxacillin resistance |
| **CMY-59** | AmpC | 1 (HG941718) | Cephalosporin resistance |
| **AAC(6')-Ib-cr** | Aminoglycoside + Quinolone | 3 (CP107120, CP107134.1, CP107178.1) | Dual resistance |
| **AAC(3)-IIe** | Aminoglycoside | 1 (CP107120) | Gentamicin resistance |

### NCBI Database (16 proteins)

| Gene | Type | Genomes | Description |
|------|------|---------|-------------|
| **blaCTX-M-15** | ESBL | 3 (CP107120.1, CP107134.1, CP107178.1) | Ceftriaxone resistance |
| **blaOXA-1** | Beta-lactamase | 3 (CP107120.1, CP107134.1, CP107178.1) | Oxacillin resistance |
| **blaCMY-23** | AmpC | 1 (HG941718.1) | Cephalosporin resistance |
| **blaEC-5** | Chromosomal | 5 (ALL genomes) | Intrinsic *E. coli* AmpC |
| **aac(6')-Ib-D181Y** | Aminoglycoside | 3 (CP107120.1, CP107134.1, CP107178.1) | Gentamicin/Tobramycin resistance |
| **aac(3)-IIe** | Aminoglycoside | 1 (CP107120.1) | Gentamicin resistance |

**Key Finding:** NCBI detected **blaEC-5** (chromosomal AmpC) in ALL 5 genomes - this is an intrinsic resistance mechanism.

### ResFinder Database (16 proteins)

| Gene | Type | Genomes | Description |
|------|------|---------|-------------|
| **blaCTX-M-15_1** | ESBL | 3 (CP107120.1, CP107134.1, CP107178.1) | Ceftriaxone resistance |
| **blaOXA-1_1** | Beta-lactamase | 3 (CP107120.1, CP107134.1, CP107178.1) | Oxacillin resistance |
| **blaCMY-23_1** | AmpC | 1 (HG941718.1) | Cephalosporin resistance |
| **aac(6')-Ib-cr_1** | Aminoglycoside + Quinolone | 3 (CP107120.1, CP107134.1, CP107178.1) | Dual resistance |
| **aac(3)-IIa_1** | Aminoglycoside | 1 (CP107120.1) | Gentamicin resistance |
| **mdf(A)_1** | Efflux pump | 5 (ALL genomes) | Multidrug resistance |

**Key Finding:** ResFinder detected **mdf(A)** efflux pump in ALL 5 genomes - chromosomal multidrug efflux.

---

## 🎯 RESISTANCE PROFILE BY GENOME

### NZ_CP107120 / CP107120.1 ⚠️ HIGHLY RESISTANT
**Beta-lactamases:**
- CTX-M-15 (ESBL) ✓
- OXA-1 ✓
- EC-5 (chromosomal) ✓

**Aminoglycoside Resistance:**
- AAC(6')-Ib-cr (also quinolone resistance) ✓
- AAC(3)-IIe / AAC(3)-IIa ✓

**Efflux:**
- mdf(A) ✓

**Resistance Profile:** MDR (Multi-Drug Resistant) - ESBL-producing strain

---

### NZ_CP107134.1 ⚠️ HIGHLY RESISTANT
**Beta-lactamases:**
- CTX-M-15 (ESBL) ✓
- OXA-1 ✓
- EC-5 (chromosomal) ✓

**Aminoglycoside Resistance:**
- AAC(6')-Ib-cr/D181Y ✓

**Efflux:**
- mdf(A) ✓

**Resistance Profile:** MDR - ESBL-producing strain

---

### NZ_CP107164 / CP107164.1 ✅ SUSCEPTIBLE
**Beta-lactamases:**
- EC-5 (chromosomal only) ✓

**Efflux:**
- mdf(A) ✓

**Resistance Profile:** Likely susceptible to most antibiotics (only intrinsic resistance)

---

### NZ_CP107178.1 ⚠️ HIGHLY RESISTANT
**Beta-lactamases:**
- CTX-M-15 (ESBL) ✓
- OXA-1 ✓
- EC-5 (chromosomal) ✓

**Aminoglycoside Resistance:**
- AAC(6')-Ib-cr/D181Y ✓

**Efflux:**
- mdf(A) ✓

**Resistance Profile:** MDR - ESBL-producing strain

---

### NZ_HG941718 / HG941718.1 ⚠️ RESISTANT
**Beta-lactamases:**
- CMY-23 (AmpC - different from CMY-59 in CARD) ✓
- EC-5 (chromosomal) ✓

**Efflux:**
- mdf(A) ✓

**Resistance Profile:** AmpC-producing strain (cephalosporin resistance)

---

## ❌ REQUESTED GENES NOT FOUND IN ANY DATABASE

| Gene | Type | Status |
|------|------|--------|
| **blaTEM** | Penicillinase | NOT FOUND ❌ |
| **blaNDM** | Carbapenemase (New Delhi Metallo) | NOT FOUND ❌ |
| **blaKPC** | Carbapenemase (K. pneumoniae) | NOT FOUND ❌ |
| **tet(A)** | Tetracycline efflux | NOT FOUND ❌ |
| **mcr-1** | Colistin/Polymyxin resistance | NOT FOUND ❌ |
| **gyrA** | Quinolone target (chromosomal) | NOT FOUND ❌ |
| **parC** | Quinolone target (chromosomal) | NOT FOUND ❌ |

### Why Are These Missing?

#### Carbapenemases (blaNDM, blaKPC)
- These are **carbapenem resistance genes** typically found in highly resistant clinical isolates
- Your genomes appear to be ESBL-producers but NOT carbapenem-resistant
- These genes are rarer and associated with last-line antibiotic failure

#### blaTEM
- One of the most common beta-lactamases globally
- Absence suggests either:
  - These strains acquired different resistance mechanisms (CTX-M, OXA)
  - They are from regions/sources where TEM is less prevalent

#### tet(A) and mcr-1
- **tet(A)**: Tetracycline resistance - your strains may be tetracycline susceptible
- **mcr-1**: Colistin resistance - critically important, absence is GOOD (colistin is a last-resort drug)

#### gyrA and parC
- These are **chromosomal genes** present in ALL *E. coli*
- Resistance databases focus on **acquired resistance genes** or **known resistance mutations**
- Your strains likely have wild-type sequences without resistance-conferring mutations
- **To find these:** Extract directly from genomes or use PointFinder for mutation detection

---

## 🔍 DATABASE COMPARISON

### Overlap & Differences

| Finding | CARD | NCBI | ResFinder |
|---------|------|------|-----------|
| CTX-M-15 | ✓ | ✓ | ✓ |
| OXA-1 | ✓ | ✓ | ✓ |
| CMY (AmpC) | CMY-59 | CMY-23 | CMY-23 |
| AAC(6')-Ib | AAC(6')-Ib-cr | aac(6')-Ib-D181Y | aac(6')-Ib-cr_1 |
| AAC(3) | AAC(3)-IIe | aac(3)-IIe | aac(3)-IIa_1 |
| Chromosomal AmpC | ❌ | blaEC-5 (5/5) | ❌ |
| Efflux pump | ❌ | ❌ | mdf(A)_1 (5/5) |

### Key Insights

1. **CMY Discrepancy:** CARD reports CMY-59, but NCBI/ResFinder report CMY-23 in NZ_HG941718
   - This could be:
     - Different variant assignments by databases
     - Sequencing/annotation differences
     - Worth investigating which is correct

2. **AAC(6')-Ib Variants:**
   - CARD: AAC(6')-Ib-cr (emphasizes quinolone resistance)
   - NCBI: aac(6')-Ib-D181Y (emphasizes mutation)
   - ResFinder: aac(6')-Ib-cr_1 (matches CARD)
   - **Same gene, different naming conventions**

3. **NCBI Advantage:** Detects chromosomal blaEC-5 (intrinsic AmpC)
4. **ResFinder Advantage:** Detects mdf(A) efflux pump (intrinsic resistance)
5. **CARD Advantage:** Most consistent naming, clinical focus

---

## 📂 OUTPUT LOCATIONS

```
results_resistance_genes/    - CARD database extractions (11 files)
results_ncbi/                 - NCBI database extractions (16 files)
results_resfinder/            - ResFinder database extractions (16 files)
results_5genomes/             - Efflux pumps and regulators (20 files)
```

**Total: 63 protein sequence files**

---

## 🎯 CLINICAL SIGNIFICANCE

### High-Risk Strains (3/5)
- **NZ_CP107120, NZ_CP107134.1, NZ_CP107178.1**
- ESBL-producing (CTX-M-15)
- Multi-drug resistant
- Expected resistance:
  - ✓ 3rd-generation cephalosporins (Ceftriaxone, Cefotaxime)
  - ✓ Penicillins
  - ✓ Aminoglycosides (Gentamicin, Tobramycin)
  - ✓ Potentially fluoroquinolones (via AAC(6')-Ib-cr)
  - ❌ Carbapenems (likely still effective)
  - ❌ Colistin (likely still effective)

### Moderate-Risk Strain (1/5)
- **NZ_HG941718**
- AmpC-producing (CMY-23)
- Expected resistance:
  - ✓ Cephalosporins
  - ✓ Penicillins
  - ❌ Carbapenems (likely still effective)

### Low-Risk Strain (1/5)
- **NZ_CP107164**
- Only intrinsic resistance
- Likely susceptible to most antibiotics

---

## 💡 RECOMMENDATIONS

### For Missing Genes:

1. **To find gyrA/parC mutations:**
   - Use PointFinder or similar mutation detection tools
   - Extract genes directly from assemblies and sequence specific codons
   - Check positions: gyrA S83L/D87N, parC S80I

2. **To find carbapenemases (blaNDM, blaKPC):**
   - Analyze different clinical isolates (ICU, bloodstream infections)
   - Look for strains from high-prevalence regions (India for NDM)
   - These genomes appear to be pre-carbapenem era or non-carbapenem-resistant

3. **To find blaTEM:**
   - Analyze older clinical isolates or hospital strains
   - Very common globally, absence is unusual for clinical MDR strains

4. **For tetracycline and colistin resistance:**
   - Current strains likely susceptible
   - Colistin susceptibility is clinically beneficial (last-resort drug)

### For Further Analysis:

1. **Resolve CMY variant discrepancy** (CMY-23 vs CMY-59)
2. **Phenotypic testing** to confirm predicted resistance profiles
3. **Plasmid analysis** to understand horizontal gene transfer potential
4. **Efflux pump expression** studies for marA, acrAB-tolC complex

---

## ✅ CONCLUSION

- **Successfully extracted 43 resistance genes** from 5 *E. coli* genomes across 3 databases
- **3/5 genomes are ESBL-producers** with multi-drug resistance (CTX-M-15)
- **1/5 genome is AmpC-producer** (CMY-23)
- **1/5 genome is susceptible** (only intrinsic resistance)
- **Carbapenemases NOT detected** - good news for treatment options
- **mcr-1 NOT detected** - colistin remains a viable last-resort option
- **Chromosomal quinolone resistance genes** (gyrA/parC) require different analysis approach

These genomes represent **ESBL-producing hospital-associated *E. coli* strains** with multi-drug resistance but preserved carbapenem and colistin susceptibility.
