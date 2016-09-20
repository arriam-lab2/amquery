from setuptools import setup, find_packages
from distutils.core import Extension
import os


os.environ["CC"] = "g++"

setup(
    name='amq',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,
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
        'pandas>=0.18.0',
        'scikit-learn>=0.17.1',
        'codeclimate-test-reporter>=0.1.2'
    ],
    entry_points='''
        [console_scripts]
        amq=amquery.cli.amq:cli
        amquery=amquery.cli.amq:cli
    ''',
    ext_modules=[Extension('amquery.index.kmers_distr.rank',
                           sources=['amquery/index/kmers_distr/rank.cpp'],
                           extra_compile_args=['-std=c++11'],
                           ),
                 Extension('amquery.index.distance.jsd',
                           sources=['amquery/index/distance/jsd.cpp'],
                           extra_compile_args=['-std=c++11'],
                           )
                 ],
)
