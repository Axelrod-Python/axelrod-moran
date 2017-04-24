# Data generation scripts and libraries

This directory contains scripts and libraries for the generation of data.

## Players used in this work

```
$ python moran.py  # Lists the number of players used
172
```

Also contains a function `generate_players` which returns a list of `axelrod`
player instances.

## Theoretic results

The file `theoretic.py` contains a number of functions used for the calculation
of analytic results for Moran processes.

## Generate the cache.

```
$ python generate_cache.py
```

This generates two data files in `../data`:

- `outcomes.csv`
- `outcomes_noise.csv`

These files are of the format:

```csv
player1_name, player2_name, player1_score, player2_score, count
```

where `count` is the number of times that particular score pair occurs.

Also contains a function `read_csv` which reads in the file to give nested
dictionaries of match outcomes.

## Run the Moran processes

The file `moran.py` is used to generate data files for the Moran process.

```
$ python moran.py 4 2 ../data/outcomes.csv ../data/sims_n_over_2/ sims_4.csv
```

This will run the Moran process for all pairs of players in a population of size
4 and 2 players of the first type. A cached outcome of match results if read
from `../data/outcomes.csv` and the output is `..data/sims_4.csv`.

## Clean the data

The file `clean_raw_moran.py` is used to clean all the data generated from
`moran.py`. Creates one data file `..data/sims_summary.csv` of the form:

```
Noise, P1, P2, N, repetitions, P1_fixation, P2_fixation
```

The file `write_fitness.py` is used to write the relative fitness for each
strategy pair to `..data/relative_fitness.csv`:

```
player, opponent, N, noise, r_1, r_{N/2}, r_{N-1}
```

Where:

- `r_1`: is relative fitness of 1 player with N - 1 opponents
- `r_{N/2}`: is relative fitness of N/2 players with N/2 opponents
- `r_{N-1}`: is relative fitness of N-1 players with 1 opponent.

**Fitness is automatically re written when running `clean_raw_moran.py`**.
