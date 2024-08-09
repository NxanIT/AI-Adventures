"""
This file includes the classes Game and Game history.
Those classes are used to save the states of the tic-tac-toe game
and enable the user to actually play a game.
"""

import random

from .state import State


class Game:
    def __init__(self, player_1, player_2, brain,verbose=False):
        """
        player_1: instance of Player,' can be human or AI
        player_2: instance of Player, can be human or AI
        brain: instance of TotalStates
        verbose: boolean, if True results are printed
        """

        self.player = [player_1, player_2]
        player_1.set_number(1)
        player_2.set_number(2)
        self.state = State([0] * 9, brain)
        self.verbose = verbose
        

    def play(self):
        """Play tic-tac-toe until win or draw."""

        # choose random who starts
        self.curr_player = random.choice([0,1])

        # loop breaks when game is over
        while True:
            # check if draw, win, loose
            if self.check_if_done():
                # evaluate players
                self.evaluate_states()
                
                if self.verbose:
                    self.print_result()
                return 

            # make move
            self.state = self.player[self.curr_player].make_move(self.state)

            # next player
            self.curr_player = 0 if self.curr_player else 1


    def print_result(self):
        """Print information about the game result."""
        
        print('Congrats to Player #{}'.format(1 if self.result==1 else 2))


    def check_if_done(self):
        """
        If game is done set result and return True.
        The result value is the perspective of player 1.
         0 ... draw
        -1 ... lost
         1 ... won

        -----
        returns: boolean, if game is done
        """

        # check if draw
        if self.state.is_draw():
            self.result = 0
            return True

        # check if win
        if self.state.is_win():
            self.result = 1 if self.state.get_winner() == 1 else -1
            return True
        
        # not done
        return False


    def evaluate_states(self):
        """Call evaluation method for both players and pass result."""

        self.player[0].evaluate(self.result, self.state)
        self.player[1].evaluate(-self.result, self.state)
        


class GameHistory:
    """This class is used to save the table of one game. Each agent has its own instance."""

    def __init__(self):
        """
        list of dictionaries
        hash: 
        value: integer [-1, 1]

        [
            {hash: value},

        ]
        """

        self.curr_history = []

    def __iter__(self):
        """Yield an iteratable object."""
        for i in self.curr_history:
            yield i


    def add_move(self, hash_value, state_value):
        """
        Append the most recent status. 
        -----
        hash_value: integer, hash of the last move
        state_value: instance of State
        """

        self.curr_history.append({hash_value : state_value})


    def recalculate(self, result, alpha=0.5):
        """
        Calculate values of states based on result and learning rate.
        -----
        result: integer {-1, 0, 1}
        alpha: float [0,1]
        """ 
        
        # reverse order or history, out of practical reasons
        reversed_history = list(reversed(self.curr_history))

        for index, state in enumerate(reversed_history):
            
            # get dict key (= hash) from list element
            key_curr = next(iter(state))
            
            if index == 0:
                # winning or loosing state -> -1, 0 or 1 respectively
                reversed_history[index][key_curr] = result
                
            else:
            # compute new value for the state based on the value of the previous move
                
                # get dict key (= hash) from previous list element (= previous state)
                key_prev = next(iter(reversed_history[index-1]))

                # compute new value for the state
                # formula: value_new = value_old + alpha * (value_next - value_old)
                value_new = reversed_history[index][key_curr] + alpha * (reversed_history[index-1][key_prev] - reversed_history[index][key_curr])

                # update value
                reversed_history[index][key_curr] = value_new

        self.curr_history = reversed_history