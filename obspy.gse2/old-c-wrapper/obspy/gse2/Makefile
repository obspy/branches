# Makefile for gse2 functions and python wrapper
# Please adapt the includer for your requirement

INCLUDES= \
	-I /usr/lib/python2.4/site-packages/numpy/core/include\
	-I /usr/include/python2.4\
	-I .

CFLAGS = -g -O3
CC = gcc
LD = ld

gse_driver: gse_driver.c buf.c gse_functions.c
	$(CC) $(CLFAGS) -c gse_functions.c buf.c
	$(CC) $(CLFAGS) -o gse_driver gse_driver.c buf.o gse_functions.o

ext_gse.so: gse_wrap.c buf.c gse_functions.c
	$(CC) $(CFLAGS) $(INCLUDES) -c gse_wrap.c buf.c gse_functions.c
	$(CC) $(CFLAGS) -shared -lm -o ext_gse.so gse_wrap.o buf.o\
		gse_functions.o

clean:
	rm -f gse_driver *.so *.o *.pyc leak.gse test.gse
