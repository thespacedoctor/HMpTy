import sys
import os
import time
from sys import stdout, stderr
from glob import glob
import platform

from setuptools import setup, Extension

import distutils.sysconfig
import os


def readme():
    with open('README.rst') as f:
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
try:
    import numpy
    include_dirs = [numpy.get_include()]
    include_dirs += ['HMpTy/include']
    have_numpy = True
except:
    have_numpy = False
    ext_modules = []
    include_dirs = []

    stdout.write('Numpy not found:  Not building C extensions\n')
    time.sleep(5)

if platform.system() == 'Darwin':
    extra_compile_args = ['-arch', 'i386', '-arch', 'x86_64']
    extra_link_args = ['-arch', 'i386', '-arch', 'x86_64']
else:
    extra_compile_args = []
    extra_link_args = []


if have_numpy:
    # HTM
    include_dirs += ['HMpTy/htm', 'HMpTy/htm/htm_src']
    htm_sources = glob('HMpTy/htm/htm_src/*.cpp')
    htm_sources += ['HMpTy/htm/htmc.cc', 'HMpTy/htm/htmc_wrap.cc']
    htm_module = Extension('HMpTy.htm._htmc',
                           extra_compile_args=extra_compile_args,
                           extra_link_args=extra_link_args,
                           sources=htm_sources)

    ext_modules.append(htm_module)
    packages.append('HMpTy.htm')

# data_files copies the ups/HMpTy.table into prefix/ups
setup(name='HMpTy',
      version='0.1',
      description='',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities',
      ],
      keywords='utilities dryx',
      url='https://github.com/thespacedoctor/HMpTy',
      author='thespacedoctor',
      author_email='davidrobertyoung@gmail.com',
      license='MIT',
      packages=packages,
      include_package_data=True,
      install_requires=[
          'pyyaml',
          'numpy'
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      ext_modules=ext_modules,
      entry_points={
          'console_scripts': ['funniest-joke=funniest.cmd:main'],
      },
      zip_safe=False,
      include_dirs=include_dirs)
