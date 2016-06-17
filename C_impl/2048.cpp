#include "2048.h"

#include <cinttypes>
#include <cstdio>

Game2048::Game2048(){
    board = 0;
    generator.seed(std::random_device{}());
    precalc();
}

void Game2048::precalc(){
    int idx, v[4], rev_idx;
    int i, x, r;
    for(idx=0;idx<(1<<16);idx++){
        v[0] = (idx&(0xF000)) >> 12; v[1] = (idx&(0x0F00)) >> 8; v[2] = (idx&(0x00F0)) >> 4; v[3] = idx&(0x000F);
        rev_idx = (v[3]<<12) + (v[2]<<8) + (v[1]<<4) + v[0];
        x = 0;
        r = 0;
        while(x<3){
            if(v[x] == 0){
                for(i=x+1;i<4;i++){
                    if(v[i] > 0){
                        v[x] = v[i]; v[i] = 0;
                        break;
                    }
                }
                if(i == 4) break;
            }
            else{
                for(i=x+1;i<4;i++){
                    if(v[i] == v[x]){
                        r += (1<<(v[x]+1));
                        v[x]++; v[i] = 0;
                        break;
                    }
                    if(v[i] > 0) break;
                }
                x++;
            }
        }
        move_left[idx] = (v[0]<<12) + (v[1]<<8) + (v[2]<<4) + v[3];
        reward_left[idx] = r;
        move_right[rev_idx] = (v[3]<<12) + (v[2]<<8) + (v[1]<<4) + v[0];
        reward_right[rev_idx] = r;
    }
}

void Game2048::init_board(){
    board = 0;
    add_rand();
    add_rand();
}

void Game2048::add_rand(){ add_rand(board, &board); }
void Game2048::add_rand(uint64_t src, uint64_t *dest){
    uint64_t mask = 0xF, empty[16];
    int i, cnt = 0;
    for(i=0;i<16;i++){
        if( (mask & src) == 0) empty[cnt++] = mask / (0xF);
        mask = mask << 4;
    }
    *dest = src;
    if(cnt == 0) return;
    std::uniform_int_distribution<int> tendis(0,9), cntdis(0,cnt-1);
    int twoorfour_roll = tendis(generator), place_roll = cntdis(generator);
    if(twoorfour_roll == 0) *dest += empty[place_roll] << 1;
    else *dest += empty[place_roll];
}

int Game2048::proceed(int m){
    int r = move(board, &board, m);
    if(r == -1) return -1;
    add_rand();
    return r;
}

int Game2048::move(uint64_t src, uint64_t *dest, int m){
    int r;
    *dest = src;
    if(m == MOVE_LEFT){
        r = reward_left[ (*dest>>48) & UINT64_C(0xFFFF) ]
          + reward_left[ (*dest>>32) & UINT64_C(0xFFFF) ]
          + reward_left[ (*dest>>16) & UINT64_C(0xFFFF) ]
          + reward_left[ (*dest>>0 ) & UINT64_C(0xFFFF) ];
        *dest = (uint64_t(move_left[ (*dest>>48) & UINT64_C(0xFFFF) ]) << 48)
              + (uint64_t(move_left[ (*dest>>32) & UINT64_C(0xFFFF) ]) << 32)
              + (uint64_t(move_left[ (*dest>>16) & UINT64_C(0xFFFF) ]) << 16)
              + (uint64_t(move_left[ (*dest>>0 ) & UINT64_C(0xFFFF) ]));
    }
    else if(m == MOVE_RIGHT){
        r = reward_right[ (*dest>>48) & UINT64_C(0xFFFF) ]
          + reward_right[ (*dest>>32) & UINT64_C(0xFFFF) ]
          + reward_right[ (*dest>>16) & UINT64_C(0xFFFF) ]
          + reward_right[ (*dest>>0 ) & UINT64_C(0xFFFF) ];
        *dest = (uint64_t(move_right[ (*dest>>48) & UINT64_C(0xFFFF) ]) << 48)
              + (uint64_t(move_right[ (*dest>>32) & UINT64_C(0xFFFF) ]) << 32)
              + (uint64_t(move_right[ (*dest>>16) & UINT64_C(0xFFFF) ]) << 16)
              + (uint64_t(move_right[ (*dest>>0 ) & UINT64_C(0xFFFF) ]));
    }
    else if(m == MOVE_UP){
        *dest = transpose(*dest);
        r = reward_left[ (*dest>>48) & UINT64_C(0xFFFF) ]
          + reward_left[ (*dest>>32) & UINT64_C(0xFFFF) ]
          + reward_left[ (*dest>>16) & UINT64_C(0xFFFF) ]
          + reward_left[ (*dest>>0 ) & UINT64_C(0xFFFF) ];
        *dest = (uint64_t(move_left[ (*dest>>48) & UINT64_C(0xFFFF) ]) << 48)
              + (uint64_t(move_left[ (*dest>>32) & UINT64_C(0xFFFF) ]) << 32)
              + (uint64_t(move_left[ (*dest>>16) & UINT64_C(0xFFFF) ]) << 16)
              + (uint64_t(move_left[ (*dest>>0 ) & UINT64_C(0xFFFF) ]));
        *dest = transpose(*dest);
    }
    else if(m == MOVE_DOWN){
        *dest = transpose(*dest);
        r = reward_right[ (*dest>>48) & UINT64_C(0xFFFF) ]
          + reward_right[ (*dest>>32) & UINT64_C(0xFFFF) ]
          + reward_right[ (*dest>>16) & UINT64_C(0xFFFF) ]
          + reward_right[ (*dest>>0 ) & UINT64_C(0xFFFF) ];
        *dest = (uint64_t(move_right[ (*dest>>48) & UINT64_C(0xFFFF) ]) << 48)
              + (uint64_t(move_right[ (*dest>>32) & UINT64_C(0xFFFF) ]) << 32)
              + (uint64_t(move_right[ (*dest>>16) & UINT64_C(0xFFFF) ]) << 16)
              + (uint64_t(move_right[ (*dest>>0 ) & UINT64_C(0xFFFF) ]));
        *dest = transpose(*dest);
    }
    if(src == *dest) return -1;
    return r;
}

uint64_t Game2048::transpose(uint64_t src){
    uint64_t a_9,a_6,a_3,a,a3,a6,a9;
    a_9 = src & UINT64_C(0x000000000000F000);
    a_6 = src & UINT64_C(0x00000000F0000F00);
    a_3 = src & UINT64_C(0x0000F0000F0000F0);
    a   = src & UINT64_C(0xF0000F0000F0000F);
    a3  = src & UINT64_C(0x0F0000F0000F0000);
    a6  = src & UINT64_C(0x00F0000F00000000);
    a9  = src & UINT64_C(0x000F000000000000);
    return (a_9<<36) + (a_6<<24) + (a_3<<12) + a + (a3>>12) + (a6>>24) + (a9>>36);
}

int Game2048::legal_moves(int *move_list){ return legal_moves(board, move_list); }
int Game2048::legal_moves(uint64_t src, int *move_list){
    uint64_t temp_dest;
    int cnt = 0;
    if(move(src, &temp_dest, 0) > -1) move_list[cnt++] = 0;
    if(move(src, &temp_dest, 1) > -1) move_list[cnt++] = 1;
    if(move(src, &temp_dest, 2) > -1) move_list[cnt++] = 2;
    if(move(src, &temp_dest, 3) > -1) move_list[cnt++] = 3;
    return cnt;
}

void Game2048::print_state(){ print_state(board); }
void Game2048::print_state(uint64_t board){
    printf("Game state!\n");
    printf("%.4" PRIX64 "\n", (board>>48) & UINT64_C(0xFFFF) );
    printf("%.4" PRIX64 "\n", (board>>32) & UINT64_C(0xFFFF) );
    printf("%.4" PRIX64 "\n", (board>>16) & UINT64_C(0xFFFF) );
    printf("%.4" PRIX64 "\n", (board>>0 ) & UINT64_C(0xFFFF) );
}

int Game2048::max_val(){ return max_val(board); }
int Game2048::max_val(uint64_t src){
    int i, max_v = 0, v;
    for(i=0;i<16;i++){
        v = src & 0xF;
        if(v > max_v) max_v = v;
        src = src >> 4;
    }
    return 1 << max_v;
}

const char* Game2048::move_name(int m){
    if(m == MOVE_LEFT) return "LEFT";
    if(m == MOVE_RIGHT) return "RIGHT";
    if(m == MOVE_UP) return "UP";
    if(m == MOVE_DOWN) return "DOWN";
    return "";
}
