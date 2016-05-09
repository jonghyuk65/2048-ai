import random
import time
import numpy as np

class Simple2048(object):
    rot = [12, 8, 4, 0, 13, 9, 5, 1, 14, 10, 6, 2, 15, 11, 7, 3]

    def __init__(self, board):
        if board is None:
            board = [0] * 16
            board[random.randrange(16)] = 2 if random.randrange(10) == 0 else 1
        self.b = np.array(board)
        self.b = np.reshape(self.b, [16])

    def canmove_row(self, b):
        for i in range(3):
            if b[i] == 0:
                for j in range(i+1,4):
                    if b[j] > 0:
                        return True
                break
        for i in range(3):
            if b[i] == b[i+1] and b[i]>0:
                return True
        return False

    def canmove(self, c):
        # possibility of move left
        res = False
        for i in range(0,16,4):
            res = res or self.canmove_row(c[i:i+4])
        return res

    def legal_moves(self):
        c = [self.b[i] for i in range(16)]
        moves = []
        for i in range(4):
            if self.canmove(c):
                moves.append(i)
            c = [c[self.rot[i]] for i in range(16)]
        return moves

    def moveleft_row(self, r):
        b = [r[i] for i in range(4)]
        i = 0
        merged = 0
        while i < 3:
            f = -1
            for j in range(i+1, 4):
                if b[j] > 0:
                    if b[i] == 0 or b[i] == b[j]:
                        f = j
                    break
            cont = 1
            if f > -1:
                if b[i] == 0:
                    b[i] = b[f]
                    cont = 0
                else:
                    b[i] = b[i] + 1
                    merged = merged + 2**b[i]
                b[f] = 0
            i = i + cont
        return b, merged

    def moveleft(self, c):
        r_sum = 0
        for i in range(0, 16, 4):
            c[i:i+4], r = self.moveleft_row(c[i:i+4])
            r_sum = r_sum + r
        return r_sum

    def addRand(self, c):
        empty_cells = [i for i in range(16) if c[i] == 0]
        if len(empty_cells) == 0: return
        p = random.randrange(len(empty_cells))
        c[empty_cells[p]] = 2 if random.randrange(10) == 0 else 1

    def domove(self, dir):
        c = [self.b[i] for i in range(16)]
        for i in range(dir): c = [c[self.rot[i]] for i in range(16)]
        r = self.moveleft(c)
        for i in range((4-dir)%4): c = [c[self.rot[i]] for i in range(16)]
        self.addRand(c)
        self.b = np.array(c)
        return r

    def printState(self):
        c = [2**self.b[i] if self.b[i] > 0 else 0 for i in range(16)]
        print np.reshape(c, [4,4])

    def getBoard(self):
        return np.reshape(self.b, [4,4]).tolist()

    def maxVal(self):
        return 2**max(self.b)

def movename(move):
    return ['left', 'down', 'right', 'up'][move]

if __name__ == '__main__':
    b = [[1,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    game = Simple2048(b)
    game.printState()
    while True:
        m = game.legal_moves()
        if len(m) == 0:
            break
        p = random.randrange(len(m))
        r = game.domove(p)
        print m, movename(p), r
        game.printState()
        time.sleep(1)
    print "Game Over"
