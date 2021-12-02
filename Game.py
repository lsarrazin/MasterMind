import random

class Game:

    lines = 12
    pins = 5
    colors = 8

    def __init__(self):
        self.new_game()

    
    def get_line(self, line):
        return self.board[line]


    def get_score(self, line):
        return self.scores[line]


    def get_solution(self):
        return self.solution


    def get_guess_line(self):
        return self.guess_line


    def submit(self, guess):
        if self.guess_line >= self.lines:
            return False

        reference = [self.solution[i] for i in range(self.pins)]
        proposal = [guess[i] for i in range(self.pins)]

        found = 0
        for i in range(self.pins):
            if reference[i] == guess[i]:
                found += 1
                proposal[i] = 'x'
                reference[i] = 'x'

        close = 0
        for i in range(self.pins):
            if proposal[i] != 'x':
                for j in range(self.pins):
                    if reference[j] == proposal[i]:
                        close += 1
                        proposal[i] = 'x'
                        reference[j] = 'x'

        print(self.solution, guess, reference, proposal, found, close)

        self.scores[self.guess_line] = [found, close]
        self.board[self.guess_line] = [guess[i] for i in range(self.pins)]
        self.guess_line += 1

        return True


    def new_game(self):
        self.board = [['x' for i in range(self.pins)] for t in range(self.lines)]
        self.solution = [str(random.randint(0,self.colors-1)) for i in range(self.pins)]
        self.scores = [[0,0] for t in range(self.lines)]
        self.guess_line = 0

