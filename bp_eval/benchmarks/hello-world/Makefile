PROJECT = hello-world
OBJECTS = hello-world.o

CC = ../../toolchain/alphaev67-unknown-linux-gnu/bin/alphaev67-unknown-linux-gnu-gcc
CFLAGS = -Wall -static
LDFLAGS =

all: $(PROJECT)

$(PROJECT): $(OBJECTS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f $(PROJECT) $(OBJECTS)

.PHONY: all clean
