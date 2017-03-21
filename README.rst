Simphony-ui
===========

A GUI which allows one to run a computation using Liggghts and OpenFOAM and visualize the result with Mayavi

.. image:: https://travis-ci.org/simphony/simphony-ui.svg?branch=master
   :target: https://travis-ci.org/simphony/simphony-ui
   :alt: Build status

.. image:: http://codecov.io/github/simphony/simphony-ui/coverage.svg?branch=master
   :target: http://codecov.io/github/simphony/simphony-ui?branch=master
   :alt: Coverage status

Repository
----------

Simphony-ui is hosted on github: https://github.com/simphony/simphony-ui

Requirements
------------

- futures

Optional requirements
~~~~~~~~~~~~~~~~~~~~~

To support the documentation built you need the following packages:

- sphinx >= 1.3.1

Installation
------------

The package requires python 2.7.x, installation is based on setuptools::

    # build and install
    python setup.py install

or::

    # build for in-place development
    python setup.py develop

Testing
-------

To run the full test-suite run::

    python -m unittest discover

Directory structure
-------------------

The module is structured as following:

- simphony_ui -- core of the simphony_ui module

  - liggghts_model

    - liggghts_model -- the trait model defining the Liggghts input parameters
    - liggghts_wrapper_creation -- the routine which creates Liggghts wrapper

  - openfoam_model

    - openfoam_model -- the trait model defining the OpenFOAM input parameters
    - openfoam_boundary_conditions -- the trait model defining the OpenFOAM input boundary conditions
    - openfoam_wrapper_creation -- the routine which creates OpenFOAM wrapper

  - couple_openfoam_liggghts -- main routine which run the calculation

  - ui -- main trait model which contains the whole UI with the Mayavi view

- doc -- Documentation related files

  - source -- Sphinx rst source files
  - build -- Documentation build directory, if documentation has been generated
    using the ``make`` script in the ``doc`` directory.
