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
    save_period = 100000
    num_epoch = 1000000
    for epoch in range(num_epoch):
        score, maxval = agent.train_playout(lr = alpha)
        print("%010.6f Epoch %d: Score %d, Max %d" % (time.time() - start, epoch, score, maxval))
        if epoch % save_period == save_period-1:
            with open('vl_{}_{}'.format(train_time, epoch), 'w') as f:
                pickle.dump(agent, f)

def main(argv):
    agent = ntuple(verbose = False)
    train(agent)

if __name__ == '__main__':
    import sys
    exit(main(sys.argv[1:]))
