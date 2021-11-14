#!/usr/bin/env python3

# standards
from pathlib import Path
import re
import setuptools


README_FILE = Path(__file__).parent / 'README.md'

LONG_DESCRIPTION = README_FILE.read_text('UTF-8')

LONG_DESCRIPTION = re.sub(
    r'(?<=\]\()(?!http)',
    'https://github.com/saintamh/poisk/tree/master/',
    LONG_DESCRIPTION,
)


setuptools.setup(
    name='poisk',
    version='1.0.1',
    description='Small utilities for searching data structures',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Hervé Saint-Amand',
    author_email='poisk@saintamh.org',
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
