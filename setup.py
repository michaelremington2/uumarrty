#! /usr/bin/env python
from setuptools import setup, find_packages

with open("README.txt", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='Krattle',
    version='0.1',
    package_dir={"src": "krattle",
                "": "bin"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    license='bsd',
    classifiers=[
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    ],
    scripts=[
        "src/krattle/sim.py",
        "src/krattle/organismsim.py",
        "bin/run_krattle.py",
        ],
    url='https://github.com/michaelremington2/Krattle',
    author='Michael Remington and Jeet Sukumaran',
    author_email='micahelremington2@gmail.com and jsukumaran@sdsu.edu',
    long_description=long_description,
)