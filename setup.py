
import os, sys
here = (os.path.abspath(os.path.dirname(__file__)))
src = os.path.join(here, "src/fuzzylogic")
sys.path.append(src)

from setuptools import find_packages
from setuptools import setup



meta={
    "name":"fuzzylogic",
    "description":"Fuzzy Logic for Python 3",
    "license":"MIT",
    "url":"https://github.com/amogorkon/fuzzylogic",
    "version":"0.1.2.post4",
    "author":"Anselm Kiefner",
    "author_email":"fuzzylogic-pypi@anselm.kiefner.de",
    "python_requires":">3.6",
    "keywords":["fuzzy logic",],
    "classifiers":[
        "Development Status :: 4 - Beta",
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
}



with open("README.md") as f:
    LONG_DESCRIPTION = f.read()
  
setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    zip_safe=False,
    **meta
)
