"""
This file includes the classes State and TotalStates.
Those classes are relevant for representing the current state of the tic-tac-toe game,
as well as for saving previously seen states together with their state values.
"""

import numpy as np


class State:
    """This class represents a state of a tic-tac-toe game."""

    map12 = {1:2, 2:1}
    display_map = {0: ' ', 1: 'X', 2: 'O'}

    def __init__(self, vector, brain):
        """
        vector: list, 9 elements
        brain: instance of TotalStates
        """
        self.vector = vector
        self.brain = brain


    def is_draw(self):
        """Return if state is a draw."""
        return not 0 in self.vector


    def is_win(self):
        """Return True if there is a winner and save the winner as attribute."""

        comb = [
            # check rows
            [0,1,2], [3,4,5], [6,7,8],
            # check cols
            [0,3,6], [1,4,7], [2,5,8],
            # check diag
            [0,4,8], [2,4,6]
        ]

        for c in comb:
            v  = self.vector[c[0]] ** 2
            v += self.vector[c[1]] ** 2
            v += self.vector[c[2]] ** 2

            if v == 3:
                self.winner = 1
                return True
            if v == 12:
                self.winner = 2
                return True
        return False


    def get_winner(self):
        """Return the winner: 1 or 2."""
        return self.winner


    def display(self):
        """Display the state of the game."""
        print("\n")
        
        fields = [self.display_map[i] for i in self.vector]
        for row in range(3):
            print("\t  {}  |  {}  |  {}".format(fields[0 + row*3], fields[1 + row*3], fields[2 + row*3]))
            if row < 2:
                print('\t_____|_____|_____') 
        
        print('\t     |     |\n\n') 


    def is_valid_move(self, player_input):
        """
        Return True if position is a valid move.
        -----
        player_input: integer, position of move
        -----
        returns: boolean
        """
        return player_input < 9 and player_input >= 0 and not self.vector[player_input]


    def update(self, player_input, nr):
        """
        Update vector by making move.
        -----
        player_input: integer, position of move
        nr: integer, number of player
        """
        self.vector[player_input] = nr


    def possible_next_states(self, player_nr):
        """
        Return all possible choices given the current state.
        -----
        player_nr: integer, number of player
        -----
        returns: list of possible states
        """

        options = []

        for i in range(len(self.vector)):
            if not self.vector[i]:
                vector = self.vector.copy()
                vector[i] = player_nr
                options.append(State(vector, self.brain))
            
        return options


    def get_best_state(self, options):
        """
        For all possible choices, lookup if state_value for possible choice available. 
        If not, calculate min_hash for player-swap/rotation/mirror neighborhood and document in game history.
        Return choice with highest state value given all possible choices.
        -----
        options: list of possible choices 
        -----
        returns: best choice as State instance, corresponding state_value
        """
        available_statevalues = {}

        # For each possible choice
        for opt in options:
            # Check if state_value for choice hash exists and 
            if self.calc_hash(opt.vector) in self.brain.minhash_by_hash and self.brain.minhash_by_hash[self.calc_hash(opt.vector)] in self.brain.statevalue_by_hash:
                # Add hash to state_value to available_statevalues
                available_statevalues[''.join(map(str, opt.vector))] = self.brain.statevalue_by_hash[self.brain.minhash_by_hash[self.calc_hash(opt.vector)]]
            else:
                # Create hash to min_hash in brain.minhash_by_hash
                self.evaluate_minhash(opt.vector)
                # Add hash to initial_statevalue to available_statevalues
                available_statevalues[''.join(map(str, opt.vector))] = self.brain.initial_statevalue

        # Determine choice with highest state_value and instantiate as State
        best_state = State(list(map(int, max(available_statevalues, key=available_statevalues.get))), self.brain)

        # Return best choice as State instance and corresponding state_value
        return best_state, available_statevalues[max(available_statevalues, key=available_statevalues.get)]


    def calc_hash(self, sublists):
        """
        Return hash of input vector, meaning its representation as integer (concat + remove leading 0).
        -----
        sublists: 
        -----
        returns:
        """
        # If input sublists not properly split in sublists yet  
        if type(sublists[0]) != list:
            sublists = [sublists[i:i+3] for i in range(0, len(sublists), 3)]

        # Transform sublists to integer
        h = int(''.join(str(i) for a in sublists for i in a))

        return h 


    def rotate(self, split_sublists):
        """
        Rotate input matrix by 90°.
        Return hash of rotated matrix and rotated matrix.
        -----
        split_sublists: 
        -----
        returns: 
        """
        # Rotate sublists 
        rotated_sublists = [list(z) for z in zip(*split_sublists[::-1])]

        # Return rotation hash and rotated sublists
        return  self.calc_hash(rotated_sublists), rotated_sublists


    def mirror(self, split_sublists):
        """
        Mirror matrix horizontally and diagonally.
        Return hashes of horizontally and diagonally mirrored matrices.
        -----
        split_sublists:
        -----
        returns:
        """
        # Mirror matrix horizontally
        horizontal = [list(x) for x in np.flip(split_sublists,0)]
        # Mirror matrix digaonally
        diagonal = list(map(list, zip(*split_sublists)))
        
        # Return hashes of mirrored matrices
        return self.calc_hash(horizontal), self.calc_hash(diagonal)


    def evaluate_minhash(self, vector):
        """
        After, splitting input vector into matrix (sublists), swap player entries (1<->2).
        For both matrices, rotate and mirror to determine mininmal hash of neighborhood.
        Document hash to min_hash for all hashes in neighborhood in brain.minhash_by_hash.
        -----
        vector: 
        """
        hashes = []

        # Split vector
        split_sublists = [vector[i:i+3] for i in range(0, len(vector), 3)]
        # Swap player entries (1<->2)
        inv_split_sublists = [[self.map12.get(x, 0) for x in sublist] for sublist in split_sublists]
        # Instantiate min_hash
        min_hash = self.calc_hash(split_sublists)

        for sublists in [split_sublists, inv_split_sublists]:
            # 4 := complete rotation
            for j in range(0,4):
                # Mirror matrix
                horizontal_hash, diagonal_hash = self.mirror(sublists)
                # Rotate matrix by 90°
                rot_hash, sublists = self.rotate(sublists)
                # Append hashes to hashes list
                hashes = hashes + [horizontal_hash, diagonal_hash, rot_hash]
        
        # Determien minimal hash in neighborhood
        min_hash = min(hashes)

        # Document hash links
        for h in hashes:
            self.brain.minhash_by_hash[h] = min_hash



class TotalStates:
    """This class is used to save all seen states. Both agents have access."""
    
    def __init__(self, initial_statevalue=0):
        """
        statevalue_by_hash Dictionary:
        key: hash
        value: integer in range [-1, 1]

        minhash_by_hash Dictionary:
        key: hash
        value: integer in range [-1, 1]
        -----
        initial_statevalue: float [-1, 1]
        """
        self.statevalue_by_hash = {}
        self.minhash_by_hash = {}
        self.initial_statevalue = initial_statevalue


    def get_value(self, state_hash):
        """
        Look up the state value by state_hash.
        -----
        state_hash:
        -----
        returns:
        """

        state_value = self.statevalue_by_hash[state_hash]
        
        return state_value


    def update_or_insert(self, history):
        """
        Add all new states and its values and update existing ones.
        -----
        history: instance of GameHistory
        """

        for state in history:
            # get dict key (= hash) from state in history
            historical_hash = next(iter(state))

            # update the values for the hashes or add new hash/value to dict
            self.statevalue_by_hash[historical_hash] = state[historical_hash]