"""
Setuptools integration script
"""

from setuptools import setup, find_packages
from distutils.core import Extension
import os


os.environ["CC"] = "g++"

setup(
    name='misal',
    version='0.3dev',
    packages=find_packages(),
    include_package_data=True,
    # dependency_links=[
    #     "git+git://github.com/nromashchenko/scikit-bio@fastunifrac#egg=scikit-bio-0.5.1.dev0"
    # ],
    # install_requires=[
    #     'lazy_import==0.2.2',
    #     'numpy==1.13.3',
    #     'scipy>=0.17.0',
    #     'scikit-bio==0.5.1.dev0',
    #     'click>=6.6',
    #     'biopython>=1.66',
    #     'joblib>=0.9.4',
    #     'multiprocess>=0.70.4',
    #     'Comparable>=1.0',
    #     'bunch>=1.0.1',
    #     'pandas==0.19.2',
    #     'scikit-learn>=0.17.1',
    #     'codeclimate-test-reporter>=0.1.2',
    #     'colorama==0.3.7',
    #     'biom-format==2.1.6',
    #     'h5py',
    #     'yack==0.1.2'
    # ],
    # entry_points='''
    #     [console_scripts]
    #     amq=amquery.cli:cli
    #     amquery=amquery.cli:cli
    #     split_fasta.py=scripts.split_fasta:cli
    #     merge_fasta.py=scripts.merge_fasta:cli
    # ''',
    # ext_modules=[Extension('amquery.core.distance.metrics.jsd',
    #                        sources=['amquery/core/distance/metrics/jsd.cpp'],
    #                        extra_compile_args=['-std=c++11'],
    #                        )
    #              ],
)
