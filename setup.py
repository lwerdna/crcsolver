# https://packaging.python.org/tutorials/packaging-projects/

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crcsolver",
    version="1.0.1",
    author="Andrew Lamoureux",
    author_email="foo@bar.com",
    description="solve for data, given a target crc",
    long_description=long_description, # load from README.md
    long_description_content_type="text/markdown",
    url="https://github.com/lwerdna/crcsolver",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Public Domain",
        "Operating System :: OS Independent",
    ],
)
