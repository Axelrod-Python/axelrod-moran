
from collections import defaultdict
import csv
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def load_player_data():
    """Loads the list of player names."""
    names = []
    path = Path("results") / "players.csv"
    with path.open() as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            i, player_name, det = line
            names.append(player_name)
    return names

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
        # l[j].append(1-v)

    # Sort by median
    centers = [(central_function(l[i]), i) for i in range(N)]
    centers.sort(reverse=True)
    domain = [y for (x, y) in centers]

    names = load_player_data()
    ranked_names = [names[y] for (x, y) in centers]

    l2 = []
    for i in domain:
        l2.append(l[i])
    if reverse:
        domain = list(reversed(domain))
        ranked_names = list(reversed(ranked_names))
    return domain, ranked_names

def pairwise_heatmap(results, pop_size):
    """Heatmap for the given population size for all players versus all other
    players."""

    domain, ranked_names = sort_results(results, reverse=True)

    player_names = load_player_data()
    n = len(domain)
    # print(n, len(domain))
    xs = list(reversed(range(n)))
    ys = list(range(n))
    cs = np.zeros((n, n))
    for i in reversed(domain):
        for j in domain:
            if i == j:
                cs[i][j] = 1.
            # elif i < j:
            r = results[(i, j)]
            cs[i][j] = pop_size * r
            # else:
            #     r = results[(j, i)]
            #     cs[i][j] = pop_size * (1 - r)

    ax = plt.pcolor(xs, ys, cs, cmap=plt.cm.viridis)
    plt.colorbar()
    plt.xlim((0, n))
    plt.ylim((0, n))
    plt.xticks(range(n), reversed(ranked_names), rotation=90)
    plt.yticks(range(n), ranked_names)
    # plt.tight_layout()
    return ax

def fixation_boxplots(results, pop_size=None):
    """Plot the boxplots of the fixation probability distributions of each
    player, sorted by median."""
    n = max(k[1] for k in results.keys()) + 1
    l = [[] for _ in range(n)]
    for k, v in results.items():
        i, j = k
        l[i].append(v)
        l[j].append(1-v)

    # Sort by median
    centers = [(np.median(l[i]), i) for i in range(n)]
    centers.sort(reverse=True)
    domain = [y for (x, y) in centers]

    names = load_player_data()
    ranked_names = []

    l2 = []
    for i in domain:
        l2.append(l[i])
        ranked_names.append(names[i])

    plt.boxplot(l2, notch=False, showcaps=False, showfliers=False,
                conf_intervals=None, bootstrap=1)
    plt.xticks(range(n), ranked_names, rotation=90)
    plt.xlim((0, n))
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

def versus_heatmap(player_name, pop_sizes=range(2, 15), all_results=None):
    """Make a heatmap of the player_name's fixation probabilities versus all
    other players versus population size."""

    if not all_results:
        all_results = combine_all_results(pop_sizes)

    player_names = load_player_data()
    n = len(player_names)

    player_index = None
    for i, name in enumerate(player_names):
        if player_name == name:
            player_index = i
            break

    xs = list(pop_sizes)
    ys = list(range(n))
    cs = np.zeros((len(xs), len(ys)))

    i = player_index
    lower = pop_sizes[0]
    for pop_size in pop_sizes:
        results = all_results[pop_size]
        for j in range(n):
            if i == j:
                cs[pop_size-lower][j] = 1. / pop_size
            # elif i < j:
            r = results[(i, j)]
            cs[pop_size-lower][j] = r
            # else:
            #     r = results[(j, i)]
            #     cs[pop_size - lower][j] = 1 - r

    ax = plt.pcolor(xs, ys, cs.transpose(), cmap=plt.cm.viridis)
    plt.xlim(pop_sizes[0], pop_sizes[-1] + 1)
    plt.ylim((0, n))
    #names = [str(p) for p in players]
    #plt.xticks(range(n), reversed(ranked_names), rotation=90)
    plt.yticks(range(n), player_names)
    plt.colorbar()
    plt.tight_layout()
    return ax

def combine_all_results(pop_sizes=range(2, 15)):
    l = dict()
    for pop_size in pop_sizes:
        try:
            path = Path("results2") / "sims_{i}.csv".format(i=pop_size)
            results = combine_data(str(path))
            l[pop_size] = results
        except IOError:
            continue
    return l

if __name__ == "__main__":
    results = combine_data()
    best_strategy(results)
