from setuptools import setup, find_packages

setup(

    name='refresher',
    version='1.0',
    author='Matheus Melo',
    install_requires=[
        "redis==3.0.1"
    ],
    packages=find_packages()
)
