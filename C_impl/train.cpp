#include "vl_light.h"

#include <cstdio>
#include <ctime>

void vl_lr_scenario(int epoch, double *lr){
    lr[0] = 0; lr[1] = 0; lr[2] = 0; lr[3] = 0;
    if(epoch <= 500000){
        lr[1] = 0.001;
        lr[3] = 0.001;
    }
    else if(epoch <= 1000000){
        lr[0] = 0.001;
        lr[1] = 0.001;
        lr[3] = 0.001;
    }
    else{
        lr[0] = 0.001;
        lr[1] = 0.001;
        lr[2] = 0.001;
        lr[3] = 0.001;
    }
}

void train_vl(){
    const clock_t begin_time = clock();
    printf("Hi, 2048 train Value Network light\n");
    int epoch;
    VL_light agent = VL_light();
    Game2048 env = Game2048();
    double lr[4];
    int cnt, i, moves[4], a, r, r_sum, max_v, dropout;
    board_t s, s_next;
    char filename[20];
    //agent.verbose = 1;
    int cont = 0;
    if(cont){
        // load
        FILE *fp = fopen("model", "rb");
        int i;
        fread(&agent.v_str[i], sizeof(double) * 4, 39, fp);
        fread(&agent.v_box[i], sizeof(double) * 4, 14, fp);
        fclose(fp);
    }

    std::default_random_engine generator;
    generator.seed(std::random_device{}());
    std::uniform_int_distribution<int> dropdis(0,10);

    for(epoch = 1; epoch <= 1500000; epoch++){
        vl_lr_scenario(epoch, lr);
        env.init_board();
        r_sum = 0;
        double loss, loss_sum = 0;
        int loss_cnt = 0;
        while((cnt = env.legal_moves(moves)) > 0){
            s = env.board;
            a = agent.get_move(s);
            r = env.proceed(a);
            r_sum += r;

            dropout = dropdis(generator);
            if(dropout == 0){
                s_next = env.board;
                loss = agent.learn_move(s, a, s_next);
                loss_sum += loss; loss_cnt++;
            }
        }
        if(loss_cnt == 0) loss_cnt = 1;
        agent.upd_grad(lr);
        max_v = env.max_val();

        printf("%10.2f Epoch %7d: %7d, %5d, %lf\n", float( clock () - begin_time ) /  CLOCKS_PER_SEC, epoch, r_sum, max_v, loss_sum / loss_cnt);

        if(epoch % 250000 == 0){
            for(i=0;i<39;i++) printf("%9.2lf %9.2lf %9.2lf %9.2lf\n", agent.v_str[i].alpha, agent.v_str[i].beta, agent.v_str[i].gamma, agent.v_str[i].delta);
            for(i=0;i<14;i++) printf("%9.2lf %9.2lf %9.2lf %9.2lf\n", agent.v_box[i].alpha, agent.v_box[i].beta, agent.v_box[i].gamma, agent.v_box[i].delta);
            // save
            sprintf(filename, "model_%d",epoch);
            FILE *fp = fopen(filename, "wb");
            int i;
            fwrite(&agent.v_str[i], sizeof(double) * 4, 39, fp);
            fwrite(&agent.v_box[i], sizeof(double) * 4, 14, fp);
            fclose(fp);
        }
    }
}

int main(){
    train_vl();
    return 0;
}
