import sys
import os
import time
from sys import stdout, stderr
from glob import glob
import platform
from setuptools import setup, Extension, find_packages
import distutils.sysconfig

moduleDirectory = os.path.dirname(os.path.realpath(__file__))
exec(open(moduleDirectory + "/HMpTy/__version__.py").read())


def readme():
    with open(moduleDirectory + '/README.rst') as f:
        return f.read()

main_libdir = distutils.sysconfig.get_python_lib()
pylib_install_subdir = main_libdir.replace(
    distutils.sysconfig.PREFIX + os.sep, '')
pylib_install_subdir = pylib_install_subdir.replace(
    'dist-packages', 'site-packages')

if not os.path.exists('ups'):
    os.mkdir('ups')
tablefile = open('ups/HMpTy.table', 'w')
tab = """
# The default version of this file will be overwritten on setup to include
# paths determined from the python version.  This is useful to have in place
# though so that dependencies can be checked *before* installation.  Currently
# there are no required dependencies, so this is somewhat moot.

setupOptional("python")
setupOptional("cjson")
envPrepend(PYTHONPATH,${PRODUCT_DIR}/%s)
""" % pylib_install_subdir
tablefile.write(tab)
tablefile.close()


# can we build recfile?
packages = ['HMpTy']
ext_modules = []

if platform.system() == 'Darwin':
    extra_compile_args = ['-arch', 'i386', '-arch', 'x86_64']
    extra_link_args = ['-arch', 'i386', '-arch', 'x86_64']
else:
    extra_compile_args = []
    extra_link_args = []

# HTM
try:
    import numpy
except:
    import pip
    pip.main(['install', 'numpy'])

import numpy
include_dirs = [numpy.get_include(), 'HMpTy/include',
                'HMpTy/htm', 'HMpTy/htm/htm_src']
htm_sources = glob('HMpTy/htm/htm_src/*.cpp')
htm_sources += ['HMpTy/htm/htmc.cc', 'HMpTy/htm/htmc_wrap.cc']
htm_module = Extension('HMpTy.htm._htmc',
                       extra_compile_args=extra_compile_args,
                       extra_link_args=extra_link_args,
                       sources=htm_sources)

ext_modules.append(htm_module)
packages.append('HMpTy.htm')

setup(name="HMpTy",
      version=__version__,
      description="Tools for working with Hierarchical Triangular Meshes (HTMs). Generate HTM-ids, crossmatch sets of sky-coordinates and more",
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities',
      ],
      keywords=['astronomy, coordinates, tools'],
      url='https://github.com/thespacedoctor/HMpTy',
      download_url='https://github.com/thespacedoctor/HMpTy/archive/v%(__version__)s.zip' % locals(
      ),
      author='David Young',
      author_email='davidrobertyoung@gmail.com',
      license='MIT',
      packages=find_packages(),
      # include_package_data=True,
      install_requires=[
          'numpy',
          'pyyaml',
          'HMpTy',
          'fundamentals',
          'docopt',
          'astrocalc'
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      ext_modules=ext_modules,
      entry_points={
          'console_scripts': ['hmpty=HMpTy.cl_utils:main'],
      },
      zip_safe=False,
      include_dirs=include_dirs)
