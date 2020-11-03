import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylighter",
    version="0.0.1",
    author="Etienne Turc",
    author_email="etienne.turc@paylead.fr",
    description="Annotation tool on Jupyter for NER tasks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PayLead/PyLighter",
    # packages=setuptools.find_packages(),
    packages=["pylighter"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
