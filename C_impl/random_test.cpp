#include "2048.h"

#include <stdio.h>

int main(){
    printf("Hi, 2048 random play test\n");
    Game2048 env = Game2048();
    std::default_random_engine generator;
    generator.seed(std::random_device{}());
    env.init_board();
    int cnt, i, moves[4], m, r;
    while((cnt = env.legal_moves(moves)) > 0){
        env.print_state();
        std::uniform_int_distribution<int> cntdis(0,cnt-1);
        m = moves[cntdis(generator)];

        printf("Possible moves");
        for(i=0;i<cnt;i++){
            if(moves[i] == m) printf(" [%s]", env.move_name(moves[i]));
            else printf(" %s", env.move_name(moves[i]));
        }
        printf("\n");
        r = env.proceed(m);
        printf("Reward : %d\n\n", r);
    }
    return 0;
}
