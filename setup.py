from setuptools import setup

setup(
    name='python-safer',
    version='1.3',
    packages=['safer'],
    description="A web scraping API written in Python to fetch data from the Department of Transportation's Safety and "
                "Fitness Electronic Records System http://www.safersys.org/",
    url='https://github.com/arthurtyukayev/python-safer',
    keywords='SAFER safer department transportation fitness electronic records system',
    author='Arthur Tyukayev',
    install_requires=['lxml', 'requests', 'python-dateutil'],
    license='MIT',
)
