
from collections import defaultdict
import csv
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

import axelrod as axl
import moran

def get_strategies():
    strategies = moran.get_strategies()
    return [s() for s in strategies]

def load_data(filename):
    """Opens sim_*.csv files."""
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            yield map(int, line)

def combine_data(filename="sims_2.csv"):
    """Aggregates data for all the matches in the simulation files."""
    d = defaultdict(int)
    count = defaultdict(int)
    for line in load_data(filename):
        i, j, w = line
        count[(i, j)] += 1
        if i == w:
            d[(i, j)] += 1
    results = dict()
    for k, v in count.items():
        results[k] = d[k] / float(count[k])
    return results

def sort_results(results, reverse=False, central_function=np.median):
    N = max(k[1] for k in results.keys()) + 1
    l = [[] for _ in range(N)]
    for k, v in results.items():
        i, j = k
        l[i].append(v)
        l[j].append(1-v)

    # Sort by median
    centers = [(central_function(l[i]), i) for i in range(N)]
    centers.sort(reverse=True)
    domain = [y for (x, y) in centers]

    players = get_strategies()
    names = [str(p) for p in players]
    ranked_names = [names[y] for (x, y) in centers]


    #players = get_strategies()
    #names = [str(p) for p in players]
    #ranked_names = []

    l2 = []
    for i in domain:
        l2.append(l[i])
        #ranked_names.append(names[i])
    if reverse:
        domain = list(reversed(domain))
        ranked_names = list(reversed(ranked_names))
    return domain, ranked_names

def pairwise_heatmap(results, pop_size):
    """Heatmap for the given population size for all players versus all other
    players."""

    domain, ranked_names = sort_results(results, reverse=True)

    players = get_strategies()
    N = len(players)
    xs = list(reversed(range(N)))
    ys = list(range(N))
    cs = np.zeros((N, N))
    for i in reversed(domain):
        for j in domain:
            if i == j:
                cs[i][j] = 1.
            else:
                try:
                    r = results[(i, j)]
                except KeyError:
                    r = results[(j, i)]
                cs[i][j] = pop_size * r
                cs[j][i] = pop_size * (1. - r)
    ax = plt.pcolor(xs, ys, cs, cmap=plt.cm.viridis)
    plt.xlim((0, N))
    plt.ylim((0, N))
    #names = [str(p) for p in players]
    plt.xticks(range(N), reversed(ranked_names), rotation=90)
    plt.yticks(range(N), ranked_names)
    plt.colorbar()
    plt.tight_layout()
    return ax

def fixation_boxplots(results, pop_size=None):
    """Plot the boxplots of the fixation probability distributions of each
    player, sorted by median."""
    N = max(k[1] for k in results.keys()) + 1
    l = [[] for _ in range(N)]
    for k, v in results.items():
        i, j = k
        l[i].append(v)
        l[j].append(1-v)

    # Sort by median
    centers = [(np.median(l[i]), i) for i in range(N)]
    centers.sort(reverse=True)
    domain = [y for (x, y) in centers]

    players = get_strategies()
    names = [str(p) for p in players]
    ranked_names = []

    l2 = []
    for i in domain:
        l2.append(l[i])
        ranked_names.append(names[i])

    plt.boxplot(l2, notch=False, showcaps=False, showfliers=False,
                conf_intervals=None, bootstrap=1)
    plt.xticks(range(N), ranked_names, rotation=90)
    plt.xlim((0, N))
    if pop_size:
        plt.axhline(1. / pop_size, color="black")
        plt.axhline(1 - 1. / pop_size, color="black")

def ranks_versus_population(pop_sizes=range(2, 14)):
    ranks = defaultdict(list)

    for popsize in pop_sizes:
        path = Path("sims_{i}.csv".format(i=popsize))
        results = analyze.combine_data(str(path))
        domain, ranked_names = analyze.sort_results(results, reverse=True)
        for i, name in enumerate(ranked_names):
            ranks[name].append(i)

    fig, ax = plt.subplots()
    for name, values in ranks.items():
        ax.plot(range(2, 2 + len(values)), values)
    plt.xlabel("Population Size")
    initial_names = [(v[0], k) for k, v in ranks.items()]
    initial_names.sort()
    names = [k for (v, k) in initial_names]
    plt.yticks(range(len(names)), names)
    plt.ylim(0, len(names)-1)

    ax2 = ax.twinx()
    final_names = [(v[-1], k) for k, v in ranks.items()]
    final_names.sort()
    names = [k for (v, k) in final_names]
    plt.yticks(range(len(names)), names)

    plt.show()



def versus_heatmap(player_name, pop_sizes=range(2, 14)):
    """Make a heatmap of the player_name's fixation probabilities versus all
    other players versus population size."""

    players = get_strategies()
    player_names = [str(p) for p in players]
    N = len(players)
    xs = list(pop_sizes)

    player_index = None
    for i, name in enumerate(player_names):
        if player_name == name:
            player_index = i
            break

    ys = list(range(N))
    cs = np.zeros((len(xs), len(ys)))

    for pop_size in pop_sizes:
        i = player_index
        path = Path("sims_{i}.csv".format(i=pop_size))
        results = combine_data(str(path))

        for j in range(N):
            if i == j:
                cs[pop_size][j] = 1.
            else:
                try:
                    r = results[(i, j)]
                    cs[pop_size][j] = pop_size * r
                except KeyError:
                    r = results[(j, i)]
                    cs[pop_size][j] = pop_size * (1. - r)

    ax = plt.pcolor(xs, ys, cs, cmap=plt.cm.viridis)
    plt.xlim(pop_sizes[0], pop_sizes[-1])
    plt.ylim((0, N))
    #names = [str(p) for p in players]
    #plt.xticks(range(N), reversed(ranked_names), rotation=90)
    plt.yticks(range(N), player_names)
    plt.colorbar()
    plt.tight_layout()
    return ax


if __name__ == "__main__":
    results = combine_data()
    #ax = prep_heatmap(results, pop_size)
    #plt.show()
    best_strategy(results)
