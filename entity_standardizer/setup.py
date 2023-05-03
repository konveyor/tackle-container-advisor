# import setuptools
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="entity-standardizer-tca",
    version="1.0",
    author="TCA team",
    author_email="choudhury@us.ibm.com",
    description="Various entity standardizer models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/konveyor/tackle-container-advisor/entity_standardizer",
    project_urls={
        "Bug Tracker": "https://github.com/konveyor/tackle-container-advisor/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # package_dir={"tfidf": "tfidf", "wdapi": "wdapi", "gnn": "gnn"},
    # packages=find_packages(where="src"),
    packages=["entity_standardizer", "entity_standardizer.tfidf", "entity_standardizer.wdapi", "entity_standardizer.siamese"],
    python_requires=">=3.6",
)
