from setuptools import setup
from distutils.core import Extension
import os


os.environ["CC"] = "g++"

setup(
    name='amq',
    version='0.2',
    py_modules=['src/amq'],
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
    entry_points='''
        [console_scripts]
        amq=src.amq:cli
    ''',
    ext_modules=[Extension('src.lib.kmerize.rank',
                           sources=['src/lib/kmerize/rank.cpp'],
                           extra_compile_args=['-std=c++11'],
                           ),
                 Extension('src.lib.jsd',
                           sources=['src/lib/jsd.cpp'],
                           extra_compile_args=['-std=c++11'],
                           )
                 ],
)
