# Pedigree Simulation and Inbreeding Coefficient Calculation

This repository contains a Python script for simulating pedigrees and calculating inbreeding coefficients for individuals in last generations.

## Requirements

- Python 3.7 or higher
- Libraries:
  - `pandas`
  - `numpy`
  - `argparse`

## Usage
Run the script using command-line arguments:
```bash
python3 inbreedingSimulator.py <female> <male> <num_gens> <rep> <migration_rate> [--max_child_mean <value>] [--mean_children_per_couple <value>]
```

- `<female>` : Number of females in the initial population.
- `<male>` : Number of males in the initial population.
- `<num_gens>` : Number of generations to simulate.
- `<rep> `: Number of simulation replicates.
- `<migration_rate>` : Incoming individuals fraction per generation (0 to 1). 
- `--max_child_mean` : Maximum mean number of children per couple (default: 7).
- `--mean_children_per_couple` : Mean number of children per couple (default: 2).

## Example:
```bash
python3 inbreedingSimulator.py 50 50 10 5 0.05
 ```
or

```bash
python3 inbreedingSimulator.py 50 50 10 5 0.05 --max_child_mean 10 --mean_children_per_couple 3

```
## Output Files

- File: "pedigree_`<female>`f_`<male>`m_`<num_gens>`g_`migration_rate>`mig_`<rep>`.csv"
contains the simulated pedigree matrix with genealogical relationships.
  - example: pedigree_50f_50m_10g_mig0.05_1.csv

- File: "female`<female>`_male`<male>`_gen`<num_gens>`_m<`migration_rate>`_r`<rep>`.txt"
lists the inbreeding coefficients for all individuals in the last generation.
  - example: female50_male50_gen10_m0.05_r1.txt
