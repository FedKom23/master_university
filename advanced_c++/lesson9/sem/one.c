CC = gcc
FLAGS = -Wall -Wextra -Werror -I include

OBJS = $(wildcard *.o)
TARGET = sem_program

.PHONY: clean install uninstall

$(TARGET): seminar_main.o src/seminar_main.c include/sem_header.h
	$(CC) $(FLAGS) -o $(TARGET) seminar_main.o

seminar_main.o: src/seminar_main.c include/sem_header.h
	$(CC) $(FLAGS) -c src/seminar_main.c -o seminar_main.o

clean:
	rm -f $(OBJS) $(TARGET)

install: $(TARGET)
	cp $(TARGET) bin/

uninstall:
	rm -f bin/$(TARGET)