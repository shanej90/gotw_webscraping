import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="gotw-webscraping-shanej90", 
    version="0.0.1",
    author="Shane Jackson",
    author_email="shane.jackson@gmx.co.uk",
    description="Scraping panel data from the Grants on the Web webpages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shanej90/gotw_webscraping",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows",
    ],
    python_requires='>=3.10',
)