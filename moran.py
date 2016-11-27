# Python 3

from __future__ import print_function

import csv
from pathlib import Path
import sys
import functools
import multiprocessing
import itertools

import axelrod as axl
import pandas as pd

from approximate_moran import ApproximateMoranProcess, Pdf
from generate_data import read_csv


def output_players(players, outfilename="players.csv"):
    """Cache players to disk for later retrieval."""
    rows = [(i, str(player), player.classifier["stochastic"]) for (i, player) in enumerate(players)]
    path = Path("results") / outfilename
    with path.open('w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def build_population(i, j, weights):
    # players = [s() for s in selected_strategies()]
    sub_players = players[i], players[j]
    population = []
    for player, weight in zip(sub_players, weights):
        for _ in range(weight):
            population.append(player.clone())
    return population

def obtain_current_count(filename):
    """Count the number of repetitions for a given strategy pair"""
    df = pd.read_csv(filename, header=None, names=["Strategy 1 index",
                                                   "Strategy 2 index",
                                                   "Winner index",
                                                   "Count"])
    counts = {pair: f["Count"].sum()
              for pair, f in df.groupby(["Strategy 1 index",
                                         "Strategy 2 index"])}
    return counts


def write_winner(outfilename, names_inv,
                 N, i, j, repetitions, seed=None):
    """
    Write the winner of a Moran process to file
    """
    if seed:
        axl.seed(seed)  # Seed the process
    initial_population = build_population(i, j, [1, N-1])

    s1 = str(players[i].clone())
    s2 = str(players[j].clone())

    # Pull out just the interaction we need
    outcomes = dict()
    for pair in [(s1, s1), (s1, s2), (s2, s1), (s2, s2)]:
        outcomes[pair] = match_outcomes[pair]

    mp = ApproximateMoranProcess(initial_population, cached_outcomes=outcomes)

    data = {i: 0, j: 0}
    for _ in range(repetitions):
        mp.reset()
        mp.play()
        winner_name = mp.winning_strategy_name
        data[names_inv[winner_name]] += 1

    path = Path("results")
    path = path / outfilename
    outputfile = csv.writer(path.open('a'))
    rows = []
    for winner, count in data.items():
        rows.append([i, j, winner, count])
    for row in rows:
        outputfile.writerow(row)


def run_simulations(N=2, turns=100, repetitions=1000, noise=0,
                    outfilename=None, processes=None, count=False):
    """This function conducts many moran processes to empirically estimate
    fixation probabilities. For each pair of strategies, the population consists
    of 1 player of the first type and N-1 players of the second type."""
    if not outfilename:
        outfilename = "sims_{N}.csv".format(N=N)

    # Obtain current count of obtained values
    if count is True:
        try:
            counts = obtain_current_count("results/" + outfilename)
        except OSError:
            # If file does not exist then don't count
            count = False

    # Cache names to reverse winners to ids later
    names_inv = dict(zip([str(p) for p in players], range(len(players))))

    player_indices = range(len(players))
    if processes is None:
        for i in player_indices:
            for j in player_indices:

                    if i != j:

                        if count is True:
                            reps = repetitions - counts.get((i, j), 0)
                        else:
                            reps = repetitions

                        if reps > 0:
                            write_winner(outfilename, names_inv, N, i, j, reps)
    else:
        if processes == 0:
            processes = multiprocessing.cpu_count()
        func = functools.partial(write_winner, outfilename,
                                 names_inv, N)
        p = multiprocessing.Pool(processes)

        player_index_pairs = [(i, j)
                              for i, j in itertools.product(player_indices,
                                                            player_indices)
                              if i != j]
        if count is True:
            reps = [repetitions - counts.get(pair, 0)
                    for pair in player_index_pairs]
        else:
            reps = [repetitions for pair in player_index_pairs]
        args = (pair + (reps[i],) for i, pair in enumerate(player_index_pairs)
                if reps[i] > 0)
        p.starmap(func, args)

def main():
    N = int(sys.argv[1])  # Population size
    try:
        outfilename = sys.argv[3]
    except IndexError:
        outfilename = None

    repetitions = 1000
    # Make sure the data folder exists
    path = Path("results")
    path.mkdir(exist_ok=True)

    output_players(players)

    run_simulations(N=N, repetitions=repetitions, processes=0, count=True,
                    outfilename=outfilename)

if __name__ == "__main__":
    # match_outcomes and players are global
    # Run with `python moran.py <N> <outcome_file> <filename>`
    try:
        match_outcomes_file = sys.argv[2]
    except IndexError:
        match_outcomes_file = "outcomes.csv"

    match_outcomes = read_csv(match_outcomes_file)
    for k, v in match_outcomes.items():
        match_outcomes[k] = Pdf(v)

    players = [s() for s in axl.all_strategies if axl.obey_axelrod(s())
               and not s().classifier['long_run_time']]

    main()
