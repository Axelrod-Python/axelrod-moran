"""
A script to write the relative fitness to file
"""
import pandas as pd
import theoretic

def read():
    summary = pd.read_csv("../data/sims_summary.csv")

    columns = [["player", "opponent", "N", "Noise", "$r_1$", "$r_{N/2}$"],
               ["player", "opponent", "N", "Noise", "$r_{N-1}$"]]
    dfs = [[], []]
    for (player, N, opponent, Noise), df in summary.groupby(["P1", "N",
                                                             "P2", "Noise"]):
        try:
            p = df[df["i"] == 1].iloc[0]["P1 fixation"]
            r1 = theoretic.find_relative_fitness(N, 1, p)
        except (IndexError, RuntimeError):
            r1 = float("nan")

        try:
            p = df[df["i"] == df["N"] / 2].iloc[0]["P1 fixation"]
            rnover2 = theoretic.find_relative_fitness(N, N / 2, p)
        except (IndexError, RuntimeError):
            rnover2 = float("nan")

        try:
            p = df[df["i"] == df["N"] - 1].iloc[0]["P1 fixation"]
            rminus1 = theoretic.find_relative_fitness(N, N - 1, p)
        except (IndexError, RuntimeError):
            rminus1 = float("nan")

        dfs[0].append(pd.DataFrame([[player, opponent, N, Noise, r1, rnover2]],
                                   columns=columns[0]))
        dfs[1].append(pd.DataFrame([[opponent, player, N, Noise, rminus1]],
                                   columns=columns[1]))

    dfs = [pd.concat(dfs[0]), pd.concat(dfs[1])]

    return dfs[0].merge(dfs[1], on=["player", "N","opponent", "Noise"])

if __name__ == "__main__":
    fitness_df = read()
    fitness_df.to_csv("../data/relative_fitness.csv")
