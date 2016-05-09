2048 AI

AI Plays http://gabrielecirulli.github.io/2048/

Just for my term project...

Browser game control part is wholly from https://github.com/nneonneo/2048-ai, also idea of optimization techniques. (But we didn't use c, so still slow)

Should install [Remote Control for Firefox](https://github.com/nneonneo/FF-Remote-Control/raw/V_1.2/remote_control-1.2-fx.xpi)

Not going to implement current state of the art methods (tree search with heuristic evaluation: https://github.com/nneonneo/2048-ai, temporal difference learning: https://github.com/aszczepanski/2048)

At first, MCTS was also considered but I suspended that plan because 2048 needs to be played very fast and random tile addition creates wide possibilities.

So just n-ply model of DQN(deep q learning or maybe value learning) is my plan

Currently implemented: random, maximum merge(greedy), monte carlo simulation

TODO: DQN
