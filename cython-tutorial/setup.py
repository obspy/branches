from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("integrate_cython1", ["integrate_cython1.pyx"]),
               Extension("integrate_cython2", ["integrate_cython2.pyx"]),
               Extension("integrate_cython3", ["integrate_cython3.pyx"]),
               Extension("integrate_cython3_alternative_syntax",
                         ["integrate_cython3_alternative_syntax.pyx"])]

setup(cmdclass={'build_ext': build_ext},
      ext_modules=ext_modules)
