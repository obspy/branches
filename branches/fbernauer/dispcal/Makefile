all: cython

cython:
	python setup.py build_ext --inplace

## Makefile for rekf2Loop.so
# 
#CC = gcc
#CFLAGS = -g3 -ggdb -O0 -fno-inline -Wall -Wextra
#
#rekf2Loop.o:
#    $(CC) -fPIC -c rekf2Loop.c
#
#rekf2Loop.so: 
#    $(CC) -shared $(CFLAGS) -lm -o rekf2Loop.so rekf2Loop.o
#
#clean: 
#    rm -f rekf2Loop.o rekf2Loop.so
