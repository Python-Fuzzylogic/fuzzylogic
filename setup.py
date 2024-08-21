import os
import pathlib
import sys

from setuptools import find_packages, setup

from src.fuzzylogic import __version__

here = os.path.abspath(os.path.dirname(__file__))
src = os.path.join(here, "src/fuzzylogic")
sys.path.append(src)

__license__ = "MIT"
__author__ = "Anselm Kiefner"
__contact__ = "fuzzylogic@anselm.kiefner.de"

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "Intended Audience :: Manufacturing",
    "Intended Audience :: Science/Research",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Scientific/Engineering :: Information Analysis",
]

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    zip_safe=False,
    name="fuzzylogic",
    description="Fuzzy Logic for Python 3",
    license=__license__,
    url="https://github.com/amogorkon/fuzzylogic",
    version=".".join(str(c) for c in __version__),
    author=__author__,
    author_email=__contact__,
    python_requires=">=3.12",
    keywords="fuzzy logic",
    classifiers=classifiers,
    extras_require={
        "plotting": ["matplotlib"],
    },
)
