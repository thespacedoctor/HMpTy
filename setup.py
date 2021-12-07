from __future__ import print_function
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
    with open(moduleDirectory + '/README.md') as f:
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
    from distutils.sysconfig import get_config_var
    from distutils.version import LooseVersion
    extra_compile_args = ['-arch', 'i386',
                          '-arch', 'x86_64', '-stdlib=libc++']
    extra_link_args = ['-arch', 'i386', '-arch', 'x86_64']
    current_system = LooseVersion(platform.mac_ver()[0])

    if current_system <= '10.12':
        extra_compile_args = ['-arch', 'i386',
                              '-arch', 'x86_64', '-stdlib=libc++']
        extra_link_args = ['-arch', 'i386', '-arch', 'x86_64']
    else:
        extra_compile_args = ['-arch', 'x86_64', '-stdlib=libc++']
        extra_link_args = ['-arch', 'x86_64']

    if 'MACOSX_DEPLOYMENT_TARGET' not in os.environ:
        current_system = LooseVersion(platform.mac_ver()[0])
        python_target = LooseVersion(
            get_config_var('MACOSX_DEPLOYMENT_TARGET'))
        if python_target < '10.9' and current_system >= '10.9':
            os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.9'
else:
    extra_compile_args = []
    extra_link_args = []


# HTM
try:
    import numpy
except:
    try:
        import pip
        if int(pip.__version__.split('.')[0]) > 9:
            from pip._internal import main
        else:
            from pip import main
        main(['install', 'numpy'])
    except:
        print("Please install numpy & pandas before installing HMpTy (conda install numpy pandas)")
        sys.exit(0)

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

install_requires = [
    'pyyaml',
    'HMpTy',
    'fundamentals',
    'docopt',
    'astrocalc',
    'multiprocess',
    'unicodecsv',
    'pandas',
    'pymysql'
]

# READ THE DOCS SERVERS
exists = os.path.exists("/home/docs/")
if exists:
    c_exclude_list = ['healpy', 'astropy',
                      'numpy', 'sherlock', 'wcsaxes', 'HMpTy', 'ligo-gracedb']
    for e in c_exclude_list:
        try:
            install_requires.remove(e)
        except:
            pass

setup(name="HMpTy",
      version=__version__,
      description="Generate Hierarchical Triangular Mesh (HTM) IDs, crossmatch sets of sky-coordinates and more",
      long_description=readme(),
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
          'Topic :: Utilities',
      ],
      keywords=['astronomy, crossmatch, htm'],
      url='https://github.com/thespacedoctor/HMpTy',
      download_url='https://github.com/thespacedoctor/HMpTy/archive/v%(__version__)s.zip' % locals(
      ),
      author='David Young',
      author_email='davidrobertyoung@gmail.com',
      license='GNU',
      packages=find_packages(),
      ext_modules=ext_modules,
      include_package_data=True,
      install_requires=install_requires,
      test_suite='nose2.collector.collector',
      tests_require=['nose2', 'cov-core'],
      entry_points={
          'console_scripts': ['hmpty=HMpTy.cl_utils:main'],
      },
      include_dirs=include_dirs,
      zip_safe=False)
