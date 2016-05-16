from __future__ import print_function
import time
import os
from agent.vl import ntuple

train_time = time.strftime("%m%d%H%M%S")

def train(agent):
    # playouts by policy in agent
    start = time.time()
    alpha = 0.0025
    save_period = 50000
    num_epoch = 1000000
    for epoch in range(num_epoch):
        score, maxval = agent.train_playout(lr = alpha)
        print("%010.6f Epoch %d: Score %d, Max %d" % (time.time() - start, epoch, score, maxval))
        if epoch % save_period == 0 and epoch > 0:
            agent.save(filename = 'models/vl_{}_{}'.format(train_time, epoch))

def main(argv):
    agent = ntuple(verbose = False)
    train(agent)

if __name__ == '__main__':
    import sys
    exit(main(sys.argv[1:]))
