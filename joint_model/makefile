CC = g++
CFLAGS = -lm -pthread -Ofast -march=native -Wall -funroll-loops -Wno-unused-result -lgsl -lm -lgslcblas
INCLUDES = -I/usr/local/include
LIBS = -L/usr/local/lib


pte : ransampl.o linelib.o utils.o main.o
	$(CC) $(CFLAGS) -o pte ransampl.o linelib.o utils.o main.o $(INCLUDES) $(LIBS)

ransampl.o : ransampl.c
	$(CC) $(CFLAGS) -c ransampl.c $(INCLUDES) $(LIBS)

linelib.o : linelib.cpp ransampl.h
	$(CC) $(CFLAGS) -c linelib.cpp $(INCLUDES) $(LIBS)

utils.o : utils.cpp
	$(CC) $(CFLAGS) -c utils.cpp $(INCLUDES) $(LIBS)

main.o : main.cpp linelib.o utils.o
	$(CC) $(CFLAGS) -c main.cpp $(INCLUDES) $(LIBS)

clean :
	rm -rf *.o pte
