import random
import numpy as np

class Simple2048(object):
    def __init__(self):
        self.moveleft = self.precalc()
        # dir order = LDRU
        # 0 1 2 3
        # 4 5 6 7
        # 8 9 10 11
        # 12 13 14 15
        self.directions = [ [[0,1,2,3], [4,5,6,7], [8,9,10,11], [12,13,14,15]],
                            [[12,8,4,0], [13,9,5,1], [14,10,6,2], [15,11,7,3]],
                            [[3,2,1,0], [7,6,5,4], [11,10,9,8], [15,14,13,12]],
                            [[0,4,8,12], [1,5,9,13], [2,6,10,14], [3,7,11,15]] ]

    def precalc(self):
        # moves to left, (next_state, reward, is_moved)
        moves = []
        for idx in range(18*18*18*18):
            row = self.idx2row(idx);
            next_row, reward, is_moved = self.move_row_left(row)
            moves.append((next_row, reward, is_moved))
        return moves

    def idx2row(self, idx):
        return [idx/(18*18*18), (idx/(18*18))%18, (idx/18)%18, idx%18]

    def row2idx(self, row):
        return row[0]*18*18*18+row[1]*18*18+row[2]*18+row[3]

    def move_row_left(self, row):
        r = [row[i] for i in range(4)]
        i = 0
        is_moved = False
        merged = 0
        for i in range(3):
            for j in range(i+1, 4):
                if r[j] > 0:
                    if r[i] == 0:
                        r[i] = r[j]
                        r[j] = 0
                        is_moved = True
                        continue
                    elif r[i] == r[j]:
                        r[i] = r[i] + 1
                        r[j] = 0
                        merged = merged + 2**r[i]
                        is_moved = True
                    break
        return self.row2idx(r), merged, is_moved

    def init_board(self, board = None):
        if board is None:
            board = [0 for i in range(16)]
            board[random.randrange(16)] = 2 if random.randrange(10) == 0 else 1
        else:
            board = [board[i][j] for i in range(4) for j in range(4)]
        self.board = board

    def legal_moves(self):
        moves = []
        for d in range(4):
            flag = False
            for row in self.directions[d]:
                _, _, is_moved = self.moveleft[self.row2idx([self.board[row[i]] for i in range(4)])]
                if is_moved:
                    flag = True
                    break
            if flag: moves.append(d)
        return moves

    def do_move(self, d):
        r = 0
        is_moved = False
        for row in self.directions[d]:
            next_row_idx, reward, is_row_moved = self.moveleft[self.row2idx([self.board[row[i]] for i in range(4)])]
            is_moved = is_moved or is_row_moved
            next_row = self.idx2row(next_row_idx)
            for i in range(4): self.board[row[i]] = next_row[i]
            r = r + reward
        if not is_moved:
            print "ILLEGAL MOVE!!"
            self.printState()
            print "tried ", d
        self.addRand()
        return r

    def addRand(self):
        empty_cells = [i for i in range(16) if self.board[i] == 0]
        if len(empty_cells) == 0: return
        p = random.choice(empty_cells)
        self.board[p] = 2 if random.randrange(10) == 0 else 1

    def do_move_emulate(self, board, d):
        r = 0
        after_state = [board[i] for i in range(16)]
        is_moved = False
        for row in self.directions[d]:
            next_row_idx, reward, is_row_moved = self.moveleft[self.row2idx([after_state[row[i]] for i in range(4)])]
            is_moved = is_moved or is_row_moved
            next_row = self.idx2row(next_row_idx)
            for i in range(4): after_state[row[i]] = next_row[i]
            r = r + reward
        if not is_moved:
            return None, None
        return r, after_state

    def printState(self):
        c = [2**self.board[i] if self.board[i] > 0 else 0 for i in range(16)]
        print np.reshape(c, [4,4])

    def getBoard(self):
        return self.board

    def getBoard_copy(self):
        return [self.board[i] for i in range(16)]

    def getBoard_plane(self):
        board = []
        for i in range(4):
            row = []
            for j in range(4):
                row.append(self.board[i*4+j])
            board.append(row)
        return board

    def maxVal(self):
        return 2**max(self.board)

def movename(move):
    return ['left', 'down', 'right', 'up'][move]

if __name__ == '__main__':
    game = Simple2048()
    game.init_board()
    game.printState()
    while True:
        m = game.legal_moves()
        if len(m) == 0:
            break
        p = random.choice(m)
        r = game.do_move(p)
        print m, movename(p), r
        game.printState()
    print "Game Over"
