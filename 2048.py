#!/usr/bin/python
# -*- coding: utf-8 -*-

''' Help the user achieve a high score in a real game of 2048 by using a move searcher. '''

from __future__ import print_function
import time
import os

def print_board(m):
    for row in m:
        for c in row:
            print('%8d' % c, end=' ')
        print()

def find_best_move(m):
    return 0

def to_val(m):
    return [[(0 if c == 0 else 2**c) for c in row] for row in m]

def movename(move):
    return ['left', 'down', 'right', 'up'][move]

def play_game(gamectrl, agent):
    if gamectrl.get_status() == 'ended':
        gamectrl.restart_game()

    moveno = 0
    start = time.time()
    while 1:
        state = gamectrl.get_status()
        if state == 'ended':
            break
        elif state == 'won':
            time.sleep(0.75)
            gamectrl.continue_game()

        moveno += 1
        board = gamectrl.get_board()
        move = agent.get_move(board)
        if move < 0:
            break
        print("%010.6f: Score %d, Move %d: %s" % (time.time() - start, gamectrl.get_score(), moveno, movename(move)))
        gamectrl.execute_move(move)

    score = gamectrl.get_score()
    board = gamectrl.get_board()
    maxval = max(max(row) for row in to_val(board))
    print("Game over. Final score %d; highest tile %d." % (score, maxval))
    return (score, maxval)

def parse_args(argv):
    import argparse

    parser = argparse.ArgumentParser(description="Use the AI to play 2048 via browser control")
    parser.add_argument('-a', '--agent', help="Select which agent to play (default: random, others: maxmerge, mc(Monte Carlo Simulation), dqn)", default = 'random', choices=('random', 'maxmerge', 'mc', 'dqn'))
    parser.add_argument('-p', '--port', help="Port number to control on (default: 32000 for Firefox, 9222 for Chrome)", type=int)
    parser.add_argument('-b', '--browser', help="Browser you're using. Only Firefox with the Remote Control extension, and Chrome with remote debugging, are supported right now.", default='firefox', choices=('firefox', 'chrome'))
    parser.add_argument('-k', '--ctrlmode', help="Control mode to use. If the browser control doesn't seem to work, try changing this.", default='hybrid', choices=('keyboard', 'fast', 'hybrid'))

    return parser.parse_args(argv)

def main(argv):
    args = parse_args(argv)

    if args.browser == 'firefox':
        from ctrl.ffctrl import FirefoxRemoteControl
        if args.port is None:
            args.port = 32000
        ctrl = FirefoxRemoteControl(args.port)
    elif args.browser == 'chrome':
        from ctrl.chromectrl import ChromeDebuggerControl
        if args.port is None:
            args.port = 9222
        ctrl = ChromeDebuggerControl(args.port)

    if args.ctrlmode == 'keyboard':
        from ctrl.gamectrl import Keyboard2048Control
        gamectrl = Keyboard2048Control(ctrl)
    elif args.ctrlmode == 'fast':
        from ctrl.gamectrl import Fast2048Control
        gamectrl = Fast2048Control(ctrl)
    elif args.ctrlmode == 'hybrid':
        from ctrl.gamectrl import Hybrid2048Control
        gamectrl = Hybrid2048Control(ctrl)

    if args.agent == 'random':
        from agent.SimpleAgent import RandomAgent
        agent = RandomAgent()
    elif args.agent == 'maxmerge':
        from agent.SimpleAgent import MaxMerge
        agent = MaxMerge()
    elif args.agent == 'mc':
        from agent.MonteCarlo import SimpleMC
        agent = SimpleMC(verbose=True)
    elif args.agent == 'dqn':
        # not implemented
        pass

    score, maxval = play_game(gamectrl, agent)

if __name__ == '__main__':
    import sys
    exit(main(sys.argv[1:]))
