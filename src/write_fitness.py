"""
A script to write the relative fitness to file
"""
import pandas as pd
import theoretic

def read():
    summary = pd.read_csv("../data/sims_summary.csv")

    columns = [["player", "opponent", "N", "Noise", "$p_1$", "$p_{N/2}$",
                "$r_1$", "$r_{N/2}$"],
               ["player", "opponent", "N", "Noise", "$p_{N-1}$", "$r_{N-1}$"]]
    dfs = [[], []]
    for (player, N, opponent, Noise), df in summary.groupby(["P1", "N",
                                                             "P2", "Noise"]):
        try:
            p1 = df[df["i"] == 1].iloc[0]["P1 fixation"]
            r1 = theoretic.find_relative_fitness(N, 1, p1)
        except (IndexError, RuntimeError):
            p1 = float("nan")
            r1 = float("nan")

        try:
            pnover2 = df[df["i"] == df["N"] / 2].iloc[0]["P1 fixation"]
            rnover2 = theoretic.find_relative_fitness(N, N / 2, pnover2)
        except (IndexError, RuntimeError):
            pnover2 = float("nan")
            rnover2 = float("nan")

        try:
            pminus1 = df[df["i"] == df["N"] - 1].iloc[0]["P1 fixation"]
            rminus1 = theoretic.find_relative_fitness(N, N - 1, pminus1)
        except (IndexError, RuntimeError):
            pminus1 = float("nan")
            rminus1 = float("nan")

        dfs[0].append(pd.DataFrame([[player, opponent, N, Noise, p1, pnover2,
                                     r1, rnover2]],
                                   columns=columns[0]))
        dfs[1].append(pd.DataFrame([[opponent, player, N, Noise, pminus1,
                                     rminus1]],
                                   columns=columns[1]))

    dfs = [pd.concat(dfs[0]), pd.concat(dfs[1])]

    return dfs[0].merge(dfs[1], on=["player", "N","opponent", "Noise"])

if __name__ == "__main__":
    fitness_df = read()
    fitness_df.to_csv("../data/main.csv")
