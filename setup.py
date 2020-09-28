import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="VisualGraphTheory",
    version="0.8.0",
    author="Isaac Flores",
    author_email="floresisaac413@gmail.com",
    description="A Graphical Program used to show how basic Graph Theory Algorithms work using pyOpenGL.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iflor413/VisualGraphTheory",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License"],
    python_requires='>=3.6',
    license='MIT')
