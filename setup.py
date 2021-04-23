#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages



with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Krattle',
    version='0.0.1',
    url='https://github.com/michaelremington2/Krattle',
    author='Michael Remington and Jeet Sukumaran',
    author_email='micahelremington2@gmail.com',
    license="LICENSE.txt",
    classifiers=[
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    ],
    scripts=[
        "bin/run_krattle.py",
        ],
    test_suite = "tests",
    package_dir={"": "src"},
    description="Agent based simulation of predator prey dynamics.",
    long_description=long_description,
    packages= find_packages(where="src"),
    python_requires=">=3.6",   
)