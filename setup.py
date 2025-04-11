from setuptools import setup, find_packages

setup(
    name="pseint_compiler",
    version="0.1",
    packages=find_packages(),
    package_dir={'': '.'},
    install_requires=[
        'ply>=3.11',
        'colorama>=0.4.6'
    ],
    python_requires='>=3.8',
)