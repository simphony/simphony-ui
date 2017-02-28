from setuptools import setup, find_packages

VERSION = "0.1.0"

requirements = [
    "simliggghts>=0.1",
    "foam-wrappers>=0.2",
]

setup(
    name='simphony_ui',
    version=VERSION,
    author='SimPhoNy, EU FP7 Project (Nr. 604005) www.simphony-project.eu',
    description='Graphical User Interface for SimPhoNy jobs as specified by established use-cases.',
    install_requires=requirements,
    packages=find_packages(),
)