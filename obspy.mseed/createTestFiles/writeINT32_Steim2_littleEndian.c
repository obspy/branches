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
static int   byteorder     = 0;
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
  outfile = fopen("int32_Steim2_littleEndian.mseed", "w");
  int psamples;
  int precords;
  MSTrace *mst;
  char srcname[50];
  psamples = 0;

  int *mychar;
  mychar = (int *) malloc(50 * sizeof(int));
  // Write integers from 1 to 50.
  int i = 1;
  for(i; i<51; i++){
    mychar[i-1] = i;
	  }

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
  mst->datasamples = mychar;
  mst->numsamples = 50; 
  mst->samplecnt = 50;
  mst->sampletype = 'i';

  mst_srcname (mst, srcname, 0); 

  /* Pack 512 byte, big-endian records, ´write Chars */
  precords = mst_pack (mst, &record_handler, srcname, 256, DE_STEIM2,
                                     0, &psamples, 1, verbose, NULL);

  ms_log (0, "Packed %d samples into %d records\n", psamples, precords);
  fclose(outfile);
  mst_free (&mst);
}