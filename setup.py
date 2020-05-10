"""Sets up the temphumi sensor collection and presentation package."""

import io

from setuptools import find_packages
from setuptools import setup

with io.open("README.md", "rt", encoding="utf-8") as f:
    readme = f.read()  # pylint: disable=C0103

setup(
    name="temphumi",
    version="1.0.0",
    license="GPL",
    author="Paweł Sałek",
    author_email="pawsa0@gmail.com",
    description="Temperature recorder and server",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    install_requires=["flask"]
)
