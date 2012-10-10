# Build environment can be configured the following
# environment variables:
#   CC : Specify the C compiler to use
#   CFLAGS : Specify compiler options to use

# Options specific for GCC
GCC = gcc
GCCFLAGS = -O2 -Wall -fPIC -I..

# Required compiler parameters
CFLAGS += -I..

LDFLAGS = -L..
LDLIBS = -lmseed
all: fullASCII_littleEndian smallASCII_littleEndian int32Steim1_littleEndian int32Steim2_littleEndian int32Int32_littleEndian int16Int16_littleEndian float32Float32_littleEndian float64Float64_littleEndian fullASCII_bigEndian smallASCII_bigEndian int32Steim1_bigEndian int32Steim2_bigEndian int32Int32_bigEndian int16Int16_bigEndian float32Float32_bigEndian float64Float64_bigEndian

int16Int16_littleEndian: writeINT16_INT16_littleEndian.o
	$(CC) $(CFLAGS) -o $@ writeINT16_INT16_littleEndian.o $(LDFLAGS) $(LDLIBS)

int32Int32_littleEndian: writeINT32_INT32_littleEndian.o
	$(CC) $(CFLAGS) -o $@ writeINT32_INT32_littleEndian.o $(LDFLAGS) $(LDLIBS)

int32Steim1_littleEndian: writeINT32_Steim1_littleEndian.o
	$(CC) $(CFLAGS) -o $@ writeINT32_Steim1_littleEndian.o $(LDFLAGS) $(LDLIBS)

int32Steim2_littleEndian: writeINT32_Steim2_littleEndian.o
	$(CC) $(CFLAGS) -o $@ writeINT32_Steim2_littleEndian.o $(LDFLAGS) $(LDLIBS)

float32Float32_littleEndian: writeFLOAT32_Float32_littleEndian.o
	$(CC) $(CFLAGS) -o $@ writeFLOAT32_Float32_littleEndian.o $(LDFLAGS) $(LDLIBS)

float64Float64_littleEndian: writeFLOAT64_Float64_littleEndian.o
	$(CC) $(CFLAGS) -o $@ writeFLOAT64_Float64_littleEndian.o $(LDFLAGS) $(LDLIBS)

fullASCII_littleEndian: writeFullASCII_littleEndian.o 
	$(CC) $(CFLAGS) -o $@ writeFullASCII_littleEndian.o $(LDFLAGS) $(LDLIBS)

smallASCII_littleEndian: writeSmallASCII_littleEndian.o 
	$(CC) $(CFLAGS) -o $@ writeSmallASCII_littleEndian.o $(LDFLAGS) $(LDLIBS)

int16Int16_bigEndian: writeINT16_INT16_bigEndian.o
	$(CC) $(CFLAGS) -o $@ writeINT16_INT16_bigEndian.o $(LDFLAGS) $(LDLIBS)

int32Int32_bigEndian: writeINT32_INT32_bigEndian.o
	$(CC) $(CFLAGS) -o $@ writeINT32_INT32_bigEndian.o $(LDFLAGS) $(LDLIBS)

int32Steim1_bigEndian: writeINT32_Steim1_bigEndian.o
	$(CC) $(CFLAGS) -o $@ writeINT32_Steim1_bigEndian.o $(LDFLAGS) $(LDLIBS)

int32Steim2_bigEndian: writeINT32_Steim2_bigEndian.o
	$(CC) $(CFLAGS) -o $@ writeINT32_Steim2_bigEndian.o $(LDFLAGS) $(LDLIBS)

float32Float32_bigEndian: writeFLOAT32_Float32_bigEndian.o
	$(CC) $(CFLAGS) -o $@ writeFLOAT32_Float32_bigEndian.o $(LDFLAGS) $(LDLIBS)

float64Float64_bigEndian: writeFLOAT64_Float64_bigEndian.o
	$(CC) $(CFLAGS) -o $@ writeFLOAT64_Float64_bigEndian.o $(LDFLAGS) $(LDLIBS)

fullASCII_bigEndian: writeFullASCII_bigEndian.o 
	$(CC) $(CFLAGS) -o $@ writeFullASCII_bigEndian.o $(LDFLAGS) $(LDLIBS)

smallASCII_bigEndian: writeSmallASCII_bigEndian.o 
	$(CC) $(CFLAGS) -o $@ writeSmallASCII_bigEndian.o $(LDFLAGS) $(LDLIBS)

clean:
	rm -f *.o fullASCII_bigEndian smallASCII_bigEndian int32Steim1_bigEndian int32Steim2_bigEndian int32Int32_bigEndian int16Int16_bigEndian float32Float32_bigEndian float64Float64_bigEndian fullASCII_littleEndian smallASCII_littleEndian int32Steim1_littleEndian int32Steim2_littleEndian int32Int32_littleEndian int16Int16_littleEndian float32Float32_littleEndian float64Float64_littleEndian
cc:
	@$(MAKE) "CC=$(CC)" "CFLAGS=$(CFLAGS)"

gcc:
	@$(MAKE) "CC=$(GCC)" "CFLAGS=$(GCCFLAGS)"

gcc32:
	@$(MAKE) "CC=$(GCC)" "CFLAGS=-m32 $(GCCFLAGS)"

gcc64:
	@$(MAKE) "CC=$(GCC)" "CFLAGS=-m64 $(GCCFLAGS)"

debug:
	$(MAKE) "CFLAGS=-g $(CFLAGS)"

gccdebug:
	$(MAKE) "CC=$(GCC)" "CFLAGS=-g $(GCCFLAGS)"

gcc32debug:
	$(MAKE) "CC=$(GCC)" "CFLAGS=-g -m32 $(GCCFLAGS)"

gcc64debug:
	$(MAKE) "CC=$(GCC)" "CFLAGS=-g -m64 $(GCCFLAGS)"

gcc32gprof:
	$(MAKE) "CC=$(GCC)" "CFLAGS=-pg -m32 $(GCCFLAGS)"

gcc64gprof:
	$(MAKE) "CC=$(GCC)" "CFLAGS=-pg -m64 $(GCCFLAGS)"

# Implicit rule for building object files
%.o: %.c
	$(CC) $(CFLAGS) -c $<

install:
	@echo
	@echo "No install target, copy the executable(s) yourself"
	@echo
