#include <Python.h>            // Python as seen from C
#include <numpy/arrayobject.h> // NumPy  as seen from C
#include <math.h>
#include "NumPy_macros.h"


static PyObject *rec_stalta(PyObject *self, PyObject *args) {
	PyArrayObject *a, *b;
	int ndat, Nsta, Nlta, i;
	double Csta, Clta, sta, lta;
	int b_dims[1];

	// arguments: a,Nsta,Nlta; parsing with checking the pointer types:
	if (!PyArg_ParseTuple(args, "O!ii", &PyArray_Type, &a, &Nsta, &Nlta))
		return NULL;
	NDIM_CHECK(a,1);
	TYPE_CHECK(a,NPY_DOUBLE);
	ndat = a->dimensions[0];
	DIM_CHECK(a,0,ndat);     // check if size of the traces is consistent

	// create output array
	b_dims[0] = ndat;
	b = (PyArrayObject *) PyArray_FromDims(1,b_dims, PyArray_DOUBLE);
	if (b==NULL) {
		printf("creating %d array failed\n",b_dims[0]);
		return NULL; //PyArray_FromDims raises exception
	}

	Csta = 1./Nsta; Clta = 1./Nlta;
	sta = 0; lta =0;
	for (i=1;i<ndat;i++) {
		sta = Csta * pow(IND1(a,i),2) + (1-Csta)*sta;
		lta = Clta * pow(IND1(a,i),2) + (1-Clta)*lta;
		IND1(b,i) = sta/lta;
	}

	if (Nlta < ndat) for (i=1;i<Nlta;i++) IND1(b,i) = 0;

	return PyArray_Return(b); //return array
}


// doc strings:
static char rec_stalta_doc[] = \
	"Recursive STA/LTA (see Withers et al. 1998 p. 98)\n\n\
	 charfunct = rec_stalta(a,sta_winlen,lta_winlen)\n\
	 charfunct    : characteristic function of recursive sta lta trigger\n\
	 sta_winlen   : window length of sta \n\
	 lta_winlen   : window length of lta \n";

// The method table must always be present - it lists the 
// functions that should be callable from Python: 
static PyMethodDef ext_recstalta_methods[] = {
	{"rec_stalta",     // name of func when called from Python
		rec_stalta,      // corresponding C function
		METH_VARARGS,    // ordinary (not keyword) arguments
		rec_stalta_doc}, // doc string for gridloop1 function
	{NULL, NULL}       // required ending of the method table
};

// need to be the module name, prefixed by init!!
void initext_recstalta() {
	// Assign the name of the module and the name of the
	// method table and (optionally) a module doc string:
	// name in quotes needs to be the module name
	Py_InitModule("ext_recstalta", ext_recstalta_methods);

	import_array(); // required NumPy initialization
}
