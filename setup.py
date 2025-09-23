from __future__ import print_function
import sys
import os
from glob import glob
import platform
from setuptools import setup, Extension, find_packages
from packaging import version
import site
import sysconfig

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
        import numpy
    except:
        print("Please install numpy & pandas before installing HMpTy (conda install numpy pandas)")
        sys.exit(0)

moduleDirectory = os.path.dirname(os.path.realpath(__file__))
exec(open(moduleDirectory + "/HMpTy/__version__.py").read())


def readme():
    with open(moduleDirectory + '/README.md') as f:
        return f.read()


# Get all site-packages directories
site_packages = site.getsitepackages()

# can we build recfile?
packages = ['HMpTy']
ext_modules = []

if platform.system() == 'Darwin':
    from sysconfig import get_config_var
    extra_compile_args = ['-arch', 'i386',
                          '-arch', 'x86_64', '-stdlib=libc++']
    extra_link_args = ['-arch', 'i386', '-arch', 'x86_64']
    current_system = version.parse(platform.mac_ver()[0])

    if current_system <= version.parse('10.12'):
        extra_compile_args = ['-arch', 'i386',
                              '-arch', 'x86_64', '-stdlib=libc++', "-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION"]
        extra_link_args = ['-arch', 'i386', '-arch', 'x86_64']
    else:
        extra_compile_args = ['-arch', 'x86_64', '-arch', 'arm64',
                              '-stdlib=libc++', "-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION"]
        extra_link_args = ['-arch', 'x86_64', '-arch', 'arm64']

    if 'MACOSX_DEPLOYMENT_TARGET' not in os.environ:
        current_system = version.parse(platform.mac_ver()[0])
        python_target = version.parse(
            get_config_var('MACOSX_DEPLOYMENT_TARGET'))
        if python_target < version.parse('10.9') and current_system >= version.parse('10.9'):
            os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.9'
else:
    extra_compile_args = ['-std=c++14',
                          "-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION"]
    extra_link_args = []

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
    'pymysql',
    'scipy'
]


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
      packages=find_packages(exclude=["*tests*"]),
      include_package_data=True,
      ext_modules=ext_modules,
      install_requires=install_requires,
      test_suite='nose2.collector.collector',
      tests_require=['nose2', 'cov-core'],
      entry_points={
          'console_scripts': ['hmpty=HMpTy.cl_utils:main'],
      },
      include_dirs=include_dirs,
      zip_safe=False)
