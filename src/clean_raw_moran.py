"""
A script to clean the raw data
"""
import csv
import preproces
import pandas as pd


def read():
    # Read in the player representations
    with open("../data/players.csv", "r") as f:
        reader = csv.reader(f)
        index_to_players = {row[0]: row[1] for row in reader}

    # Read in the data
    data = []
    for N in range(2, 14 + 1):
        # Read N = 2 data
        for filename in ["../data/sims_n_over_2/sims_{}.csv".format(N),
                         "../data/sims_1/sims_{0:02d}.csv".format(N)]:

            noise = "noise" in filename
            i = 1 if "sims_1/" in filename else N // 2

            try:
                with open(filename, "r") as f:
                    reader = csv.reader(f)
                    for row in reader:

                        index1, index2, indexwinner, winnercount = row

                        p1 = index_to_players[index1]
                        p2 = index_to_players[index2]
                        winner = index_to_players[indexwinner]

                        data.append([noise, int(N), i, p1, p2, winner, int(winnercount)])
            except FileNotFoundError:
                pass

    return pd.DataFrame(data, columns=["Noise", "N", "i", "P1", "P2",
                                       "Winner", "Winner count"])

def write(full_data):
    # Clean and write the data to file.
    with open("../data/sims_summary.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["P1", "P2", "N", "i", "Noise",
                         "Repetitions", "P1 fixation", "P2 fixation"])
        for index, df in full_data.groupby(["P1", "P2", "N", "i", "Noise"]):

            total = df["Winner count"].sum()

            fixation_probabilities = []
            for rep in range(2):
                count = float(df[df["Winner"] == index[rep]]["Winner count"].sum())
                fixation_probabilities.append(count / total)

            writer.writerow([*index, total, *fixation_probabilities])

if __name__ == "__main__":
    print("Reading raw data")
    full_data = read()
    print("Writing summary data")
    write(full_data)

    print("Finalising data")
    fitness_df = preproces.read()
    print("Writing main data")
    preproces.write(fitness_df)
