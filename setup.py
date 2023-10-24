from pathlib import Path
from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="python-safer",
    version="1.5",
    packages=["safer"],
    description="A web scraping API written in Python to fetch data from the Department of Transportation's Safety and "
    "Fitness Electronic Records System http://www.safersys.org/",
    url="https://github.com/arthurtyukayev/python-safer",
    keywords="SAFER safer department transportation fitness electronic records system",
    author="Arthur Tyukayev",
    author_email="arthurtyukayev@gmail.com",
    install_requires=["lxml", "requests", "python-dateutil"],
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
