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

# For tests
import collections
import tempfile
import unittest


def output_players(players, outfilename="players.csv"):
    """Cache players to disk for later retrieval."""
    rows = [(i, str(player), player.classifier["stochastic"]) for (i, player) in enumerate(players)]
    path = Path("results") / outfilename
    with path.open('w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)


def build_population(players, i, j, weights):
    """Return the population of strategies according to a given weights"""
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
                 N, i, j, repetitions, n=1):
    """
    Write the winner of a Moran process to file
    """

    initial_population = build_population(players, i, j, [n, N-n])

    s1 = str(players[i].clone())
    s2 = str(players[j].clone())

    # Pull out just the interaction we need
    outcomes = dict()
    for pair in [(s1, s1), (s1, s2), (s2, s1), (s2, s2)]:
        outcomes[pair] = match_outcomes[pair]

    mp = ApproximateMoranProcess(initial_population, cached_outcomes=outcomes)

    data = {i: 0, j: 0}
    for seed in range(repetitions):
        axl.seed(seed)
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
                    outfilename=None, processes=None, count=False, n=1):
    """This function conducts many moran processes to empirically estimate
    fixation probabilities. For each pair of strategies, the population consists
    of n player of the first type and N-n players of the second type."""
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
        args = (pair + (reps[i], n) for i, pair in enumerate(player_index_pairs)
                if reps[i] > 0)
        p.starmap(func, args)

def main():
    N = int(sys.argv[1])  # Population size

    try:
        n = sys.argv[2]
    except IndexError:
        n = 1

    try:
        outfilename = sys.argv[4]
    except IndexError:
        outfilename = None

    repetitions = 1000
    # Make sure the data folder exists
    path = Path("results")
    path.mkdir(exist_ok=True)

    output_players(players)

    run_simulations(N=N, repetitions=repetitions, processes=0, count=True,
                    outfilename=outfilename, n=n)

if __name__ == "__main__":
    # match_outcomes and players are global
    # Run with `python moran.py <N> <n> <outcome_file> <filename>`
    try:
        match_outcomes_file = sys.argv[3]
    except IndexError:
        match_outcomes_file = "outcomes.csv"

    match_outcomes = read_csv(match_outcomes_file)
    for k, v in match_outcomes.items():
        match_outcomes[k] = Pdf(v)

    # players are global
    from players import selected_players
    players = selected_players()

    main()


#########
# Tests #
#########


class Test_output_players(unittest.TestCase):
    """Test the output players function"""
    def test_output(self):
        outfile = tempfile.NamedTemporaryFile('w')
        players = [s() for s in axl.demo_strategies]
        output_players(players, outfile.name)
        with open(outfile.name, 'r') as outfile:
            test_output = [row for row in csv.reader(outfile)]
        expected_output = [['0', 'Cooperator', 'False'],
                           ['1', 'Defector', 'False'],
                           ['2', 'Tit For Tat', 'False'],
                           ['3', 'Grudger', 'False'],
                           ['4', 'Random: 0.5', 'True']]
        self.assertEqual(test_output, expected_output)


class Test_build_population(unittest.TestCase):
    """Test the output players function"""
    def test_build_pop(self):
        players = [axl.Cooperator(), axl.Defector()]
        for weights in [(1, 1), (1, 5), (5, 3), (0, 0), (4, 12)]:
            population = build_population(players, 0, 1, weights)
            str_population = [str(p) for p in population]
            self.assertEqual(str_population, ['Cooperator'] * weights[0] +
                                             ['Defector'] * weights[1])


class Test_obtain_current_count(unittest.TestCase):
    """Test the obtain current count function"""
    def test_obtain_current_count(self):
        data = [(0, 1, 0, 5), (0, 1, 1, 1), (0, 2, 0, 1), (0, 2, 1, 3)]
        df = pd.DataFrame(data)
        temp_file = tempfile.NamedTemporaryFile("w")
        df.to_csv(temp_file.name, header=False)
        current_count = obtain_current_count(temp_file.name)
        for pair, count in [((0, 1), 6), ((0, 2), 4)]:
            self.assertEqual(current_count[pair], count)
        temp_file.close()


class Test_write_winner(unittest.TestCase):
    """Test that the output of a given simulation is as expected"""
    global players
    players = [axl.Cooperator(), axl.Defector()]

    global match_outcomes
    players = [axl.Cooperator(), axl.Defector()]
    match_outcomes = {}
    counter = collections.Counter([(5, 0)])
    pdf = Pdf(counter)
    match_outcomes[('Defector', 'Cooperator')] = pdf
    counter = collections.Counter([(0, 5)])
    pdf = Pdf(counter)
    match_outcomes[('Cooperator', 'Defector')] = pdf
    counter = collections.Counter([(3, 3)])
    pdf = Pdf(counter)
    match_outcomes[('Cooperator', 'Cooperator')] = pdf
    counter = collections.Counter([(1, 1)])
    pdf = Pdf(counter)
    match_outcomes[('Defector', 'Defector')] = pdf

    temp_file = tempfile.NamedTemporaryFile()
    names_inv = {"Cooperator": 0, "Defector": 1}

    def test_write_winner(self):
        write_winner(self.temp_file.name, self.names_inv, 2, 0, 1, 10)
        df = pd.read_csv(self.temp_file.name, header=None)
        self.assertEqual(list(df.ix[:, 3]), [0, 10])
        self.temp_file.close()
