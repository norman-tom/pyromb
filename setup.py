from setuptools import setup, find_packages
import os

# Read the long description from README.md
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyromb",
    version="0.2.1",
    packages=find_packages(
        where="src", exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    package_dir={"": "src"},
    author="Tom Norman",
    author_email="tom@normcosystems.com",
    description="Runoff Model Builder (Pyromb) is a package used for building RORB and WBNM control files from catchment diagrams built from ESRI shapefiles. Its primary use is in the QGIS plugin Runoff Model: RORB and Runoff Model: WBNM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/norman-tom/pyromb",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    include_package_data=True,  # Ensures inclusion of files specified in MANIFEST.in
)
