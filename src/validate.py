"""
A script to draw the validation plots.
"""
import pandas as pd
import axelrod as axl
import matplotlib.pyplot as plt
import csv

import generate_cache
import theoretic

import functools
import multiprocessing
import itertools


def simulated_fixation(strategy_pair, N, i=1, repetitions=10,
                       cachefile=None):
    """Run an approximate Moran process and obtain the fixation probabilities"""
    if cachefile is None:
        cachefile = "../data/outcomes.csv"

    cache = generate_cache.read_csv(cachefile)
    for k, v in cache.items():
        cache[k] = axl.Pdf(v)

    players = []
    for _ in range(i):
        players.append(strategy_pair[0])
    for _ in range(N - i):
        players.append(strategy_pair[1])
    mp = axl.ApproximateMoranProcess(players, cached_outcomes=cache)

    win_count = 0
    for seed in range(repetitions):
        axl.seed(seed)
        mp.reset()
        mp.play()
        if mp.winning_strategy_name == str(players[0]):
            win_count += 1

    return win_count / repetitions


def theoretic_vs_simulated(repetitions, utilities, filename,
                           N, player1, player2):
    """
    Return the theoretic values and the simulated values
    """
    players = (player1, player2)

    starting_pop = [1, N // 2, N - 1] if N != 2 else [1]

    for i in starting_pop:
        player_names = [str(p) for p in players]
        t = theoretic.fixation(player_names, N, i, utilities=utilities)
        s = simulated_fixation(players,  N, i, repetitions=repetitions)

        with open(filename, "a") as f:
            writer = csv.writer(f)
            writer.writerow([repetitions, N, i, *player_names, t, s])


if __name__ == "__main__":

    outcomes_file = "../data/outcomes.csv"
    output_file = "../data/fixation_validation.csv"
    with open(output_file, "w") as f:
        f.write("Repetitions,N,i,Player 1,Player 2,Theoretic,Simulated\n")

    player_pairs = [(axl.Defector(), axl.Defector()),
                    (axl.Defector(), axl.Alternator()),
                    (axl.Defector(), axl.Cooperator()),
                    (axl.Defector(), axl.TitForTat()),
                    (axl.Defector(), axl.WinStayLoseShift()),
                    (axl.Random(), axl.Random()),
                    (axl.Random(), axl.ZDExtort2()),
                    (axl.Random(), axl.GTFT()),
                    (axl.Random(), axl.ALLCorALLD()),
                    (axl.Random(), axl.PSOGambler2_2_2()),
                    (axl.Cooperator(), axl.Random()),
                    (axl.Cooperator(), axl.ZDExtort2()),
                    (axl.Cooperator(), axl.GTFT()),
                    (axl.Cooperator(), axl.ALLCorALLD()),
                    (axl.Cooperator(), axl.PSOGambler2_2_2()),
                    (axl.Alternator(), axl.Random()),
                    (axl.Alternator(), axl.ZDExtort2()),
                    (axl.Alternator(), axl.GTFT()),
                    (axl.Alternator(), axl.ALLCorALLD()),
                    (axl.Alternator(), axl.PSOGambler2_2_2()),
                    (axl.ALLCorALLD(), axl.Cooperator()),
                    (axl.ALLCorALLD(), axl.Defector()),
                    (axl.ALLCorALLD(), axl.TitForTat()),
                    (axl.Alternator(), axl.Cooperator()),
                    (axl.Alternator(), axl.Defector()),
                    (axl.Alternator(), axl.TitForTat()),
                    (axl.Alternator(), axl.WinStayLoseShift()),
                    (axl.Defector(), axl.WinStayLoseShift()),
                    (axl.Calculator(), axl.ALLCorALLD()),
                    (axl.Calculator(), axl.ArrogantQLearner()),
                    (axl.Calculator(), axl.Random()),
                    (axl.Cooperator(), axl.TitForTat()),
                    (axl.Defector(), axl.Cooperator()),
                    (axl.Defector(), axl.TitForTat()),
                    (axl.Random(), axl.Cooperator()),
                    (axl.Random(), axl.Defector()),
                    (axl.Random(), axl.TitForTat()),
                    (axl.WinStayLoseShift(), axl.TitForTat())]


    max_N = 20
    repetitions = 1000

    df = pd.read_csv(outcomes_file, header=None,
                     names=["Player 1", "Player 2",
                            "Score 1", "Score 2", "Iteration"])

    utilities = {pair: (f["Score 1"].mean(), f["Score 2"].mean())
                 for pair, f in df.groupby(["Player 1", "Player 2"])}

    processes = multiprocessing.cpu_count()

    func = functools.partial(theoretic_vs_simulated, repetitions,
                             utilities, output_file)
    p = multiprocessing.Pool(processes)

    args = ((N, *players)
            for N, players in itertools.product(range(2, max_N + 1, 2),
                                                player_pairs))
    p.starmap(func, args)
