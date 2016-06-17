#ifndef c_2048_
#define c_2048_

#include <cstdint>
#include <random>

#define MOVE_LEFT 0
#define MOVE_RIGHT 1
#define MOVE_UP 2
#define MOVE_DOWN 3

#define board_t uint64_t

class Game2048{
public:
    board_t board;
    Game2048();
    void init_board();
    void add_rand();
    void add_rand(uint64_t src, uint64_t *dest);
    int proceed(int m);
    int move(uint64_t src, uint64_t *dest, int m);
    int legal_moves(int *move_list);
    int legal_moves(uint64_t src, int *move_list);
    void print_state();
    void print_state(uint64_t board);
    const char* move_name(int m);
    uint64_t transpose(uint64_t src);
    int max_val();
    int max_val(uint64_t src);
private:
    int move_left[1<<16];
    int move_right[1<<16];
    int reward_left[1<<16];
    int reward_right[1<<16];
    void precalc();
    std::default_random_engine generator;
};

#endif
