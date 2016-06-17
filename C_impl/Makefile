CC = g++
CFLAGS = -std=c++11

all: random_test train

random_test: 2048
	$(CC) $(CFLAGS) random_test.cpp 2048.o -o random_test
train: 2048 vl_light
	$(CC) $(CFLAGS) train.cpp 2048.o vl_light.o -o train
2048:
	$(CC) $(CFLAGS) 2048.cpp -c
vl_light:
	$(CC) $(CFLAGS) vl_light.cpp -c
clean:
	rm *.o
	rm train
	rm random_test
