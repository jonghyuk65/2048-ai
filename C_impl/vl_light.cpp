#include "vl_light.h"

#include <cmath>

VL_light::VL_light(){
    test_env = Game2048();
    precalc();
    int i;
    for(i=0;i<39;i++){ v_str[i] = {0,0,0,0}; sample_str[i].clear(); }
    for(i=0;i<14;i++){ v_box[i] = {0,0,0,0}; sample_box[i].clear(); }
}

void VL_light::precalc(){
    int idx, sym_idx, i, j, v[4], w[4], rank_idx;
    int idx_rank_straight[1<<8], idx_rank_box[1<<8], straight_cnt = 0, box_cnt = 0;
    int sym_straight[1][4] = {{3,2,1,0}}, sym_box[7][4] = {{1,0,3,2},{2,0,3,1},{0,2,1,3},{3,2,1,0},{2,3,0,1},{1,3,0,2},{3,1,2,0}};
    for(idx = 0; idx < (1<<8); idx++){ idx_rank_straight[idx] = -1; idx_rank_box[idx] = -1; }
    for(idx = 0; idx < (1<<8); idx++){
        v[0] = (idx&(0xC0))>>6; v[1] = (idx&(0x30))>>4; v[2] = (idx&(0x0C))>>2; v[3] = idx&(0x03);
        for(i=0;i<4;i++){
            w[i] = 0;
            for(j=0;j<4;j++){
                if(v[j] < v[i]) w[i]++;
            }
            if(v[i] != w[i]) break;
        }
        if(i < 4) continue;

        rank_idx = -1;
        for(i=0;i<1;i++){
            for(j=0;j<4;j++) w[j] = v[sym_straight[i][j]];
            sym_idx = (w[0]<<6) + (w[1]<<4) + (w[2]<<2) + w[3];
            if(idx_rank_straight[sym_idx] > -1){
                rank_idx = idx_rank_straight[sym_idx];
            }
        }
        if(rank_idx == -1) rank_idx = straight_cnt++;
        idx_rank_straight[idx] = rank_idx;

        rank_idx = -1;
        for(i=0;i<7;i++){
            for(j=0;j<4;j++) w[j] = v[sym_box[i][j]];
            sym_idx = (w[0]<<6) + (w[1]<<4) + (w[2]<<2) + w[3];
            if(idx_rank_box[sym_idx] > -1){
                rank_idx = idx_rank_box[sym_idx];
            }
        }
        if(rank_idx == -1) rank_idx = box_cnt++;
        idx_rank_box[idx] = rank_idx;
    }

    for(idx = 0; idx < (1<<16); idx++){
        double x, d;
        v[0] = (idx&(0xF000))>>12; v[1] = (idx&(0x0F00))>>8; v[2] = (idx&(0x00F0))>>4; v[3] = idx&(0x000F);
        x = ((1<<v[0])+(1<<v[1])+(1<<v[2])+(1<<v[3]))/4.; d = 0;
        for(i=0;i<4;i++){
            w[i] = 0;
            for(j=0;j<4;j++){
                if(v[j] < v[i]) w[i]++;
                if(v[i] - v[j] > d) d = v[i] - v[j];
            }
        }
        x = log2(x)/10.; d = d/10.;
        rank_idx = (w[0]<<6) + (w[1]<<4) + (w[2]<<2) + w[3];
        str[idx].idx = idx_rank_straight[rank_idx];
        str[idx].x = x; str[idx].d = d;
        box[idx].idx = idx_rank_box[rank_idx];
        box[idx].x = x; box[idx].d = d;
    }
}

void VL_light::board2idxs(board_t s, struct info *s_str, struct info *s_box){
    s_str[0] = str[ (s>>48) & UINT64_C(0xFFFF) ];
    s_str[1] = str[ (s>>32) & UINT64_C(0xFFFF) ];
    s_str[2] = str[ (s>>16) & UINT64_C(0xFFFF) ];
    s_str[3] = str[ (s>>0 ) & UINT64_C(0xFFFF) ];
    board_t st = test_env.transpose(s);
    s_str[4] = str[ (st>>48) & UINT64_C(0xFFFF) ];
    s_str[5] = str[ (st>>32) & UINT64_C(0xFFFF) ];
    s_str[6] = str[ (st>>16) & UINT64_C(0xFFFF) ];
    s_str[7] = str[ (st>>0 ) & UINT64_C(0xFFFF) ];

    s_box[0] = box[ ((s>>48) & UINT64_C(0xFF00)) + ((s>>40) & UINT64_C(0x00FF)) ];
    s_box[1] = box[ ((s>>44) & UINT64_C(0xFF00)) + ((s>>36) & UINT64_C(0x00FF)) ];
    s_box[2] = box[ ((s>>40) & UINT64_C(0xFF00)) + ((s>>32) & UINT64_C(0x00FF)) ];
    s_box[3] = box[ ((s>>32) & UINT64_C(0xFF00)) + ((s>>24) & UINT64_C(0x00FF)) ];
    s_box[4] = box[ ((s>>28) & UINT64_C(0xFF00)) + ((s>>20) & UINT64_C(0x00FF)) ];
    s_box[5] = box[ ((s>>24) & UINT64_C(0xFF00)) + ((s>>16) & UINT64_C(0x00FF)) ];
    s_box[6] = box[ ((s>>16) & UINT64_C(0xFF00)) + ((s>>8 ) & UINT64_C(0x00FF)) ];
    s_box[7] = box[ ((s>>12) & UINT64_C(0xFF00)) + ((s>>4 ) & UINT64_C(0x00FF)) ];
    s_box[8] = box[ ((s>>8 ) & UINT64_C(0xFF00)) + ((s>>0 ) & UINT64_C(0x00FF)) ];
}

double VL_light::evaluate_board(board_t s){
    int i;
    double v, v_sum = 0;
    struct weights w;
    struct info x, s_str[8], s_box[9];
    board2idxs(s, s_str, s_box);
    //test_env.print_state(s);
    //for(i=0;i<8;i++) printf("%d %lf %lf\n", s_str[i].idx, s_str[i].x, s_str[i].d);
    //for(i=0;i<9;i++) printf("%d %lf %lf\n", s_box[i].idx, s_box[i].x, s_box[i].d);
    for(i=0;i<8;i++){
        x = s_str[i];
        w = v_str[x.idx];
        v = w.alpha * x.x * x.x + w.beta * x.x + w.gamma * x.d + w.delta;
        v_sum += v;
    }
    for(i=0;i<9;i++){
        x = s_box[i];
        w = v_box[x.idx];
        v = w.alpha * x.x * x.x + w.beta * x.x + w.gamma * x.d + w.delta;
        v_sum += v;
    }
    return v_sum;
}

double VL_light::evaluate_move(board_t s, int a){
    int r;
    double v;
    board_t sp;

    r = test_env.move(s, &sp, a);
    if(r == -1) r = 0;
    v = evaluate_board(sp);

    return r + v;
}

int VL_light::get_move(board_t s){
    int a_max, a, i;
    double v_max, v;
    int moves[4], cnt;
    cnt = test_env.legal_moves(s, moves);
    if(cnt == 0) return -1;
    if(verbose) test_env.print_state(s);
    for(i=0;i<cnt;i++){
        a = moves[i];
        v = evaluate_move(s, a);
        if(verbose){
            printf("%s: %lf ", test_env.move_name(a), v);
        }
        if(i == 0){ v_max = v; a_max = a; }
        else if(v_max < v){ v_max = v; a_max = a; }
    }
    if(verbose) printf("\n");
    return a_max;
}

void VL_light::accum_sample(board_t s, double v){
    int i;
    struct info x, s_str[8], s_box[9];
    board2idxs(s, s_str, s_box);
    for(i=0;i<8;i++){
        x = s_str[i];
        sample_str[x.idx].push_back( std::make_pair(x.x, std::make_pair(x.d, v)) );
    }
    for(i=0;i<9;i++){
        x = s_box[i];
        sample_box[x.idx].push_back( std::make_pair(x.x, std::make_pair(x.d, v)) );
    }
}

void VL_light::upd_grad(double *lr){
    int i,j;
    std::pair<double, std::pair<double, double> > sample;
    double x,d,v;

    for(j=0;j<39;j++){
        for(i=0;i<sample_str[j].size();i++){
            sample = sample_str[j][i];
            x = sample.first; d = sample.second.first; v = sample.second.second;
            v_str[j].alpha += x * x * v * lr[0];
            v_str[j].beta  += x * v * lr[1];
            v_str[j].gamma += d * v * lr[2];
            v_str[j].delta += v * lr[3];
        }
        sample_str[j].clear();
    }

    for(j=0;j<14;j++){
        for(i=0;i<sample_box[j].size();i++){
            sample = sample_box[j][i];
            x = sample.first; d = sample.second.first; v = sample.second.second;
            v_box[j].alpha += x * x * v * lr[0];
            v_box[j].beta  += x * v * lr[1];
            v_box[j].gamma += d * v * lr[2];
            v_box[j].delta += v * lr[3];
        }
        sample_box[j].clear();
    }
}

double VL_light::learn_move(board_t s, int a, board_t s_next){
    int r, r_next, a_next;
    board_t sp, sp_next;
    double diff;
    r = test_env.move(s, &sp, a);
    a_next = get_move(s_next);
    if(a_next == -1){
        diff = 0 - evaluate_board(sp);
    }
    else{
        r_next = test_env.move(s_next, &sp_next, a_next);
        diff = r_next + evaluate_board(sp_next) - evaluate_board(sp);
    }
    accum_sample(sp, diff);
    return diff;
}
