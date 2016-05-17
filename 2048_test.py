from agent.SimpleAgent import RandomAgent
from agent.SimpleAgent import MaxMerge
from agent.MonteCarlo import SimpleMC
from agent.vl import ntuple
from agent.environment.Simple2048 import Simple2048

import time
import numpy as np

def test(agent):
    env = Simple2048()
    env.init_board()
    score = 0
    movecount = 0
    while True:
        #env.printState()
        moves = env.legal_moves()
        if len(moves) == 0: break
        board = env.getBoard_plane()
        move = agent.get_move(board)
        r = env.do_move(move)
        movecount = movecount + 1
        score = score + r
    maxval = env.maxVal()
    return score, maxval, movecount

def testAgent(N, agent):
    print "Test ", agent.__class__.__name__
    res = np.zeros([N, 4])
    for i in range(N):
        start = time.time()
        score, v, movecount = test(agent)
        res[i,0] = time.time()-start
        res[i,1] = movecount
        res[i,2] = score
        res[i,3] = v
        print i+1, ":", res[i]
    print "Results:", sum(res[:,2]) / float(N), max(res[:,3])
    for i in range(9,13):
        cnt = 0
        for j in range(N):
            if res[j,3] >= 2**i:
                cnt = cnt + 1
        print 2**i, ":", cnt / float(N)
    print ""

if __name__ == '__main__':
    testAgent(10, RandomAgent())
    testAgent(10, MaxMerge())
    testAgent(10, SimpleMC())
    #testAgent(10, ntuple(filename = 'models/?'))
