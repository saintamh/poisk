#!/usr/bin/env python3

# standards
import setuptools

setuptools.setup(
    name='poisk',
    description='Small utilities for searching data structures',
    version='1.0.0',
    author='Hervé Saint-Amand',
    package_data={'poisk': ['py.typed']},
    packages=setuptools.find_packages(),
    install_requires=[
        'cssselect>=1.1,<2',
        'typing-extensions>=3.7,<4',
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=False,  # https://mypy.readthedocs.io/en/latest/installed_packages.html#creating-pep-561-compatible-packages
)
