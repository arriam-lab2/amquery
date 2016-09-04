from setuptools import setup
from distutils.core import setup
from distutils.extension import Extension
import numpy

try:
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False
else:
    use_cython = True

cmdclass = {}
ext_modules = []

if use_cython:
    ext_modules += [
        Extension("mgns.rank", ["lib/kmerize/rank.pyx"]),
    ]
    cmdclass.update({'build_ext': build_ext})
else:
    ext_modules += [
        Extension("mgns.rank", ["lib/kmerize/rank.c"]),
    ]

setup(
    name='mgns',
    version='0.1',
    py_modules=['mgns'],
    install_requires=[
        'numpy>=1.11.0',
        'scipy>=0.17.0',
        'click>=6.6',
        'biopython>=1.66',
        'joblib>=0.9.4',
        'multiprocess>=0.70.4',
        'Comparable>=1.0',
        'bunch>=1.0.1',
        'genetic>=0.1.dev3',
        'tqdm>=4.7.0',
        'pandas>=0.18.0'
    ],
    include_dirs=[numpy.get_include()],
    entry_points='''
        [console_scripts]
        mgns=mgns:cli
    ''',
    cmdclass=cmdclass,
    ext_modules=ext_modules,
)
