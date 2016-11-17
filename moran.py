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

def output_players(players, outfilename="players.csv"):
    """Cache players to disk for later retrieval."""
    rows = [(i, str(player), player.classifier["stochastic"]) for (i, player) in enumerate(players)]
    path = Path("results") / outfilename
    with path.open('w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)

def build_population(i, j, weights):
    players = [s() for s in selected_strategies()]
    players = players[i], players[j]
    population = []
    for player, weight in zip(players, weights):
        for _ in range(weight):
            population.append(player.clone())
    return population

def write_winner(outfilename, turns, noise, names_inv,
                 N, i, j, seed):
    """
    Write the winner of a Moran process to file
    """
    axl.seed(seed)  # Seed the process
    initial_population = build_population(i, j, [1, N-1])

    mp = axl.MoranProcess(initial_population, turns=turns, noise=noise)
    populations = mp.play()
    winner_name = mp.winning_strategy_name

    path = Path("results")
    path = path / outfilename
    outputfile = csv.writer(path.open('a'))
    row = [i, j, names_inv[winner_name]]
    outputfile.writerow(row)

def run_simulations(players, N=2, turns=100, repetitions=1000, noise=0,
                    outfilename=None, processes=None):
    """This function conducts many moran processes to empirically estimate
    fixation probabilities. For each pair of strategies, the population consists
    of 1 player of the first type and N-1 players of the second type."""
    if not outfilename:
        outfilename = "sims_{N}.csv".format(N=N)

    # Cache names to reverse winners to ids later
    names_inv = dict(zip([str(p) for p in players], range(len(players))))

    # For each distinct pair of players, play `repetitions` number of Moran matches
    #for i, player_1 in enumerate(players):
        #print(i, len(players))
        #for j, player_2 in enumerate(players):

    player_indices = range(len(players))
    if processes is None:
        for i in player_indices:
            print(i, len(players))
            for j in player_indices:
                for seed in range(repetitions):
                    write_winner(outfilename, turns, noise,
                                 names_inv, N, i, j, seed)
    else:
        func = functools.partial(write_winner, outfilename,
                                 turns, noise,
                                 names_inv, N)
        p = multiprocessing.Pool(multiprocessing.cpu_count())
        args = itertools.product(player_indices, player_indices,
                                 range(repetitions))
        p.starmap(func, args)

def main():
    N = int(sys.argv[1]) # Population size
    try:
        repetitions = int(sys.argv[2])
    except IndexError:
        repetitions = 1000
    turns = 100
    # Make sure the data folder exists
    path = Path("results")
    path.mkdir(exist_ok=True)

    strategies = [s() for s in selected_strategies()]
    output_players(strategies)

    run_simulations(strategies, N=N, repetitions=repetitions, turns=turns,
                    processes=True)

if __name__ == "__main__":
    main()
