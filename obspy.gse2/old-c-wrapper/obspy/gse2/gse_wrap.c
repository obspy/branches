/*
#-------------------------------------------------------------------
# Filename: gse_wrap.c
#  Purpose: Python wrapper for gse_driver of Stefan Stange
#   Author: Moritz Beyreuther
#    Email: moritz.beyreuther@geophysik.uni-muenchen.de
#
# Copyright (C) 2008 Moritz Beyreuther, Stefan Stange
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#---------------------------------------------------------------------
*/

#include <Python.h>            // Python as seen from C
#include <numpy/arrayobject.h> // NumPy  as seen from C
#include <math.h>
#include <stdio.h>             // for debug output
#include "NumPy_macros.h"
#include "buf.h"
#include "gse_header.h"
#include "gse_types.h"

static PyObject *readgse(PyObject *self, PyObject *args)
{
	PyArrayObject *a;
	struct header head;
	const char *gsefile;
	long chksum=0, chksum2=0;
	int i, n, ierr;
	FILE *fp;
	char tline[82]="";
	long *data; 
	//long *ap;
	int a_dims[1];


	if (!PyArg_ParseTuple(args, "s", &gsefile)) return NULL;

	fp = fopen(gsefile,"r");
	read_header(fp,&head);                  // find and read the header line

	data = (long *) calloc (head.n_samps,sizeof(long));// allocate data vector
	// Allocate help array
	a_dims[0] = head.n_samps;
	a = (PyArrayObject *) PyArray_FromDims(1,a_dims, PyArray_LONG);
	if (a==NULL) {
		printf("creating %d array failed\n",a_dims[0]);
		return NULL;                           //PyArray_FromDims raises exception
	}

	n = decomp_6b (fp, head.n_samps, data);  // read and decode the data
	printf("actual number of data read: %d\n",n);
	rem_2nd_diff (data, n);                  // remove second differences
	chksum=0;
	if (fgets(tline,82,fp) == NULL)          // read next line (there might be
	{ printf ("GSE: No CHK2 found before EOF\n");// an additional
		return; }                              // blank line)
	if (strncmp(tline,"CHK2",4))             // and look for CHK2
	{ if (fgets(tline,82,fp) == NULL)        // read another line
	  { printf ("GSE: No CHK2 found before EOF\n");
	    return; } }
	if (strncmp(tline,"CHK2",4))
	{ printf ("GSE: No CHK2 found!\n");
	  return; }
	sscanf(tline,"%*s %ld",&chksum);         // extract checksum
	chksum2 = check_sum (data, n, chksum2);  // compute checksum from data
	printf("checksum read:     %ld\nchecksum computed: %ld\n",chksum,chksum2);
	fclose(fp);                 // close the input file
	//
	// not using IND1 here, IND1 is only defined for double
	// creating a help array of pointer which are assinged to the "real data"
	// in order to fill the structure. Note a->data is a method of a and has
	// nothing to do with the "real data"
	/*ap = (long *) a->data;
	for (i=0;i<n;i++) {
		ap[i] = data[i];
	}*/

	for (i=0;i<n;i++) {
		INDL1(a,i) = data[i];
	}

  free( (void*) data);    // clean up

	// NOTE: Using the "O" indicator in Py_BuildValue INCREF's the object
	// before returning it. But, since these objects already have an
	// INCREMENTED reference count you are incrementing the reference count
	// by two for these object. They will never go away and release their
	// memory. 
	// The character you want to use is "N" and it was introduced in Pythen 1.5.2
	// (don't forget the PyArray_Return()): 
	return Py_BuildValue("{s:i,s:i,s:i,s:i,s:i,s:d,s:s,s:s,s:s,s:s,s:i,s:d,s:d,s:d,s:s,s:d,s:d},N",
  "d_year",head.d_year,
	"d_mon",head.d_mon,
	"d_day",head.d_day,
	"t_hour",head.t_hour,
	"t_min",head.t_min,
	"t_sec",head.t_sec,
	"station",head.station,
	"channel",head.channel,
	"auxid",head.auxid,
	"datatype",head.datatype,
	"n_samps",head.n_samps,
	"samp_rate",head.samp_rate,
	"calib",head.calib,
	"calper",head.calper,
	"instype",head.instype,
	"hang",head.hang,
	"vang",head.vang,
	PyArray_Return(a));
}

static PyObject *writegse(PyObject *self, PyObject *args)
{
	PyArrayObject *a;
	struct header head;
	const char *gsefile;
	long chksum=0;
	int n, ierr;
	FILE *fp;
	long *tr;
	char *station;
	char *channel;
	char *auxid;
	char *datatype;
	char *instype;
    int nn; // add this to support null strings s# in PyArg_ParseTuple

	if (!PyArg_ParseTuple(args, "(iiiiifs#s#s#s#ifffs#ff)O!s", &head.d_year, &head.d_mon, &head.d_day, &head.t_hour, &head.t_min, &head.t_sec, &station, nn, &channel, nn, &auxid, nn,&datatype, nn, &head.n_samps, &head.samp_rate, &head.calib, &head.calper, &instype, nn, &head.hang, &head.vang, &PyArray_Type, &a, &gsefile)) return NULL;
	NDIM_CHECK(a,1);
	TYPE_CHECK(a,NPY_LONG);
	n = a->dimensions[0];
	tr = (long *) a->data;
	// memcpy((void *) tr, (void *) trace, n * sizeof(long))

	// pad whitespaces until specific length is reached
	// NOTE: strcpy adds carriage (length 1), therefore length must 
	// be one less
	while(strlen(station) < 5) strcat(station," ");
	strcpy(head.station,station); //copy strings onto special length chars
	while(strlen(channel) < 3) strcat(channel," ");
	strcpy(head.channel,channel);
	while(strlen(auxid) < 4) strcat(auxid," ");
	strcpy(head.auxid,auxid);
	while(strlen(datatype) < 3) strcat(datatype," ");
	strcpy(head.datatype,datatype);
	while(strlen(instype) < 6) strcat(instype," ");
	strcpy(head.instype,instype);
	
	buf_init();                 // initialize the character buffer
	fp = fopen(gsefile,"w");    // open the output file
	chksum=labs(check_sum (tr,n,chksum));// 1st, compute the checksum
	diff_2nd (tr,n,0);          // 2nd, compute the 2nd differences
	ierr=compress_6b (tr,n);    // 3rd, character-encode the data
	printf("error status after compression: %d\n",ierr);
	printf("actual number of data written: %d\n",n);
	printf ("chksum written:    %8ld\n",chksum);
	write_header(fp,&head);     // 4th, write the header to the output file
	buf_dump (fp);              // 5th, write the data to the output file
	fprintf (fp,"CHK2 %8ld\n\n",chksum);// 6th, write checksum and closing line
	fclose(fp);                 // close the output file
	buf_free();                 // clean up!
	return Py_BuildValue("i",0);// return 0
}

// doc strings:
static char read_doc[] = \
	"(header,data) = read(gsefile) \n\
	header       : tuple containing GSE2 header \n\
	data         : array containing the data, type: PyArray_LONG \n\
	gsefile      : name of GSE2 file to read \n";

static char write_doc[] = \
	"Write data to gsefile with given header \n\
	\n\
	write( (d_year, d_mon, d_day, t_hour, t_min, t_sec, station, channel, auxid, datatype, n_samps, samp_rate, calib, calper, instype, hang, vang), data, gsefile) \n\
	d_year       : int length 4 containing the year, e.g. 2007 \n\
	d_mon        : int length 2 containing the month, e.g. 5 \n\
	d_day        : int length 2 containing the day, e.g. 27 \n\
	t_hour       : int length 2 containing the hour, e.g. 23 \n\
	t_min        : int length 2 containing the min, e.g. 59 \n\
	t_sec        : float containing the sec, e.g. 24.1245 \n\
	station      : string max length 6 containing the station name, e.g. STAU \n\
	channel      : string max length 4 containing the channel, e.g. SHZ \n\
	auxid        : string max length 5 containing the auxid, e.g. VEL \n\
	datatype     : string max length 4 containing the type of data, e.g. CM6 \n\
	n_samps      : int containing the number of samples \n\
	samp_rate    : float containing the sampling rate, e.g. 200. \n\
	calib        : float containing the calibration factor,  e.g. 1./(2*pi) = 0.15915\n\
	calper       : float containing the calper, e.g. 1. \n\
	instype      : string max length 7 containing the type of instrument, e.g. LE-3D \n\
	hang         : float containing the hang factor, e.g. -1.0 \n\
	vang         : float containing the vang factor, e.g.  0. \n\
	data         : array containing the data, type: PyArray_LONG \n\
	gsefile      : name of GSE2 file to read \n";

/*static char module_doc[] = \
	"module ext_squareloop:\n\
	squareloop(a, alpha)";*/

// The method table must always be present - it lists the 
// functions that should be callable from Python: 
static PyMethodDef ext_gse_methods[] = {
	{"read",       // name of func when called from Python
	  readgse,     // corresponding C function
	  METH_VARARGS,// ordinary (not keyword) arguments
	  read_doc},   // doc string for gridloop1 function
	{"write",      // name of func when called from Python
	  writegse,    // corresponding C function
	  METH_VARARGS,// ordinary (not keyword) arguments
	  write_doc},  // doc string for gridloop1 function
	{NULL, NULL}   // required ending of the method table
};

// needs to be the module name!!! prefixed by init
void initext_gse() {
	// Assign the name of the module and the name of the
	// method table and (optionally) a module doc string:
	// name in quotes needs to be the module name */
	Py_InitModule("ext_gse", ext_gse_methods);

	import_array();   // required NumPy initialization
}
