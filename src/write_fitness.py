"""
A script to write the relative fitness to file

TODO: Get rid of the intermediate step in `clean_raw_moran.py` and do it all in
one go.
"""
import pandas as pd
import theoretic
import tempfile

def merged_df(N):
    summary = pd.read_csv("../data/sims_summary.csv")
    summary = summary[summary["N"] == N]

    columns = [["player", "opponent", "N", "Noise", "$p_1$", "$p_{N/2}$",
                "$r_1$", "$r_{N/2}$"],
               ["player", "opponent", "N", "Noise", "$p_{N-1}$", "$r_{N-1}$"]]
    dfs = [[], []]
    for (player, N, opponent, Noise), df in summary.groupby(["P1", "N",
                                                             "P2", "Noise"]):
        try:
            p1 = df[df["i"] == 1].iloc[0]["P1 fixation"]
            pminus1 = df[df["i"] == 1].iloc[0]["P2 fixation"]
        except IndexError:
            p1 = float("nan")
            pminus1 = float("nan")


        try:
            if N % 2 == 0:
                pnover2 = df[df["i"] == df["N"] / 2].iloc[0]["P1 fixation"]
            else:
                pnover2 = float("nan")
        except IndexError:
            pnover2 = float("nan")


        try:
            r1 = theoretic.find_relative_fitness(N, 1, p1)
        except RuntimeError:
            r1 = float("nan")

        try:
            rminus1 = theoretic.find_relative_fitness(N, N - 1, pminus1)
        except RuntimeError:
            rminus1 = float("nan")

        if N % 2 == 0:
            try:
                rnover2 = theoretic.find_relative_fitness(N, N / 2, pnover2)
            except RuntimeError:
                rnover2 = float("nan")
        else:
            rnover2 = float("nan")

        dfs[0].append(pd.DataFrame([[player, opponent, N, Noise, p1, pnover2,
                                     r1, rnover2]],
                                   columns=columns[0]))
        dfs[1].append(pd.DataFrame([[opponent, player, N, Noise, pminus1,
                                     rminus1]],
                                   columns=columns[1]))

    dfs = [pd.concat(dfs[0]), pd.concat(dfs[1])]

    return dfs[0].merge(dfs[1], on=["player", "N","opponent", "Noise"])

def read():
    dfs = []
    for N in range(2, 14 + 1):
        dfs.append(merged_df(N))

    return pd.concat(dfs)

def write(df):
    df = df[~df["Noise"]].drop("Noise", axis=1)
    df.to_csv("../data/main.csv", index=False)

if __name__ == "__main__":
    fitness_df = read()
    write(fitness_df)
