# Python 3

from __future__ import print_function

import csv
from collections import defaultdict, Counter
import itertools
from pathlib import Path
import random
import sys

import numpy as np

import axelrod as axl

def selected_strategies():
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

#def print_dict_sorted(d):
    #"""Prints a dictionary sorted by the values."""
    #items = [(v, k) for (k, v) in d.items()]
    #for v, k in sorted(items):
        #print("{v}: {k}".format(v=v, k=k))


def build_population(players, weights):
    population = []
    for player, weight in zip(players, weights):
        for _ in range(weight):
            population.append(player.clone())
    return population

def output_players(players, outfilename="players.csv"):
    rows = [(i, str(player)) for (i, player) in enumerate(players)]
    path = Path("results") / outfilename
    with path.open('w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(outfilename)

def run_simulations(players, N=2, turns=100, repetitions=1000, noise=0, outfilename=None):
    """This function conducts many moran processes to empirically estimate
    fixation probabilities. For each pair of strategies, the population consists
    of 1 player of the first type and N-1 players of the second type."""
    path = Path("results")
    if not outfilename:
        outfilename = "sims_{N}.csv".format(N=N)
    path = path / outfilename
    outfile = csv.writer(path.open('a'))

    # Cache names to reverse winners to ids later
    names = dict(zip([str(p) for p in players], range(len(players))))

    # For each distinct pair of players, play `repetitions` number of Moran matches
    for i, player_1 in enumerate(players):
        print(i, len(players))
        for j, player_2 in enumerate(players):
            if i == j:
                continue
            rows = []
            initial_population = build_population([player_1, player_2], [1, N-1])
            mp = axl.MoranProcess(initial_population, turns=turns, noise=noise)
            for _ in range(repetitions):
                mp.reset()
                populations = mp.play()
                winner_name = mp.winning_strategy_name
                winner_name = list(populations[-1].keys())[0]
                row = [i, j, names[winner_name]]
                rows.append(row)
            outfile.writerows(rows)

def main():
    N = int(sys.argv[1]) # Population size
    try:
        repetitions = int(sys.argv[2])
    except IndexError:
        repetitions = 1000
    # Make sure the data folder exists
    path = Path("results")
    path.mkdir(exist_ok=True)
    #players = [s() for s in selected_strategies()]
    players = [s() for s in axl.ordinary_strategies]
    output_players(players)
    run_simulations(players, N=N, repetitions=repetitions, outfilename="test.csv")


if __name__ == "__main__":
    main()
