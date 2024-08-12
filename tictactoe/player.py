"""
This files includes the classes PlayerHuman and PlayerAI.
Those classes are used for the actual players of a tic-tac-toe game.
"""

import numpy as np
import random

from game import GameHistory


class Player:
    """This abstract class represents a tic-tac-toe player."""

    def set_number(self, nr):
        self.nr = nr

    def make_move(self, state):
        pass

    def evaluate(self, result, state):
        pass


class PlayerHuman(Player):

    def __init__(self):
        Player.__init__(self)


    def make_move(self, state):
        """
        Read in the user input until it is valid and return the resulting state of his move.
        -----
        state: State instance, before player's move
        -----
        returns: State instance, after player's move
        """

        print("Make your move!")
        state.display()
        
        while True:
            player_input = self.get_input()
            if state.is_valid_move(player_input):
                state.update(player_input, self.nr)
                return state

            print("Field already taken.")


    def get_input(self):
        """
        Read in and return the users choice for his next move.
        -----
        returns: integer, index of the tic-tac-toe vector
        """
        while True:
            try:
                row = int(input('row 1,2 or 3:'))
                col = int(input('col 1,2 or 3:'))
                break

            except ValueError as e: 
                print('Please only integer!')
                continue

        return (row-1)*3 + col-1

    def evaluate(self, result, state):
        """
        Display the final state to for the user.
        -----
        result: integer {-1, 1}
        state: instance of State
        """

        print('Final State:')
        state.display()


class PlayerAI(Player):

    def __init__(self, alpha, rnd, brain):
        """
        alpha: float [0,1], learning rate
        rnd: float [0,1], probability of choosing the next move random
        brain: instance of TotalStates
        """

        self.alpha = alpha
        self.rnd = rnd
        self.brain = brain

        # history of all the states the moves of this player resulted in
        self.history = GameHistory()
        Player.__init__(self)
    

    def make_move(self, state):
        """
        Return the resulting state after the player made his move.
        -----
        state: list with 9 elements (values 0/1/2)
        -----
        returns: list with 9 elements (values 0/1/2)
        """
        # possible choices is list of states
        options = state.possible_next_states(self.nr)

        if np.random.choice([True, False], p=[self.rnd, 1 - self.rnd]):
            # select random choice from options 
            choice = random.choice(options)
            curr_hash = choice.calc_hash(choice.vector)
        
            if curr_hash in self.brain.minhash_by_hash and self.brain.minhash_by_hash[curr_hash] in self.brain.statevalue_by_hash:
                value = self.brain.statevalue_by_hash[self.brain.minhash_by_hash[curr_hash]]

            else:
                choice.evaluate_minhash(choice.vector)
                value = self.brain.initial_statevalue
            
            curr_hash = self.brain.minhash_by_hash[choice.calc_hash(choice.vector)]

        else:
            choice, value = state.get_best_state(options)
            curr_hash = self.brain.minhash_by_hash[choice.calc_hash(choice.vector)]

        #TODO hier muss min_hash uebergeben werden 
        self.history.add_move(curr_hash, value)

        return choice


    def evaluate(self, result, state):
        """
        Calculate values of states based on result and learning rate and save them to brain.
        -----
        result: integer (-1, 0, 1)
        state: instance of State
        """
        
        # calculate values
        self.history.recalculate(result) 

        # update values in brain
        self.brain.update_or_insert(self.history)  

        # new history
        self.history = GameHistory() 