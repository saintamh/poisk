#!/usr/bin/env python3

# standards
import setuptools

setuptools.setup(
    name='forban',
    version='1.0',
    author='Hervé Saint-Amand',
    packages=setuptools.find_packages(),
    install_requires=[
        'cssselect>=1.1,<2',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
)
