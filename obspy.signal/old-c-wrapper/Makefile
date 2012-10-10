# Makefile for C extensions of obspy
#

INCLUDES= \
	-I /usr/lib/python2.4/site-packages/numpy/core/include\
	-I /usr/include/python2.4\
	-I .

# If you use a local python2.5 installation modify the following INCLUDES
#PREFIX25= /export/data/beyreuth/local/src/Python-2.5.2
#INCLUDES= \
#	-I $(PREFIX25)/lib/python2.5/site-packages/numpy/core/include\
#	-I $(PREFIX25)/include/python2.5\
#	-I. 

CFLAGS = -g -O3
CC = gcc
LD = ld

all: ext_recstalta.so recstalta.so

ext_recstalta.so: recstalta_wrap.c
	$(CC) $(CFLAGS) $(INCLUDES) -c recstalta_wrap.c
	$(CC) $(CFLAGS) -shared -lm -o ext_recstalta.so recstalta_wrap.o

clean:
	rm *.so *.o
