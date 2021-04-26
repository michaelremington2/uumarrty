#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages



with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='peon',
    version='0.0.2',
    url='https://github.com/michaelremington2/peon',
    author='Michael Remington and Jeet Sukumaran',
    author_email='michaelremington2@gmail.com',
    license="LICENSE.txt",
    classifiers=[
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    ],
    scripts=[
        "bin/run_peon.py",
        ],
    test_suite = "tests",
    package_dir={"": "src"},
    description="Agent based simulation of predator prey dynamics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    python_requires=">=3.6",   
)