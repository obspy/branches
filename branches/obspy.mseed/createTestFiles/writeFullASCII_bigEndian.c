#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <errno.h>

#include <libmseed.h>

static short int verbose   = 2;
static short int ppackets  = 0;
static short int tracepack = 1;
static int   reclen        = 0;
static int   packreclen    = -1;
static char *encodingstr   = 0;
static int   packencoding  = -1;
static int   byteorder     = 1;
static char *inputfile     = 0;
static FILE * outfile;

static int parameter_proc (int argcount, char **argvec);
static void record_handler (char *record, int reclen, void *ptr);
static void usage (void);
static void term_handler (int sig);

static void record_handler (char *record, int reclen, void *srcname) {
  fwrite(record, reclen, 1, outfile);
}

main() {
  outfile = fopen("fullASCII_bigEndian.mseed", "w");
  int psamples;
  int precords;
  MSTrace *mst;
  char srcname[50];
  psamples = 0;

  // Allocate char array. One more allocated char is necessary for
  // the zero terminating last char.
  char *mychar = (char *) malloc(96 * sizeof(char));
  // Copy contents to char. In this case copy all ASCII chars.
  strcpy(mychar, " !\"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~");

  mst = mst_init (NULL);

  /* Populate MSTrace values */
  strcpy (mst->network, "XX");
  strcpy (mst->station, "TEST");
  strcpy (mst->channel, "BHE");
  mst->starttime = ms_seedtimestr2hptime ("2004,350,00:00:00.000000");
  mst->samprate = 1.0;
  /* The datasamples pointer and numsamples counter will be adjusted by
     the packing routine, the datasamples array must be dynamic memory
     allocated by the malloc() family of routines. */
  mst->datasamples = mychar; /* pointer to 8-bit ascii data samples */  
  mst->numsamples = 95; 
  mst->samplecnt = 95;
  mst->sampletype = 'a';      /* declare type to be 8 bit ASCII */

  mst_srcname (mst, srcname, 0); 

  /* Pack 256 byte, big-endian records, write chars */
  precords = mst_pack (mst, &record_handler, srcname, 256, DE_ASCII,
                                     1, &psamples, 1, verbose, NULL);

  ms_log (0, "Packed %d samples into %d records\n", psamples, precords);
  fclose(outfile);
  mst_free (&mst);
}
