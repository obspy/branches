from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

#setup(
#  cmdclass = {'build_ext': build_ext},
#  ext_modules = [Extension("rekf2", ["rekf2.pyx"])]
#)

setup(
  cmdclass = {'build_ext': build_ext},
  ext_modules = [Extension("politrend", ["politrend.pyx"])]
)

#setup(
#  cmdclass = {'build_ext': build_ext},
#  ext_modules = [Extension("ltisim", ["ltisim.pyx"])]
#)

#setup(
#  cmdclass = {'build_ext': build_ext},
#  ext_modules = [Extension("rekf1", ["rekf1.pyx"])]
#)

#setup(
#  cmdclass = {'build_ext': build_ext},
#  ext_modules = [Extension("quad", ["quad.pyx"])]
#)
