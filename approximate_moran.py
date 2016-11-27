import axelrod as axl
import numpy as np

# For tests
import collections
import unittest


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
    def __init__(self, players, cached_outcomes, mutation_rate=0.):
        super(ApproximateMoranProcess, self).__init__(
            players, turns=0, noise=0, deterministic_cache=None,
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


#########
# Tests #
#########


class TestPdf(unittest.TestCase):
    """A suite of tests for the Pdf class"""
    observations = [('C', 'D')] * 4 + [('C', 'C')] * 12 + \
                   [('D', 'C')] * 2 + [('D', 'D')] * 15
    counter = collections.Counter(observations)
    pdf = Pdf(counter)

    def test_init__(self):
        self.assertEqual(set(self.pdf.sample_space), set(self.counter.keys()))
        self.assertEqual(set(self.pdf.counts), set([4, 12, 2, 15]))
        self.assertEqual(self.pdf.total, sum([4, 12, 2, 15]))
        self.assertAlmostEqual(sum(self.pdf.probability), 1)

    def test_sample(self):
        """Test that sample maps to correct domain"""
        all_samples = []

        np.random.seed(0)
        for sample in range(100):
            all_samples.append(self.pdf.sample())

        self.assertEqual(len(all_samples), 100)
        self.assertEqual(set(all_samples), set(self.observations))

    def test_seed(self):
        """Test that numpy seeds the sample properly"""

        for seed in range(10):
            np.random.seed(seed)
            sample = self.pdf.sample()
            np.random.seed(seed)
            self.assertEqual(sample, self.pdf.sample())


class ApproximateMoranProcess(unittest.TestCase):
    """A suite of tests for the ApproximateMoranProcess"""
    players = [axl.Cooperator(), axl.Defector()]
    cached_outcomes = {}

    counter = collections.Counter([(0, 5)])
    pdf = Pdf(counter)
    cached_outcomes[('Cooperator', 'Defector')] = pdf

    counter = collections.Counter([(3, 3)])
    pdf = Pdf(counter)
    cached_outcomes[('Cooperator', 'Cooperator')] = pdf

    counter = collections.Counter([(1, 1)])
    pdf = Pdf(counter)
    cached_outcomes[('Defector', 'Defector')] = pdf

    amp = ApproximateMoranProcess(players, cached_outcomes)

    def test_init(self):
        """Test the initialisation process"""
        self.assertEqual(set(self.amp.cached_outcomes.keys()),
                         set([('Cooperator', 'Defector'),
                              ('Cooperator', 'Cooperator'),
                              ('Defector', 'Defector')]))
        self.assertEqual(self.amp.players, self.players)
        self.assertEqual(self.amp.turns, 0)
        self.assertEqual(self.amp.noise, 0)

    def test_next(self):
        """Test the next function of the Moran process"""
        scores = self.amp._play_next_round()
        self.assertEqual(scores, [0, 5])
        scores = self.amp._play_next_round()
        self.assertEqual(scores, [0, 5])
        scores = self.amp._play_next_round()
        self.assertEqual(scores, [0, 5])
