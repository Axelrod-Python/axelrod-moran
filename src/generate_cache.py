from collections import defaultdict, Counter
import csv
import functools
import multiprocessing
import os

import axelrod as axl
#from approximate_moran import *

def write_csv(outcomes, filename="outcomes.csv", append=False):
    s = 'w'
    if append:
        s = 'a'
    writer = csv.writer(open(filename, s))
    for pair, counter in outcomes.items():
        for scores, count in counter.items():
            row = [pair[0], pair[1], scores[0], scores[1], count]
            writer.writerow(row)

def read_csv(filename="outcomes.csv"):
    reader = csv.reader(open(filename))
    outcomes = defaultdict(Counter)
    for row in reader:
        p1, p2, s1, s2, count = row
        outcomes[(p1, p2)][(float(s1), float(s2))] = int(count)
        outcomes[(p2, p1)][(float(s2), float(s1))] = int(count)
    return outcomes

def generate_matchups(players):
    # Want the triangular product
    for i in range(len(players)):
        for j in range(i, len(players)):
            if i == j:
                yield players[i].clone(), players[j]
            else:
                yield players[i], players[j]

def generate_matchups_indices(num_players):
    # Want the triangular product
    for i in range(num_players):
        for j in range(i, num_players):
            yield i, j

def sample_match_outcomes(players, turns, repetitions, noise=0):
    """
    Play all matches between pairs of players and return a dictionary mapping
    player names to outcomes.
    """
    match_outcomes = dict()
    matchups = list(generate_matchups(players))

    for pairs in matchups:

        match = axl.Match(pairs, turns=turns, noise=noise)
        rs = repetitions
        if not match._stochastic:
            rs = 1
        outcomes = []
        for _ in range(rs):
            match.play()
            outcomes.append(match.final_score_per_turn())

        counts = Counter(outcomes)

        player_names = tuple(map(str, pairs))
        match_outcomes[player_names] = counts

    return match_outcomes

def write_winner(filename, turns, repetitions, noise, i, j, seed=None):
    """
    Write the winner of a Moran process to file
    """
    if seed:
        axl.seed(seed)  # Seed the process

    pairs = (players[i].clone(), players[j].clone())
    match = axl.Match(pairs, turns=turns, noise=noise)
    rs = repetitions
    if not match._stochastic and noise == 0:
        rs = 1
    outcomes = []

    for _ in range(rs):
        try:
            match.play()
            outcomes.append(match.final_score_per_turn())
        except KeyError:
            print(turns, repetitions, noise, i, j, seed)

    counts = Counter(outcomes)
    player_names = tuple(map(str, pairs))
    match_outcomes = dict()
    match_outcomes[player_names] = counts
    write_csv(match_outcomes, filename=filename, append=True)


def sample_match_outcomes_parallel(turns, repetitions, filename, noise=0,
                                   processes=None):
    """
    Parallel matches.
    """

    player_indices = range(len(players))
    if processes is None:
        for i in player_indices:
            print(i, len(players))
            for j in player_indices:
                for seed in range(repetitions):
                    write_winner(filename, turns, repetitions, noise, i, j,
                                 seed)
    else:
        func = functools.partial(write_winner, filename, turns, repetitions,
                                 noise)
        p = multiprocessing.Pool(processes)

        args = generate_matchups_indices(len(players))
        p.starmap(func, args)


if __name__ == "__main__":
    # players are global
    from players import selected_players
    players = selected_players()

    print(len(list(map(str, players))))

    try:
        os.remove("../data/outcomes.csv")
        os.remove("../data/outcomes_noise.csv")
    except FileNotFoundError:
        pass

    repetitions = 10000
    turns = 200

    sample_match_outcomes_parallel(turns=turns, repetitions=repetitions,
                                   filename="../data/outcomes.csv", noise=0,
                                   processes=4)

    sample_match_outcomes_parallel(turns=turns, repetitions=repetitions,
                                   filename="../data/outcomes_noise.csv", noise=0.05,
                                   processes=4)
