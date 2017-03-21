SimPhoNy-UI
===========

You can use SimPhoNy-UI to run a calculation using OpenFOAM and Liggghts at the same time
and visualize the result with Mayavi.

Input parameters
----------------

Using the UI, you will be able to set the parameters of the computation (number of
iterations, time step, boundary conditions...).

You must specify input files for OpenFOAM and Liggghts. You can find
examples of input files in the simphony_ui/tests/fixtures directory.

Run the calculation
-------------------

Once input parameters correctly set, you'll be able to run the calculation with
the "Run" button at the bottom of the dialog. A progress bar dialog should appears.
It can take a few minutes for large number of iterations.

Visualize result
----------------

Once the calculation terminated, the result should automatically appears in the 3D
Mayavi scene. You could then see the Mayavi pipeline and change some parameters of
the visualization.
If you run the calculation again, Mayavi input datasets will be overwritten.