SimPhoNy-UI
===========

You can use SimPhoNy-UI to run a calculation using OpenFOAM and Liggghts at the same time
and visualize the result with Mayavi.

Input parameters
----------------

Using the UI, you will be able to set the following parameters:

- General parameters
- LIGGGHTS specific parameters
- OpenFoam specific parameters

You must specify input files for OpenFOAM and Liggghts. You can find
examples of input files in the simphony_ui/tests/fixtures directory.

General parameters
------------------

The following parameters are available in the general configuration tab:

- Number of iterations: It is the total number of full steps the evaluation will perform.
- Update frequency: Allows to specify the number of iterations at which the data
  will be snapshot. For example, 10000 iterations with an update frequency of 1000 will
  produce image frames at iterations 1000, 2000, 3000 etc.
- Force type: the force type to use, common between liggghts and openfoam.

LIGGGHTS parameters
-------------------

This dialog contains parameters specific to LIGGGHTS. 
Their documentation can be found on the appropriate sources for LIGGGHTS.

OpenFoam parameters
-------------------

This dialog contains parameters specific to OpenFoam. 
Their documentation can be found on the appropriate sources for OpenFoam.

Run the calculation
-------------------

Once input parameters are correctly set, you'll be able to run the calculation with
the "Run" button at the bottom of the dialog. A progress bar dialog should appear.
It can take a few minutes for large number of iterations.

Visualize result
----------------

Once the calculation terminated, the result should automatically appears in the 3D
Mayavi scene. You could then see the Mayavi pipeline and change some parameters of
the visualization, and play the movie or change frames using the buttons on the
bottom part of the visualization.

The "Save..." button allows to save the rendered frames as png files. Once
pressed, a dialog will request a directory. Files in the format "frame-N.png"
with N the frame number will be created.

If you run the calculation again, Mayavi input datasets will be overwritten.
