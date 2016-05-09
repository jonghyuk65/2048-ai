from agent.SimpleAgent import RandomAgent
from agent.SimpleAgent import MaxMerge
from agent.MonteCarlo import SimpleMC
from agent.environment.Simple2048 import Simple2048
import time

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
    scores = 0
    maxval = 0
    for i in range(N):
        start = time.time()
        score, v, movecount = test(agent)
        print i+1, ":", score, v, movecount, time.time()-start
        scores = scores + score
        if maxval < v: maxval = v
    print "Results:", scores / float(N), maxval
    print ""

if __name__ == '__main__':
    testAgent(10, RandomAgent())
    testAgent(10, MaxMerge())
    testAgent(10, SimpleMC())
