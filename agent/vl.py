import numpy as np
import random
import time
from environment.Simple2048 import Simple2048
import cPickle as pickle

class ntuple(object):
    # value network learning with n(4)-tuple

    def __init__(self, verbose = False, timecut = 0.1, filename = None):
        self.verbose = verbose
        self.timecut = timecut
        self.env = Simple2048()
        self.v1 = [0 for i in range(18*18*18*18)] # row score, init by 0
        self.v2 = [0 for i in range(18*18*18*18)] # box score, init by 0
        if filename is not None:
            self.load(filename)
        # 0 1 2 3
        # 4 5 6 7
        # 8 9 10 11
        # 12 13 14 15
        self.tuples1 = []
        for i in range(4):
            tp = []
            for j in range(4):
                tp.append(4*i+j)
            self.tuples1.append(tp)
        for j in range(4):
            tp = []
            for i in range(4):
                tp.append(4*i+j)
            self.tuples1.append(tp)
        self.tuples2 = []
        for i in range(3):
            for j in range(3):
                self.tuples2.append([4*i+j, 4*i+j+1, 4*(i+1)+j, 4*(i+1)+j+1])

    def save(self, filename):
        with open(filename, 'w') as f:
            pickle.dump(self.v1, f)
            pickle.dump(self.v2, f)

    def load(self, filename):
        with open(filename, 'r') as f:
            self.v1 = pickle.load(f)
            self.v2 = pickle.load(f)

    def row2idx(self, row):
        idx = []
        idx.append(row[0] * 18 * 18 * 18 + row[1] * 18 * 18 + row[2] * 18 + row[3])
        idx.append(row[3] * 18 * 18 * 18 + row[2] * 18 * 18 + row[1] * 18 + row[0])
        return min(idx)

    def box2idx(self, row):
        idx = []
        # 0 1   2 0    3 2  1 3
        # 2 3   3 1    1 0  0 2
        idx.append(row[0] * 18 * 18 * 18 + row[1] * 18 * 18 + row[2] * 18 + row[3])
        idx.append(row[2] * 18 * 18 * 18 + row[0] * 18 * 18 + row[3] * 18 + row[1])
        idx.append(row[3] * 18 * 18 * 18 + row[2] * 18 * 18 + row[1] * 18 + row[0])
        idx.append(row[1] * 18 * 18 * 18 + row[3] * 18 * 18 + row[0] * 18 + row[2])
        return min(idx)

    def board2idxs(self, board):
        idx1 = []
        idx2 = []
        for tp in self.tuples1:
            idx1.append(self.row2idx([board[tp[i]] for i in range(4)]))
        for tp in self.tuples2:
            idx2.append(self.box2idx([board[tp[i]] for i in range(4)]))
        return idx1, idx2

    def eval_board(self, board):
        idx1, idx2 = self.board2idxs(board)
        vsum = 0
        for idx in idx1:
            vsum = vsum + self.v1[idx]
        for idx in idx2:
            vsum = vsum + self.v2[idx]
        return vsum

    def upd_eval(self, board, delta_v):
        idx1, idx2 = self.board2idxs(board)
        for idx in idx1:
            self.v1[idx] = self.v1[idx] + delta_v
        for idx in idx2:
            self.v2[idx] = self.v2[idx] + delta_v

    def eval_move(self, board, m):
        r, s_after = self.env.do_move_emulate(board, m)
        if r is None:
            return None
        return r + self.eval_board(s_after)

    def movename(self, move):
        return ['left', 'down', 'right', 'up'][move]

    def max_eval(self, board, verbose = False):
        vals = []
        moves = []
        for m in range(4):
            r = self.eval_move(board, m)
            if r is not None:
                vals.append(r)
                moves.append(m)
        if len(moves) == 0:
            return None
        if verbose: print [(self.movename(moves[i]), vals[i]) for i in range(4)]
        maxv = max(vals)
        max_moves = []
        for i in range(len(moves)):
            if vals[i] == maxv:
                max_moves.append(moves[i])
        m = random.choice(max_moves)
        if verbose: print "Move : ", self.movename(m)
        return m

    def learn_move(self, s, a, s_next, lr):
        r, s_after = self.env.do_move_emulate(s, a)
        a_next = self.max_eval(s_next)
        if r == None:
            print "ERROR!!, ILLEGAL MOVE"
            print s
            print a
            print s_next
        if a_next == None: # terminal
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
        board = [board[i][j] for i in range(4) for j in range(4)]
        # 1ply
        m = self.max_eval(board, verbose = self.verbose)
        return m
