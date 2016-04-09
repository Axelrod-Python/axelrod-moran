# Python 3

import csv
from collections import defaultdict, Counter
import itertools
import random

import numpy as np

import axelrod as axl

def get_strategies():
    strategies = [
        axl.Aggravater,
        axl.ALLCorALLD,
        axl.Alternator,
        axl.AlternatorHunter,
        axl.AntiCycler,
        axl.AntiTitForTat,
        axl.APavlov2006,
        axl.APavlov2011,
        axl.Appeaser,
        axl.AverageCopier,
        axl.BackStabber,
        axl.Bully,
        axl.Calculator,
        axl.Champion,
        axl.Cooperator,
        axl.CyclerCCCCCD,
        axl.CyclerCCCD,
        axl.CyclerCCD,
        axl.Davis,
        axl.Defector,
        axl.DoubleCrosser,
        axl.Eatherley,
        axl.Feld,
        axl.FirmButFair,
        axl.FoolMeForever,
        axl.FoolMeOnce,
        axl.ForgetfulFoolMeOnce,
        axl.ForgetfulGrudger,
        axl.Forgiver,
        axl.ForgivingTitForTat,
        axl.PSOGambler,
        axl.GTFT,
        axl.GoByMajority,
        axl.GoByMajority10,
        axl.GoByMajority20,
        axl.GoByMajority40,
        axl.GoByMajority5,
        axl.HardGoByMajority,
        axl.HardGoByMajority10,
        axl.HardGoByMajority20,
        axl.HardGoByMajority40,
        axl.HardGoByMajority5,
        axl.Golden,
        axl.Grofman,
        axl.Grudger,
        axl.Grumpy,
        axl.HardProber,
        axl.HardTitFor2Tats,
        axl.HardTitForTat,
        axl.Inverse,
        axl.InversePunisher,
        axl.Joss,
        axl.LimitedRetaliate,
        axl.LimitedRetaliate2,
        axl.LimitedRetaliate3,
        axl.EvolvedLookerUp,
        axl.MathConstantHunter,
        axl.NiceAverageCopier,
        axl.Nydegger,
        axl.OmegaTFT,
        axl.OnceBitten,
        axl.OppositeGrudger,
        axl.Pi,
        axl.Prober,
        axl.Prober2,
        axl.Prober3,
        axl.Punisher,
        axl.Random,
        axl.RandomHunter,
        axl.Retaliate,
        axl.Retaliate2,
        axl.Retaliate3,
        axl.Shubik,
        axl.SneakyTitForTat,
        axl.SoftJoss,
        axl.StochasticWSLS,
        axl.SuspiciousTitForTat,
        axl.Tester,
        axl.ThueMorse,
        axl.TitForTat,
        axl.TitFor2Tats,
        axl.TrickyCooperator,
        axl.TrickyDefector,
        axl.Tullock,
        axl.TwoTitsForTat,
        axl.WinStayLoseShift,
        axl.ZDExtort2,
        axl.ZDExtort2v2,
        axl.ZDExtort4,
        axl.ZDGen2,
        axl.ZDGTFT2,
        axl.ZDSet2,
        axl.e,
    ]

    strategies = [s for s in strategies if axl.obey_axelrod(s())]
    return strategies

def fitness_proportionate_selection(scores):
    """Randomly selects an individual proportionally to score."""
    csums = np.cumsum(scores)
    total = csums[-1]
    r = random.random() * total

    for i, x in enumerate(csums):
        if x >= r:
            return i

def print_dict_sorted(d):
    """Prints a dictionary sorted by the values."""
    items = [(v, k) for (k, v) in d.items()]
    for v, k in sorted(items):
        print("{v}: {k}".format(v=v, k=k))

# Moran Process

def moran_process(players, turns=10, verbose=True, noise=0):
    """The Moran process.

    Parameters
    ----------
    players: sequence
        a collection of Axelrod players
    turns: int, 10
        the number of turns in each interaction
    verbose: bool, True
        report progress as rounds proceed

    Returns
    -------
    populations, list[dict]
        the populations in each round, indexed by player name
    scores, list[dict]
        the scores for each player each round, indexed by name
    """

    populations = []
    round_scores = []
    N = len(players)
    for round_number in itertools.count(1):
        player_names = [str(player) for player in players]
        counter = Counter(player_names)
        populations.append(counter)

        # Exit condition: Population consists of a single player type
        if len(set(player_names)) == 1:
            break
        # Otherwise report progress
        if verbose:
            print("\nRound:", round_number)
            print_dict_sorted(counter)

        # Everyone plays everyone else
        scores = [0] * N
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                player1 = players[i]
                player2 = players[j]
                player1.reset()
                player2.reset()
                match = axl.Match((player1, player2), turns, noise=noise)
                results = match.play()
                match_scores = np.sum(match.scores(), axis=0) / float(turns)
                scores[i] += match_scores[0]
                scores[j] += match_scores[1]
        # Save the scores
        score_dict = defaultdict(float, dict(zip(player_names, scores)))
        for k, v in counter.items():
            score_dict[k] /= (float(v) * turns)
        round_scores.append(score_dict)
        # Update the population
        # Fitness proportionate selection
        j = fitness_proportionate_selection(scores)
        # Randomly remove a strategy
        i = random.randrange(0, N)
        # Replace player i with player j
        players[i] = players[j].clone()
    if verbose:
        print("\n", str(players[0]), "is the winner!")
    return populations, round_scores


def run_simulations(N=2, turns=100, repetitions=1000, noise=0):
    outfile_name = "sims_{N}.csv".format(N=N)
    outfile = csv.writer(open(outfile_name, 'a'))

    players = [s() for s in get_strategies()]
    names = dict(zip([str(p) for p in players], range(len(players))))

    for i, player_1 in enumerate(players):
        for j, player_2 in enumerate(players):
            if j <= i:
                continue
            reps = 1
            if player_1.classifier['stochastic'] or player_2.classifier['stochastic'] or noise:
                reps = repetitions
            for _ in range(reps):
                player_1.reset()
                player_2.reset()
                sim_players = []
                # 50-50
                #for _ in range(N // 2):
                    #sim_players.append(player_1.clone())
                    #sim_players.append(player_2.clone())
                # Single mutant
                sim_players.append(player_1.clone())
                for _ in range(N - 1):
                    sim_players.append(player_2.clone())
                populations, scores = moran_process(sim_players, verbose=False,
                                                    noise=noise)
                winner_name = list(populations[-1].keys())[0]
                #rounds = len(populations)
                row = [i, j, names[winner_name]]
                outfile.writerow(row)
                print(i, j, str(player_1), str(player_2), winner_name)

if __name__ == "__main__":
    import sys
    N = int(sys.argv[1])
    run_simulations(N)
