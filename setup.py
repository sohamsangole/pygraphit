from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pygraphit",
    version="0.1.0",
    author="Soham Sangole",
    author_email="sasangole2019@gmail.com",
    description="Turn any Python repository into a queryable knowledge graph using static analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sohamsangole/pyGraph",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "pygraphit-index=pygraphit.cli.index:main",
            "pygraphit-query=pygraphit.cli.query:main",
            "pygraphit-visualize=pygraphit.cli.visualize:main",
        ],
    },
)
