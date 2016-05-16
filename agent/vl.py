import numpy as np
import random
import time
from environment.Simple2048 import Simple2048

class ntuple(object):
    # value network learning with n(4)-tuple

    def __init__(self, verbose = False, timecut = 0.1):
        self.verbose = verbose
        self.timecut = timecut
        self.env = Simple2048()
        self.v = [0 for i in range(18*18*18*18)] # init by 0

    def row2idx(self, row):
        return row[0] * 18 * 18 * 18 + row[1] * 18 * 18 + row[2] * 18 + row[3]

    def board2idxs(self, board):
        tuples = [[0,1,2,3],
                  [4,5,6,7],
                  [8,9,10,11],
                  [12,13,14,15],
                  [0,4,8,12],
                  [1,5,9,13],
                  [2,6,10,14],
                  [3,7,11,15]]
        idxs = []
        for tp in tuples:
            idxs.append(self.row2idx([board[tp[i]] for i in range(4)]))
        return idxs

    def eval_board(self, board):
        idxs = self.board2idxs(board)
        vsum = 0
        for idx in idxs:
            vsum = vsum + self.v[idx]
        return vsum

    def upd_eval(self, board, delta_v):
        idxs = self.board2idxs(board)
        for idx in idxs:
            self.v[idx] = self.v[idx] + delta_v

    def eval_move(self, board, m):
        r, s_after = self.env.do_move_emulate(board, m)
        if r == -1:
            return -1
        return r + self.eval_board(s_after)

    def movename(self, move):
        return ['left', 'down', 'right', 'up'][move]

    def max_eval(self, board, verbose = False):
        vs = []
        for m in range(4):
            r = self.eval_move(board, m)
            vs.append(r)
        if verbose: print [(self.movename(i), vs[i]) for i in range(4)]
        maxv = max(vs)
        if maxv == -1: return -1
        moves = []
        for i in range(4):
            if vs[i] == maxv:
                moves.append(i)
        m = random.choice(moves)
        if verbose: print "Move : ", self.movename(m)
        return m

    def learn_move(self, s, a, s_next, lr):
        r, s_after = self.env.do_move_emulate(s, a)
        a_next = self.max_eval(s_next)
        if a_next == -1: # terminal
            self.upd_eval(s_after, lr * (0 - self.eval_board(s_after)))
            return
        r_next, s_next_after = self.env.do_move_emulate(s_next, a_next)
        self.upd_eval(s_after, lr * (r_next + self.eval_board(s_next_after) - self.eval_board(s_after)))

    def train_playout(self, lr = 0.001):
        self.env.init_board()
        rsum = 0
        while True:
            # do move
            moves = self.env.legal_moves()
            if len(moves) == 0: break
            s = self.env.getBoard_copy()
            if self.verbose: self.env.printState()
            m = self.max_eval(s, verbose = self.verbose)
            r = self.env.do_move(m)
            rsum = rsum + r

            # update
            s_next = self.env.getBoard_copy()
            self.learn_move(s, m, s_next, lr)
        return rsum, self.env.maxVal()

    def get_move(self, board):
        # 1ply
        m = self.max_eval(board, verbose = self.verbose)
        return m
