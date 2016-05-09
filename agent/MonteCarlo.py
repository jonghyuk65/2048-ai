import numpy as np
import random
import time
from environment.Simple2048 import Simple2048

class SimpleMC(object):
    # Simple Monte Carlo Simulation
    # Uses random playout method

    def __init__(self, verbose = False, timecut = 0.1):
        self.verbose = verbose
        self.timecut = timecut
        self.env = Simple2048()

    def RandomPlayout(self, board, d):
        # starts with left move
        self.env.init_board(board)
        moves = self.env.legal_moves()
        if not d in moves: return 0
        rsum = self.env.do_move(d)
        while True:
            m = self.env.legal_moves()
            if len(m) == 0:
                break
            p = random.randrange(len(m))
            r = self.env.do_move(p)
            rsum = rsum + r
        return rsum

    def get_move(self, board):
        playcount = 0
        playsum = np.zeros(4)
        start = time.time()
        while time.time() - start < self.timecut:
            for i in range(4):
                playsum[i] = playsum[i] + self.RandomPlayout(board, i)
            playcount = playcount + 1
        maxsum = max(playsum)
        moves = [i for i in range(4) if playsum[i] == maxsum]
        if self.verbose:
            print "MC ", playcount, playsum/float(playcount)

        return moves[random.randrange(len(moves))]
