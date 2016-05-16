from __future__ import print_function
import time
import os
import cPickle as pickle
from agent.vl import ntuple

train_time = time.strftime("%m%d%H%M%S")

def train(agent):
    # playouts by policy in agent
    start = time.time()
    alpha = 0.0025
    for epoch in range(1000000):
        score, maxval = agent.train_playout(lr = alpha)
        print("%010.6f Epoch %d: Score %d, Max %d" % (time.time() - start, epoch, score, maxval))
        if epoch % 50000 == 49999:
            with open('vl_{}_{}'.format(train_time, epochs)) as f:
                f.save(agent)

def main(argv):
    agent = ntuple(verbose = True)
    train(agent)

if __name__ == '__main__':
    import sys
    exit(main(sys.argv[1:]))
