from setuptools import setup, find_packages
import textwrap

VERSION = "0.1.0.dev0"

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
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        'gui_scripts': [
            ('openfoam_liggghts_ui = '
             'simphony_ui.cli.openfoam_liggghts_ui:main')
        ]
    },
)
