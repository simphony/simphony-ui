from setuptools import setup, find_packages
import textwrap

VERSION = "0.1.0"

# Read description
with open('README.rst', 'r') as readme:
    README_TEXT = readme.read()


def write_version_py(filename=None):
    if filename is None:
        filename = os.path.join(
            os.path.dirname(__file__), 'simphony_ui', 'version.py')
    ver = """\
version = '%s'
"""
    fh = open(filename, 'wb')
    try:
        fh.write(ver % VERSION)
    finally:
        fh.close()


write_version_py()

requirements = [
    "simliggghts>=0.1",
    "foam-wrappers>=0.2",
    "futures"
]

setup(
    name='simphony_ui',
    version=VERSION,
    author='SimPhoNy, EU FP7 Project (Nr. 604005) www.simphony-project.eu',
    description=textwrap.dedent('''
        Graphical User Interface for SimPhoNy jobs as specified
        by established use-cases.'''),
    long_description=README_TEXT,
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        'gui_scripts': [
            ('openfoam_liggghts_ui = '
             'simphony_ui.cli.openfoam_liggghts_ui:main')
        ]
    },
)
