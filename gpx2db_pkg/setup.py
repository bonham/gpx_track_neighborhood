from setuptools import setup, find_packages

setup(
    name='gpackage',
    version='1.0',
    description='Lib for gisprojekt',
    author='El Fu',
    # author_email='foomail@foo.com',
    packages=find_packages(),
    # external packages as dependencies
    install_requires=['gpxpy==1.4.2', 'psycopg2>=2.8.6', 'mock'],
    python_requires='>=3.8'
)
