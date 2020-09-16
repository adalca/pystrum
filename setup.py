import setuptools

setuptools.setup(
    name='pystrum',
    version='0.2',
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
