"""
A script to draw the validation plots.
"""
import pandas as pd
import axelrod as axl
import matplotlib.pyplot as plt

import generate_cache
import theoretic

import functools
import multiprocessing


def simulated_fixation(strategy_pair, N, i=1, repetitions=10,
                       cachefile=None):
    """Run a Moran process and obtain the fixation probabilities"""
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
        if mp.winning_strategy_name == players[0].name:
            win_count += 1

    return win_count / repetitions


def plot_theoretic_vs_simulated(max_N, repetitions, utilities, player1, player2):
    """
    Plot the theoretic value vs the simulated value
    """
    players = (player1, player2)
    ns = range(2, max_N + 1, 2)
    repetitions = repetitions

    player_names = [p.__repr__() for p in players]
    calculated = [theoretic.fixation(player_names, n, n // 2,
                                     utilities=utilities)
                 for n in ns]
    simulated = [simulated_fixation(players,  n, n // 2,
                                    repetitions=repetitions)
                 for n in ns]
    plt.figure()
    plt.plot(ns, calculated, label="Theoretic $x_{N/2}$")
    plt.scatter(ns, simulated, label="Simulated $x_{N/2}$")


    plt.xlabel("Population size $N$")
    plt.title("Fixation probability for {} against {}".format(*player_names))
    plt.xticks(ns)
    plt.legend()
    plt.ylim(0, 1)

    filename = "img/{}_v_{}_{}_repetitions".format(*player_names, repetitions)
    for substr in [".", ": ", ":", " "]:  # Clean up special characters
        filename = filename.replace(substr, "_")
    filename += ".pdf"
    filename = "../" + filename

    plt.savefig(filename)


if __name__ == "__main__":

    outcomes_file = "../data/outcomes.csv"

    player_pairs = [(axl.ALLCorALLD(), axl.Cooperator()),
                    (axl.ALLCorALLD(), axl.Defector()),
                    (axl.ALLCorALLD(), axl.TitForTat()),
                    (axl.Alternator(), axl.Cooperator()),
                    (axl.Alternator(), axl.Defector()),
                    (axl.Alternator(), axl.TitForTat()),
                    (axl.Alternator(), axl.WinStayLoseShift()),
                    (axl.Alternator(), axl.WinStayLoseShift()),
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

    func = functools.partial(plot_theoretic_vs_simulated, max_N, repetitions,
                             utilities)
    p = multiprocessing.Pool(processes)

    p.starmap(func, player_pairs)
