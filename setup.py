from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='aiohttp-parameter-parser',
    version='0.1.1',
    description='Declare and validate HTTP query and path parameters in aiohttp',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Ivan Vinogradov',
    author_email='isvinogradov@gmail.com',
    url="https://github.com/isvinogradov/aiohttp-parameter-parser",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=['pytz', 'aiohttp'],  # external packages as dependencies
    python_requires='>=3.6',
)
