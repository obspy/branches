#ifndef NUMPY_MACROS__H
#define NUMPY_MACROS__H

/* This file defines some macros for programming with
   NumPy arrays in C extension modules. */

/* define some macros for array dimension/type check
	 and subscripting */
#define QUOTE(s) # s   /* turn s into string "s" */
#define NDIM_CHECK(a, expected_ndim) \
	if (a->nd != expected_ndim) { \
		PyErr_Format(PyExc_ValueError, \
		"%s array is %d-dimensional, but expected to be %d-dimensional",\
		QUOTE(a), a->nd, expected_ndim); \
		return NULL; \
	}
#define DIM_CHECK(a, dim, expected_length) \
	if (dim > a->nd) { \
		PyErr_Format(PyExc_ValueError, \
		"%s array has no %d dimension (max dim. is %d)", \
		QUOTE(a),dim,a->nd); \
		return NULL; \
	} \
	if (a->dimensions[dim] != expected_length) { \
		PyErr_Format(PyExc_ValueError, \
		"%s array has wrong %d-dimension=%d (expected %d)", \
		 QUOTE(a),dim,a->dimensions[dim],expected_length); \
		return NULL; \
	}
#define TYPE_CHECK(a, tp) \
	if (a->descr->type_num != tp) { \
		PyErr_Format(PyExc_TypeError, \
		"%s array is of type (%d) and not of correct type (%d)\n\
		NPY_BOOL        0\n\
		NPY_BYTE        1\n\
		NPY_UBYTE       2\n\
		NPY_SHORT       3\n\
		NPY_USHORT      4\n\
		NPY_INT         5\n\
		NPY_UINT        6\n\
		NPY_LONG        7\n\
		NPY_ULONG       8\n\
		NPY_LONGLONG    9\n\
		NPY_ULONGLONG   10\n\
		NPY_FLOAT       11\n\
		NPY_DOUBLE      12\n\
		NPY_LONGDOUBLE  13\n\
		NPY_CFLOAT      14\n\
		NPY_CDOUBLE     15\n\
		NPY_CLONGDOUBLE 16\n\
		NPY_OBJECT      17\n\
		NPY_STRING      18\n\
		NPY_UNICODE     19\n\
		NPY_VOID        20\n\
		NPY_NTYPES      21\n\
		NPY_NOTYPE      22\n\
		NPY_CHAR        23\n\
		NPY_USERDEF     256", \
		QUOTE(a), a->descr->type_num, tp); \
		return NULL; \
	}
#define CALLABLE_CHECK(func) \
	if (!PyCallable_Check(func)) { \
		PyErr_Format(PyExc_TypeError, \
		"%s is not a callable function", QUOTE(func)); \
		return NULL; \
	}

#define IND1(a, i) *((double *)(a->data + i*a->strides[0]))
#define IND2(a, i, j) \
	*((double *)(a->data + i*a->strides[0] + j*a->strides[1]))
#define IND3(a, i, j, k) \
	*((double *)(a->data + i*a->strides[0] + j*a->strides[1] + k*a->strides[2]))

#define INDL1(a, i) *((long *)(a->data + i*a->strides[0]))
#endif
