from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
  cmdclass = {'build_ext': build_ext},
  ext_modules = [Extension("relcalstack", ["relcalstack.pyx"])]
)

setup(
  cmdclass = {'build_ext': build_ext},
  ext_modules = [Extension("calstackrel", ["calstackrel.pyx"])]
)

setup(
  cmdclass = {'build_ext': build_ext},
  ext_modules = [Extension("transfunc", ["transfunc.pyx"])]
)

setup(
  cmdclass = {'build_ext': build_ext},
  ext_modules = [Extension("konno_ohmachi_smoothing", ["konno_ohmachi_smoothing.pyx"])]
)
