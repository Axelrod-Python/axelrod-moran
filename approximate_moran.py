import axelrod as axl
import numpy as np

class Pdf(object):
    """A class for a probability distribution"""
    def __init__(self, counter):
        """Take as an instance of collections.counter"""
        self.sample_space, self.counts = zip(*counter.items())
        self.size = len(self.sample_space)
        self.total = sum(self.counts)
        self.probability = list([v / self.total for v in self.counts])

    def sample(self):
        """Sample from the pdf"""
        index = np.random.choice(a=range(self.size), p=self.probability)
        # Numpy cannot sample from a list of n dimensional objects for n > 1,
        # need to sample an index
        return self.sample_space[index]

    def __repr__(self):
        return "Sample space: {} - Probabilities: {}".format(self.sample_space,
                                                             self.probability)


class ApproximateMoranProcess(axl.MoranProcess):
    """
    A class to approximate a Moran process based
    on a distribution of potential Match outcomes.

    Instead of playing the matches, the result is sampled
    from a dictionary of play tuples to distribution of match outcomes
    """
    def __init__(self, players, cached_outcomes=None, turns=0,
                 noise=0, mutation_rate=0.):
        super(ApproximateMoranProcess, self).__init__(
            players, turns=turns, noise=noise, deterministic_cache=None,
            mutation_rate=mutation_rate)
        self.cached_outcomes = cached_outcomes

    def _play_next_round(self):
        """
        Plays the next round of the process. Every player is paired up
        against every other player and the total scores are obtained from the
        """
        N = self.num_players
        scores = [0] * N
        for i in range(N):
            for j in range(i + 1, N):
                player_names = tuple([str(self.players[i]), str(self.players[j])])

                try:
                    match_scores = self.cached_outcomes[player_names].sample()
                    scores[i] += match_scores[0]
                    scores[j] += match_scores[1]
                except KeyError:
                    match_scores = self.cached_outcomes[player_names[::-1]].sample()
                    scores[i] += match_scores[1]
                    scores[j] += match_scores[0]
        self.score_history.append(scores)
        return scores
