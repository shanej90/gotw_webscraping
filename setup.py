import setuptools
from os import path

#set location for reading requirmenets txt
HERE = path.abspath(path.dirname(__file__))

# Parse requirements.txt file so to have one single source of truth
REQUIREMENTS_DATA = []
with open(path.join(HERE, "requirements.txt"), encoding="utf-8") as f:
    for l in f.readlines():
        if not l.startswith("#"):
            if ">=" in l:
                REQUIREMENTS_DATA.append([l.split(">=")[0]])
            elif "=" in l:
                REQUIREMENTS_DATA.append([l.split("=")[0]])

#configuratiuon
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="gotw-webscraping-shanej90", 
    version="0.0.4",
    author="Shane Jackson",
    author_email="shane.jackson@gmx.co.uk",
    description="Scraping panel data from the Grants on the Web webpages",
    install_requires = REQUIREMENTS_DATA,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shanej90/gotw_webscraping",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.10',
)