from setuptools import setup, find_packages

setup(

    name='refresher',
    version='1.0',
    author='Matheus Melo',
    install_requires=[
        "redis==4.4.4"
    ],
    packages=find_packages()
)
