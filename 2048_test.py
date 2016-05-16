from agent.SimpleAgent import RandomAgent
from agent.SimpleAgent import MaxMerge
from agent.MonteCarlo import SimpleMC
from agent.environment.Simple2048 import Simple2048
import time
import numpy as np

def test(agent):
    env = Simple2048(None)
    score = 0
    movecount = 0
    while True:
        #env.printState()
        moves = env.legal_moves()
        if len(moves) == 0: break
        board = env.getBoard()
        move = agent.get_move(board)
        if move not in moves:
            continue
        r = env.domove(move)
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
    print ""

if __name__ == '__main__':
    testAgent(10, RandomAgent())
    testAgent(10, MaxMerge())
    testAgent(10, SimpleMC())
