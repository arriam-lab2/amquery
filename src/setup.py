from setuptools import setup

setup(
    name='mgns',
    version='0.1',
    py_modules=['mgns'],
    install_requires=[
        'click',
        'numpy',
        'scipy',
        'click',
        'biopython',
        'joblib'
    ],
    entry_points='''
        [console_scripts]
        mgns=mgns:cli
    ''',
)
