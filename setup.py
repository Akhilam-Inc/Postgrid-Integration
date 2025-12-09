from setuptools import find_packages, setup

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in postgrid_integration/__init__.py
from postgrid_integration import __version__ as version

setup(
    name="postgrid_integration",
    version=version,
    description="Postgrid Integration With ERPNext",
    author="Akhilam Inc.",
    author_email="raaj@akhilaminc.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
