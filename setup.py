#!/usr/bin/env python

import re
import pathlib
import setuptools

# extract the current version
init_file = pathlib.Path(__file__).parent.resolve().joinpath('pystrum/__init__.py')
init_text = open(init_file, 'rt').read()
pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = re.search(pattern, init_text, re.M)
if not match:
    raise RuntimeError(f'Unable to find __version__ in {init_file}')
version = match.group(1)

# run setup
setuptools.setup(
    name='pystrum',
    version=version,
    license='MIT',
    description='General Python Utility Library',
    url='https://github.com/adalca/pystrum',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'six',
        'numpy',
        'scipy',
        'matplotlib',
    ]
)
