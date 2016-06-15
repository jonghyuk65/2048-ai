import numpy as np
import random
import time
from environment.Simple2048 import Simple2048
import cPickle as pickle

class ntuple_light(object):
    # value network learning with n(4)-tuple, light weight

    def __init__(self, verbose = False, timecut = 0.1, filename = None, depth = 1, show_arg = False, xtype = 'max'):
        self.verbose = verbose
        self.timecut = timecut
        self.env = Simple2048()

        # weights
        self.dim = 1
        if xtype == 'max':
            self.extract_x = self.max_x
        elif xtype == 'mean':
            self.extract_x = self.mean_x
        elif xtype == 'meanquad':
            self.extract_x = self.meanquad_x
            self.dim = 2;
        elif xtype == 'meandiffquad':
            self.extract_x = self.meandiffquad_x
            self.dim = 3;

        self.v1 = [np.zeros(self.dim+1) for i in range(39)] # row score, init by 0
        self.v2 = [np.zeros(self.dim+1) for i in range(14)] # box score, init by 0
        self.grad_v1 = [np.zeros(self.dim+1) for i in range(39)] # row grad, init by 0
        self.grad_v2 = [np.zeros(self.dim+1) for i in range(14)] # box grad, init by 0
        self.grad_count = 0
        self.grad_upd_term = 100
        self.rank2idx_row, self.rank2idx_box = self.rank2idx_precalc()

        self.depth = depth
        if filename is not None:
            self.load(filename)
            if show_arg:
                for v in self.v1: print v
                for v in self.v2: print v

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

    def row2rank(self, v):
        r = []
        r.append((1 if v[0]>v[1] else 0) + (1 if v[0]>v[2] else 0) + (1 if v[0]>v[3] else 0))
        r.append((1 if v[1]>v[0] else 0) + (1 if v[1]>v[2] else 0) + (1 if v[1]>v[3] else 0))
        r.append((1 if v[2]>v[0] else 0) + (1 if v[2]>v[1] else 0) + (1 if v[2]>v[3] else 0))
        r.append((1 if v[3]>v[0] else 0) + (1 if v[3]>v[1] else 0) + (1 if v[3]>v[2] else 0))
        return r

    def grouping_idens(self, rs, idens):
        n = len(rs)
        c = [0]*n
        eqv_classes = []
        for i in range(n):
            if c[i] == 1:
                continue
            eqv_class = [rs[i]]
            for j in range(i+1, n):
                for trans in idens:
                    if [rs[i][trans[k]] for k in range(4)] == rs[j]:
                        eqv_class.append(rs[j])
                        c[j] = 1
                        break
            eqv_classes.append(eqv_class)
        rank2idx = [0 for i in range(4*4*4*4)]
        for idx, eqv_class in enumerate(eqv_classes):
            for rank in eqv_class:
                rank2idx[rank[0]*4*4*4 + rank[1]*4*4 + rank[2]*4 + rank[3]] = idx
        return rank2idx

    def rank2idx_precalc(self):
        rs = []
        v = [0, 0, 0, 0]
        while True:
            r = self.row2rank(v)
            flag = True
            for old_r in rs:
                if old_r == r:
                    flag = False
                    break
            if flag: rs.append(r)
            i = 3
            while i >= 0:
                v[i] = v[i] + 1
                if v[i] == 4:
                    v[i] = 0
                    i = i - 1
                else:
                    break
            if v == [0,0,0,0]:
                break
        return self.grouping_idens(rs, [[0,1,2,3],[3,2,1,0]]), \
               self.grouping_idens(rs, [[0,1,2,3],[2,0,3,1],[3,2,1,0],[1,3,0,2], \
                                        [1,0,3,2],[3,1,2,0],[2,3,0,1],[0,2,1,3]])

    def save(self, filename):
        with open(filename, 'w') as f:
            pickle.dump(self.v1, f)
            pickle.dump(self.v2, f)

    def load(self, filename, verbose = False):
        with open(filename, 'r') as f:
            self.v1 = pickle.load(f)
            self.v2 = pickle.load(f)

    def max_x(self, row):
        return np.array([max(row) / 10., 1.])

    def mean_x(self, row):
        row_mean = np.mean([2**r for r in row]) # 0 as 1 for simplicity
        return np.array([np.log2(row_mean) / 10., 1.])

    def meanquad_x(self, row):
        row_mean = np.mean([2**r for r in row]) # 0 as 1 for simplicity
        x = np.log2(row_mean) / 10.
        return np.array([x * x, x, 1.])

    def meandiffquad_x(self, row):
        row_mean = np.mean([2**r for r in row]) # 0 as 1 for simplicity
        x = np.log2(row_mean) / 10.
        d = (max(row)-min(row)) / 10.
        return np.array([x * x, x, d, 1.])

    def row2idx(self, row):
        rank = self.row2rank(row)
        x = self.extract_x(row)
        return (self.rank2idx_row[rank[0]*4*4*4 + rank[1]*4*4 + rank[2]*4 + rank[3]], x)

    def box2idx(self, row):
        rank = self.row2rank(row)
        x = self.extract_x(row)
        return (self.rank2idx_box[rank[0]*4*4*4 + rank[1]*4*4 + rank[2]*4 + rank[3]], x)

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
        vsum = 0.
        for (idx, x) in idx1:
            vsum = vsum + np.dot(self.v1[idx], x)
        for (idx, x) in idx2:
            vsum = vsum + np.dot(self.v2[idx], x)
        return vsum

    def upd_eval(self, board, delta_v):
        idx1, idx2 = self.board2idxs(board)
        for (idx, x) in idx1:
            self.grad_v1[idx] = self.grad_v1[idx] + delta_v * x
        for (idx, x) in idx2:
            self.grad_v2[idx] = self.grad_v2[idx] + delta_v * x
        self.grad_count = self.grad_count + 1
        if self.grad_count == self.grad_upd_term:
            grad_sum1 = np.zeros(self.dim+1)
            for idx in range(39):
                grad_sum1 = grad_sum1 + self.grad_v1[idx]
                self.v1[idx] = self.v1[idx] + self.grad_v1[idx]
                self.grad_v1[idx] = np.zeros(self.dim+1)
            grad_sum2 = np.zeros(self.dim+1)
            for idx in range(14):
                grad_sum2 = grad_sum2 + self.grad_v2[idx]
                self.v2[idx] = self.v2[idx] + self.grad_v2[idx]
                self.grad_v2[idx] = np.zeros(self.dim+1)
            self.grad_count = 0

    def eval_move(self, board, m):
        r, s_after = self.env.do_move_emulate(board, m)
        if r is None:
            return None
        return r + self.eval_board(s_after)

    def movename(self, move):
        return ['left', 'down', 'right', 'up'][move]

    def max_eval(self, board, verbose = False, needVal = False):
        vals = []
        moves = []
        for m in range(4):
            r = self.eval_move(board, m)
            if r is not None:
                vals.append(r)
                moves.append(m)
        if needVal:
            if len(vals) == 0: return 0
            return max(vals)
        if len(moves) == 0:
            return None
        if verbose: print [(self.movename(moves[i]), vals[i]) for i in range(len(moves))]
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

    def train_playout(self, lr = 0.001, epsilon = 0):
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

    def max_eval_ts(self, board, depth, verbose, isRoot):
        if depth == 1:
            if isRoot:
                return self.max_eval(board, verbose = verbose)
            return self.max_eval(board, verbose = False, needVal = True)
        moves = []
        vals = []
        for m in range(4):
            r, s_after = self.env.do_move_emulate(board, m)
            if r is None: continue
            v = 0
            cnt = 0
            for i in range(16):
                if s_after[i] == 0:
                    s_after[i] = 1
                    v = v + 0.9 * self.max_eval_ts(s_after, depth-1, False, False)
                    s_after[i] = 2
                    v = v + 0.1 * self.max_eval_ts(s_after, depth-1, False, False)
                    cnt = cnt + 1
                    s_after[i] = 0
            v = r + v / cnt
            moves.append(m)
            vals.append(v)
        if isRoot and verbose: print [(self.movename(moves[i]), vals[i]) for i in range(len(moves))]
        maxv = max(vals)
        if not isRoot:
            if len(vals) == 0: return 0
            return maxv
        max_moves = []
        for i in range(len(moves)):
            if vals[i] == maxv:
                max_moves.append(moves[i])
        m = random.choice(max_moves)
        if isRoot and verbose: print "Move : ", self.movename(m)
        return m

    def get_move(self, board):
        board = [board[i][j] for i in range(4) for j in range(4)]
        m = self.max_eval_ts(board, self.depth, self.verbose, True)
        return m
