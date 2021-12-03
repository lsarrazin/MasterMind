'''
Module Game

Provides the class Game that is implementing a MasterMind game
'''

import random

class Game:
    '''
    MasterMind game controler
    Implements a classic mastermind, producing problem, recording and scoring submissions
    '''

    lines = 12
    pins = 5
    colors = 8

    def __init__(self):
        random.seed()
        self.new_game()


    def get_line(self, line):
        '''
        Returns a user submission
        Parameters:
        line -- number of requested submission
        '''
        return self.board[line]


    def get_score(self, line):
        '''
        Get score of some line

        Parameters:
        line (int): line to consider

        Returns:
        Array[int]: number of found colors, and number of close colors (wrong location)
        '''
        return self.scores[line]


    def get_solution(self):
        '''
        Get solution

        Returns:
        Array[char]: List of colors to find
        '''
        return self.solution


    def get_guess_line(self):
        '''
        Get current guess number

        Returns:
        int: current guess line (starting at zero)
        '''
        return self.guess_line


    def submit(self, guess):
        '''
        Submit a new user guess, at the current submission line
        The guess is compared to the solution
        The corresponding score is added to the game and can be requested using get_score
        A guess is composed of an array of colors (numbers)
        Returns True if the guess matches the solution
        '''
        if self.guess_line >= self.lines:
            return False

        reference = [self.solution[i] for i in range(self.pins)]
        proposal = [guess[i] for i in range(self.pins)]

        found = 0
        for i in range(self.pins):
            if reference[i] == proposal[i]:
                found += 1
                proposal[i] = 'x'
                reference[i] = 'x'

        close = 0
        for i in range(self.pins):
            if proposal[i] != 'x':
                for j in range(self.pins):
                    if reference[j] != 'x' and reference[j] == proposal[i]:
                        close += 1
                        proposal[i] = 'x'
                        reference[j] = 'x'
                        j = self.pins

        assert found <= self.pins
        assert close <= self.pins
        assert found + close <= self.pins

        #print(self.guess_line, self.solution, guess, reference, proposal, found, close)

        self.scores[self.guess_line] = [found, close]
        self.board[self.guess_line] = [guess[i] for i in range(self.pins)]
        self.guess_line += 1

        return found == 5


    def new_game(self):
        '''
        Reset the current game
        '''
        self.board = [['x' for i in range(self.pins)] for t in range(self.lines)]
        self.solution = [str(random.randint(0,self.colors-1)) for i in range(self.pins)]
        self.scores = [[0,0] for t in range(self.lines)]
        self.guess_line = 0
