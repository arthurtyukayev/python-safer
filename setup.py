from setuptools import setup

setup(
    name='python-safer',
    version='1.1',
    packages=['safer'],
    description="Web scraping API wrapping for the Department of Transportation's Safety and Fitness Electronic Records (SAFER) System",
    url='https://github.com/arthurtyukayev/python-safer',
    keywords='SAFER safer department transportation fitness electronic records system',
    author='Arthur Tyukayev',
    install_requires=['lxml', 'requests', 'python-dateutil'],
    license='MIT',
)
