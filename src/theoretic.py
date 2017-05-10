"""
Code to calculate analytic fixation probabilities
"""
import unittest
import numpy as np
import math
import functools

from scipy.optimize import newton

def scores(strategy_pair, utilities):
    """
    Return the fitness scores:

        [a, b]
        [c, d]

    for a pair of strategies, in a population of N individuals
    with i individuals of the first type.
    """
    try:
        s1, s2 = strategy_pair
        m = np.array([[utilities[(s1, s1)][0], utilities[(s1, s2)][0]],
                      [utilities[(s1, s2)][1], utilities[(s2, s2)][0]]])
    except KeyError:
        s2, s1 = strategy_pair
        m = np.array([[utilities[(s2, s2)][0], utilities[(s1, s2)][1]],
                      [utilities[(s1, s2)][0], utilities[(s1, s1)][0]]])
    return m

def fitness(strategy_pair, N, i, utilities):
    """
    Return the nowak fitness of a strategy pair in a population with
    N total individuals and i individuals of the first type.
    """
    m = scores(strategy_pair, utilities)

    f = (m[0, 0] * (i - 1) + m[0, 1] * (N - i)) / (N - 1)
    g = (m[1, 0] * i + m[1, 1] * (N - i - 1)) / (N - 1)

    return f, g

def nowak_fitness(strategy_pair, N, i, utilities, selection_intensity=1):
    """
    Return the nowak fitness of a strategy pair in a population with
    N total individuals and i individuals of the first type.
    """
    F, G = [1 + selection_intensity * (k - 1) for k in fitness(strategy_pair, N, i, utilities)]

    return F, G

def fermi_fitness(strategy_pair, N, i, utilities, selection_intensity=1):
    """
    Return the fermi fitness of a strategy pair in a population with
    N total individuals and i individuals of the first type.
    """
    F, G = [math.exp(k) for k in fitness(strategy_pair, N, i, utilities)]

    return F / (F + G), G / (F + G)

def transition(strategy_pair, N, i, utilities, fitness_type="nowak",
	       selection_intensity=1):
    """
    Return the 3 transition probabilities:

    P[i, i - 1]
    P[i, i]
    P[i, i + 1]

    Assuming:
     - a given stratgy pair,
     - a given total population size N
     - and a state i (the number of individuals of the first type)
    """
    fitness_types = {"nowak": nowak_fitness, "fermi": fermi_fitness}
    fitness = fitness_types[fitness_type]
    fit = fitness(strategy_pair, N, i, utilities=utilities, selection_intensity=selection_intensity)

    p_up = (fit[0] * i / (fit[0] * i + fit[1] * (N - i))) * ((N - i) / N)

    p_down = (fit[1] * (N - i) / (fit[0] * i + fit[1] * (N - i))) * (i / N)

    p_stay = 1 - p_up - p_down
    return p_down, p_stay, p_up

def fixation(strategy_pair, N, i, utilities,
             fitness_type="nowak", selection_intensity=1):
    """Return the fixation probability for each pair"""
    ratios = []
    for j in range(1, N): # ignore first and last transitions, which are likely zero
        p_down, _, p_up = transition(strategy_pair, N, i=j, utilities=utilities,
                                     fitness_type=fitness_type, selection_intensity=selection_intensity)
        ratios.append(p_down / p_up)
    t = np.cumprod(ratios)
    s = np.cumsum(t)
    if i > 1:
        return (1 + s[i - 2]) / (1 + s[-1])
    return 1 / (1 + s[-1])

#########
# Tests #
#########

utilities = {("Defector", "Cooperator"): (5, 0),
             ("Defector", "Defector"): (1, 1),
             ("Cooperator", "Cooperator"): (3, 3)}

class TestScores(unittest.TestCase):
    def test_defector_v_cooperator(self):
        result = scores(("Defector", "Cooperator"), utilities)
        self.assertTrue(np.array_equal(result, np.array([[1, 5], [0, 3]])))
    def test_cooperator_v_defector(self):
        result = scores(("Cooperator", "Defector"), utilities)
        self.assertTrue(np.array_equal(result, np.array([[3, 0], [5, 1]])))

class TestFitness(unittest.TestCase):
    def test_defector_v_cooperator_nowak(self):
        self.assertEqual(nowak_fitness(("Defector", "Cooperator"), 5, 1,
                         utilities)[::-1],
                         nowak_fitness(("Cooperator", "Defector"), 5, 4,
                         utilities))
    def test_defector_v_cooperator_fermi(self):
        self.assertEqual(fermi_fitness(("Defector", "Cooperator"), 5, 1,
                         utilities)[::-1],
                         fermi_fitness(("Cooperator", "Defector"), 5, 4,
                         utilities))

class TestTransition(unittest.TestCase):
    def test_defector_v_cooperator(self):
        self.assertEqual(transition(("Defector", "Cooperator"), 5, 2,
                                    utilities),
                         transition(("Cooperator", "Defector"), 5, 3,
                                    utilities)[::-1])

class TestFixation(unittest.TestCase):
    def test_defector_v_cooperator(self):
        self.assertEqual(fixation(("Cooperator", "Defector"), 5, 1, utilities),
                         0)
