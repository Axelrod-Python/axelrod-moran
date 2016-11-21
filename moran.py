# Python 3

from __future__ import print_function

import csv
from pathlib import Path
import sys
import functools
import multiprocessing
import itertools

import axelrod as axl

from strategies import selected_strategies
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

def write_winner(outfilename, turns, noise, names_inv, repetitions,
                 N, i, j, seed=None):
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

    # mp = axl.MoranProcess(initial_population, turns=turns, noise=noise)
    mp = ApproximateMoranProcess(initial_population, cached_outcomes=outcomes,
                                 turns=turns, noise=noise)
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
                    outfilename=None, processes=None):
    """This function conducts many moran processes to empirically estimate
    fixation probabilities. For each pair of strategies, the population consists
    of 1 player of the first type and N-1 players of the second type."""
    if not outfilename:
        outfilename = "sims_{N}.csv".format(N=N)

    # Cache names to reverse winners to ids later
    names_inv = dict(zip([str(p) for p in players], range(len(players))))

    player_indices = range(len(players))
    if processes is None:
        for i in player_indices:
            print(i, len(players))
            for j in player_indices:
                # for seed in range(repetitions):
                    write_winner(outfilename, turns, noise,
                                 names_inv, repetitions, N, i, j)
    else:
        func = functools.partial(write_winner, outfilename,
                                 turns, noise,
                                 names_inv, repetitions, N)
        p = multiprocessing.Pool(processes)
        args = itertools.product(player_indices, player_indices)
        p.starmap(func, args)

def main():
    N = int(sys.argv[1]) # Population size
    try:
        repetitions = int(sys.argv[2])
    except IndexError:
        repetitions = 1000
    turns = 200
    # Make sure the data folder exists
    path = Path("results")
    path.mkdir(exist_ok=True)

    output_players(players)

    run_simulations(N=N, repetitions=repetitions, turns=turns,
                    processes=4)

if __name__ == "__main__":
    # match_outcomes and players are global
    match_outcomes = read_csv("outcomes.csv")
    for k, v in match_outcomes.items():
        match_outcomes[k] = Pdf(v)

    players = [s() for s in axl.all_strategies if axl.obey_axelrod(s())
               and not s().classifier['long_run_time']]

    main()
