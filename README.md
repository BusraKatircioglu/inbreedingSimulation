# Pedigree Simulation and Inbreeding Coefficient Calculation

This repository contains a Python script for simulating pedigrees and calculating inbreeding coefficients for individuals in last generations.

## Requirements

- Python 3.7 or higher
- Libraries:
  - `pandas`
  - `numpy`
  - `argparse`
  - `csv`

## Usage
Run the script using command-line arguments:
```bash
python3 inbreedingSimulation.py <female> <male> <num_gens> <rep> <migration_rate>
```
- `<female>` : Number of females in the initial population.
- `<male>` : Number of males in the initial population.
- `<num_gens>` : Number of generations to simulate.
- `<rep> `: Number of simulation replicates.
- `<migration_rate>` : Incoming individuals fraction per generation (0 to 1).

## Example:
```
python3 inbreedingSimulation.py 50 50 10 5 0.05
```

## Output Files

- File: "pedigree_`<female>`f_`<male>`m_`<num_gens>`g_`migration_rate>`mig_`<rep>`.csv"
contains the simulated pedigree matrix with genealogical relationships.

- File: "female`<female>`_male`<male>`_gen`<num_gens>`_m<`migration_rate>`_r`<rep>`.txt"
lists the inbreeding coefficients for all individuals in the final generation.
