import axelrod as axl

C, D = axl.Actions.C, axl.Actions.D

fsm_transitions = [
    [(0, C, 7, C), (0, D, 1, C),
     (1, C, 11, D), (1, D, 11, D),
     (2, C, 8, D), (2, D, 8, C),
     (3, C, 3, C), (3, D, 12, D),
     (4, C, 6, C), (4, D, 3, C),
     (5, C, 11, C), (5, D, 8, D),
     (6, C, 13, D), (6, D, 14, C),
     (7, C, 4, D), (7, D, 2, D),
     (8, C, 14, D), (8, D, 8, D),
     (9, C, 0, C), (9, D, 10, D),
     (10, C, 8, C), (10, D, 15, C),
     (11, C, 6, D), (11, D, 5, D),
     (12, C, 6, D), (12, D, 9, D),
     (13, C, 9, D), (13, D, 8, D),
     (14, C, 8, D), (14, D, 13, D),
     (15, C, 4, C), (15, D, 5, C)],
    [(0, C, 13, D), (0, D, 12, D),
     (1, C, 3, D), (1, D, 4, D),
     (2, C, 14, D), (2, D, 9, D),
     (3, C, 0, C), (3, D, 1, D),
     (4, C, 1, D), (4, D, 2, D),
     (5, C, 12, C), (5, D, 6, C),
     (6, C, 1, C), (6, D, 14, D),
     (7, C, 12, D), (7, D, 2, D),
     (8, C, 7, D), (8, D, 9, D),
     (9, C, 8, D), (9, D, 0, D),
     (10, C, 2, C), (10, D, 15, C),
     (11, C, 7, D), (11, D, 13, D),
     (12, C, 3, C), (12, D, 8, D),
     (13, C, 7, C), (13, D, 10, D),
     (14, C, 10, D), (14, D, 7, D),
     (15, C, 15, C), (15, D, 11, D)],
    [(0, C, 0, C), (0, D, 3, C),
     (1, C, 5, D), (1, D, 0, C),
     (2, C, 3, C), (2, D, 2, D),
     (3, C, 4, D), (3, D, 6, D),
     (4, C, 3, C), (4, D, 1, D),
     (5, C, 6, C), (5, D, 3, D),
     (6, C, 6, D), (6, D, 6, D),
     (7, C, 7, D), (7, D, 5, C)]]

fsm_players = [axl.FSMPlayer(transitions=transitions)
               for transitions in fsm_transitions]
fsm_players += [axl.FSMPlayer(transitions=transitions, initial_state=0, initial_action=C)
               for transitions in fsm_transitions]

fsm_players[3].classifier["memory_depth"] = float('inf')
fsm_players[4].classifier["memory_depth"] = float('inf')
fsm_players[5].classifier["memory_depth"] = float('inf')

def selected_players(extra_players=fsm_players):
    """
    Return a list of all players used in this paper
    """
    filterset = {"long_run_time": False,
                 "manipulates_source": False,
                 "manipulates_state": False,
                 "inspects_source": False}
    players = [s() for s in axl.filtered_strategies(filterset)]

    if extra_players is not None:
        players += extra_players

    return players

if __name__ == "__main__":
    print(len(selected_players()))
