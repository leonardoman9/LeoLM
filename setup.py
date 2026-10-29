"""Packaging compatibility shim; installation is performed explicitly by the documented workflow."""

from setuptools import find_packages, setup

setup(name="leolm", version="0.1.0", package_dir={"": "src"}, packages=find_packages("src"))
