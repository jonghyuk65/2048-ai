#ifndef c_vl_light_
#define c_vl_light_

#include "2048.h"
#include<vector>
#include <algorithm>

class VL_light{
public:
    bool verbose = 0;
    struct weights{ double alpha, beta, gamma, delta; };
    struct info{ int idx; double x, d; };
    struct weights v_str[39], v_box[14];
    VL_light();
    int get_move(board_t s);
    double learn_move(uint64_t s, int a, uint64_t s_next);
    void upd_grad(double *lr);
private:
    struct info str[1<<16];
    struct info box[1<<16];
    std::vector< std::pair<double, std::pair<double, double>> > sample_str[39], sample_box[14];
    void precalc();
    Game2048 test_env;
    void board2idxs(uint64_t s, struct info *str_idxs, struct info *box_idxs);
    double evaluate_move(uint64_t s, int a);
    double evaluate_board(uint64_t s);
    void accum_sample(uint64_t s, double v);
};

#endif
