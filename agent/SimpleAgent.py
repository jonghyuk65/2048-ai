import random

class RandomAgent(object):
    # Play randomly

    def __init__(self):
        pass

    def get_move(self, board):
        return random.randrange(4)

class MaxMerge(object):
    # Find Max Merge

    def __init__(self):
        pass

    def mergerow(self, row):
        b = [row[0], row[1], row[2], row[3]]
        i = 0
        moved = False
        merged = 0
        while i < 3:
            f = -1
            if b[i] == 0:
                for j in range(i+1,4):
                    if b[j] > 0:
                        f = j
                        break
            else:
                for j in range(i+1, 4):
                    if b[j] > 0:
                        if b[j] == b[i]:
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
                moved = True
            i = i + cont
        return (merged, moved)

    def mergeleft(self, board):
        merged = 0
        moved = False
        for i in range(4):
            (rowmerged, rowmoved) = self.mergerow(board[i])
            merged = merged + rowmerged
            moved = (moved or rowmoved)
        return (merged, moved)

    def rotate(self, board):
        cnt = 0
        newboard = [[0]*4, [0]*4, [0]*4, [0]*4]
        for j in range(3,-1,-1):
            for i in range(4):
                newboard[i][j] = board[cnt/4][cnt%4]
                cnt = cnt + 1
        return newboard

    def get_move(self, board):
        val = [0]*4
        for i in range(4):
            (val[i],moved) = self.mergeleft(board)
            if moved == False: val[i] = -1
            board = self.rotate(board)
        #print val
        moves = []
        for i in range(4):
            flag = True
            for j in range(4):
                if val[i]<val[j]:
                    flag = False
                    break
            if flag: moves.append(i)
        return moves[random.randrange(len(moves))]
