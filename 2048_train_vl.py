from __future__ import print_function
import time
import os
from agent.vl_light import ntuple_light

train_time = time.strftime("%m%d%H%M%S")

def train(agent):
    # playouts by policy in agent
    start = time.time()
    alpha = 0.01
    save_period = 30000
    num_epoch = 300000
    epsilon_plan = [1] * 10000 + [0.5] * 10000 + [0.2] * 10000 + [0] * (num_epoch - 30000)
    for epoch in range(num_epoch):
        score, maxval = agent.train_playout(lr = alpha, epsilon = epsilon_plan[epoch])
        print("%010.6f Epoch %d: Score %d, Max %d" % (time.time() - start, epoch, score, maxval))
        if epoch % save_period == 0 and epoch > 0:
            agent.save(filename = 'models/vl_light_{}_{}'.format(train_time, epoch))

def parse_args(argv):
    import argparse

    parser = argparse.ArgumentParser(description="Train")
    parser.add_argument('-m', '--model', help="model to continue")

    return parser.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    agent = ntuple_light(verbose = False)
    if args.model is not None:
        agent.load(args.model)
    train(agent)

if __name__ == '__main__':
    import sys
    exit(main(sys.argv[1:]))
