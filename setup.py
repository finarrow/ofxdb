import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ofxdb",
    version="0.0.1",
    author="Ricardo Rosales",
    author_email="rrosales1028@gmail.com",
    description="DB Generator for OFX Financial Statement Data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/finarrow/ofxdb",
    packages=["ofxdb"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment"
    ],
    python_requires=">=3.7",
    install_requires=["ofxtools>=0.8.20", "pandas>=1.0.1"],
)
