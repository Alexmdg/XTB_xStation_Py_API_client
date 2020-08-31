import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyXTB_amdg", # Replace with your own username
    version="0.0.2",
    author="AlexMDG",
    author_email="alexmdg@protonmail.com",
    description="python wrapper for xStation json API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Alexmdg/XTB_xStation_Py_API_client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)