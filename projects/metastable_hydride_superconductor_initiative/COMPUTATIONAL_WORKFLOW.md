# Computational Workflow

## Objective

Build a reproducible computational pipeline for evaluating hypothetical metastable hydride derivative phases.

## Workflow Overview

1. Structure acquisition
2. Candidate derivative generation
3. DFT relaxation
4. Formation energy calculation
5. Competing phase comparison
6. Hydrogen insertion pathway analysis
7. Phonon stability
8. Electronic structure
9. Electron-phonon coupling
10. Candidate ranking

## Tools

**Primary:**

- Quantum ESPRESSO
- ASE
- phonopy
- pymatgen
- spglib

**Possible later tools:**

- EPW
- VASP if licensed
- Materials Project API
- AFLOW / OQMD data
- Jupyter / Colab notebooks
- HPC cluster

## Directory Design

```
simulations/
├── qe/
│   ├── parent_mg2irh5/
│   └── candidate_mg2irh6/
├── ase/
│   ├── build_structures.py
│   └── relax_workflow.py
├── neb/
│   └── hydrogen_insertion_pathway/
└── phonons/
    ├── parent/
    └── candidate/
```

## Candidate Evaluation Gates

| Gate | Criterion |
|------|-----------|
| 1 | Structure relaxes without unphysical distortion |
| 2 | Formation energy is not obviously impossible relative to competing phases |
| 3 | No major imaginary phonon modes after relaxation |
| 4 | Electronic structure has plausible Fermi-level density of states |
| 5 | Electron-phonon coupling merits deeper study |
| 6 | Synthesis pathway is not obviously impossible or unsafe |

## Candidate Ranking

Rank candidates by:

- dynamic stability
- metastability window
- hydrogen insertion barrier
- electronic density of states
- electron-phonon coupling potential
- synthesis feasibility
- safety profile
- novelty

## Reproducibility Standards

Every computational run should record:

- code version
- pseudopotentials
- exchange-correlation functional
- k-point mesh
- energy cutoff
- convergence thresholds
- structure source
- relaxation settings
- run date
- machine/environment
- output path
