"""Example to solve 2D poiseuille flow

"""

# Imports general
import os
import sys
import time
import math
import numpy as np
from . import OpenFoam_input
import tempfile

# Imports simphony general
from simphony.core.cuba import CUBA

# Imports simphony-openfoam
from simphony.engine import openfoam_file_io
from simphony.engine import openfoam_internal

# Imports simphony-liggghts
from simphony.engine import liggghts
from simliggghts import CUBAExtension


runstart = time.time()

mode_OF = "internal"
mesh_type = "block"


# Defining the wrapper for OpenFoam
if mode_OF == "internal":
    wrapper_OF = openfoam_internal.Wrapper()
    CUBAExt_OF = openfoam_internal.CUBAExt
elif mode_OF == "io":
    wrapper_OF = openfoam_file_io.Wrapper()
    CUBAExt_OF = openfoam_file_io.CUBAExt
else:
    print "Wrong mode_OF!"
    sys.exit(1)


# define the wrapper for LIGGGHTS
dem_wrapper = liggghts.LiggghtsWrapper(use_internal_interface=True)

if mode_OF == "internal":
    path = os.path.abspath(os.curdir)
    print path

# General settings
number_iterations = 10

force_type = "Stokes"


# OF settings
mesh_name = 'test_mesh'
mesh_path = '.'
num_timesteps_OF = 10
timestep_OF = 2.0e-4
visco_OF = 1.0e-3
dens_liquid = 1000.0
delta_p = 0.008

# size of channel in OF
chansize = [1.0e-1, 1.0e-2, 2.0e-3]

# number of elements in all channel-directions
numgrid = [400, 40, 1]

# number of bins for velo profile generation
Nbins_OF = 30


# **** Liggghts settings *****************

# The number of DEM steps in each cycle, this is the number of
# steps that are run at each call of wrapper.run().
num_timesteps_DEM = 10

# Time step for MD simulation
timestep_DEM = 1e-6

# number of bins for velo profile generation
Nbins_lmp = Nbins_OF

restart_file = os.path.abspath(os.path.join("simphony_ui", "DEM_input.dat"))


if mode_OF != "none":

    # **********  Settings for OpenFoam wrapper  **********

    wrapper_OF.CM[CUBA.NAME] = mesh_name

    wrapper_OF.CM_extensions[CUBAExt_OF.GE] = (CUBAExt_OF.INCOMPRESSIBLE,
                                               CUBAExt_OF.LAMINAR_MODEL)
    # defines solver = simpleFoam
    # other options CUBAExt_OF.VOF -> interFoam
    #               CUBAExt_OF.NUMBER_OF_CORES = N -> parallel

    wrapper_OF.SP[CUBA.TIME_STEP] = timestep_OF
    wrapper_OF.SP[CUBA.NUMBER_OF_TIME_STEPS] = num_timesteps_OF
    wrapper_OF.SP[CUBA.DENSITY] = dens_liquid
    wrapper_OF.SP[CUBA.DYNAMIC_VISCOSITY] = visco_OF

    # setting BCs
    wrapper_OF.BC[CUBA.VELOCITY] = {'inlet': 'zeroGradient',
                                    'outlet': 'zeroGradient',
                                    'walls': ('fixedValue', (0, 0, 0)),
                                    'frontAndBack': 'empty'}
    wrapper_OF.BC[CUBA.PRESSURE] = {'inlet': ('fixedValue', delta_p),
                                    'outlet': ('fixedValue', 0.0),
                                    'walls': 'zeroGradient',
                                    'frontAndBack': 'empty'}

    run_readOF_start = time.time()

    print "Reading mesh and conversion to CUDS file"

    if mesh_type == "block":
        if mode_OF == "internal":
            openfoam_file_io. \
                create_block_mesh(path, mesh_name, wrapper_OF,
                                  OpenFoam_input.blockMeshDict)
        else:
            openfoam_file_io. \
                create_block_mesh(".", mesh_name, wrapper_OF,
                                  OpenFoam_input.blockMeshDict)
    else:
        corner_points = [(0.0, 0.0, 0.0),
                         (chansize[0], 0.0, 0.0),
                         (chansize[0], chansize[1], 0.0),
                         (0.0, chansize[1], 0.0),
                         (0.0, 0.0, chansize[2]),
                         (chansize[0], 0.0, chansize[2]),
                         (chansize[0], chansize[1], chansize[2]),
                         (0.0, chansize[1], chansize[2])]

        openfoam_file_io.create_quad_mesh(tempfile.mkdtemp(), mesh_name,
                                          wrapper_OF, corner_points,
                                          numgrid[0], numgrid[1],
                                          numgrid[2])

    mesh_wOF = wrapper_OF.get_dataset(mesh_name)

    print "Working directory", mesh_wOF.path

    print ("Number of points in mesh: {}".
           format(sum(1 for _ in mesh_wOF.iter_points())))

    run_readOF_end = time.time()

    time_read_OF = run_readOF_end - run_readOF_start


# ********* Settings for liggghts wrapper **********

# Reading existing particle file

run_readLM_start = time.time()

print "\nReading particle file"
particles_list = liggghts.read_data_file(restart_file)

pc_flow = particles_list[0]
pc_wall = particles_list[1]

pc_flow.name = "flow_chain"
pc_wall.name = "wall"

num_particles = sum(1 for _ in pc_flow.iter_particles())
num_particles_wall = sum(1 for _ in pc_wall.iter_particles())

print ("Number of atoms in group {}: {}".format(pc_flow.name, num_particles))
print ("Number of atoms in group {}: {}".format(
    pc_wall.name,
    num_particles_wall))

# shift boxorigin to 0,0,0 and update particles accordingly
boxorigin = pc_flow.data_extension[CUBAExtension.BOX_ORIGIN]

for par in pc_flow.iter_particles():
    par.coordinates = (par.coordinates[0] - boxorigin[0],
                       par.coordinates[1] - boxorigin[1],
                       par.coordinates[2] - boxorigin[2])
    pc_flow.update_particles([par])

pc_flow.data_extension[CUBAExtension.BOX_ORIGIN] = (0.0, 0.0, 0.0)


print "\nReading input files: done"

run_readLM_end = time.time()

time_read_LM = run_readLM_end - run_readLM_start


# Add particle (containers) to wrapper
dem_wrapper.add_dataset(pc_flow)
dem_wrapper.add_dataset(pc_wall)
pc_wflow = dem_wrapper.get_dataset(pc_flow.name)


# define the CM component of the SimPhoNy application model:
dem_wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = num_timesteps_DEM
dem_wrapper.CM[CUBA.TIME_STEP] = timestep_DEM

# Define the BC component of the SimPhoNy application model:
dem_wrapper.BC_extension[liggghts.CUBAExtension.BOX_FACES] = [
    "periodic",
    "fixed",
    "periodic"
]

# Information about fixed walls: 0: No fixation, 1: Particles are fixed
dem_wrapper.BC_extension[liggghts.CUBAExtension.FIXED_GROUP] = [0, 1]

# MATERIAL PARAMETERS INPUT
dem_wrapper.SP[CUBA.YOUNG_MODULUS] = [2.e4, 2.e4]
dem_wrapper.SP[CUBA.POISSON_RATIO] = [0.45, 0.45]
dem_wrapper.SP[CUBA.RESTITUTION_COEFFICIENT] = [0.95, 0.95, 0.95, 0.95]
dem_wrapper.SP[CUBA.FRICTION_COEFFICIENT] = [0.0, 0.0, 0.0, 0.0]
dem_wrapper.SP[CUBA.COHESION_ENERGY_DENSITY] = [0.0, 0.0, 0.0, 0.0]

dem_wrapper.SP_extension[liggghts.CUBAExtension.PAIR_POTENTIALS] = \
                                                ['repulsion', 'cohesion']


time_OF = 0.0
time_LGT = 0.0
time_drag = 0.0

if mode_OF is not "none":
    # Generate cell list
    cellmat = {}
    index = {}
    gridsize = [chansize[0]/numgrid[0],
                chansize[1]/numgrid[1],
                chansize[2]/numgrid[2]]

    for cell in mesh_wOF.iter_cells():
        LLN = [chansize[0]*2, chansize[1]*2, chansize[2]*2]
        for k in range(0, 8):
            for i in range(0, 3):
                if mesh_wOF.get_point(cell.points[k]).coordinates[i] < LLN[i]:
                    LLN[i] = mesh_wOF.get_point(cell.points[k]).coordinates[i]

        for i in range(0, 3):
            index[i] = round(LLN[i]/gridsize[i])

        cellmat[index[0], index[1], index[2]] = cell.uid


# ****************** MAIN LOOP *******************************


# Repeating OF calculation several times with modified pressure drop last
# result from previous iteration as input for new iteration
for numrun in range(0, number_iterations):

    print ("\n Performing iteration {} of {}".
           format(numrun, number_iterations-1))

    if mode_OF != "none":

        # Open Foam calculation

        run_OF_start = time.time()

        # running OpenFoam
        print ("RUNNING OPENFOAM for {} timesteps".format(num_timesteps_OF))
        wrapper_OF.run()

        run_OF_end = time.time()
        time_OF = time_OF + run_OF_end - run_OF_start

    run_drag_start = time.time()

    m = 0
    force = np.zeros(num_particles)

    # Compute relative velocity & drag force
    for par in pc_wflow.iter_particles():

        testpoint = par.coordinates

        if mode_OF is not "none":

            index = {}
            for i in range(0, 3):

                index[i] = int(math.floor(testpoint[i] /
                                          (chansize[i]/float(numgrid[i]))))

                if index[i] == numgrid[i]:
                    index[i] = 0
                elif index[i] == -1:
                    index[i] = numgrid[i]-1

            cell_id = cellmat[index[0], index[1], index[2]]
            cell = mesh_wOF.get_cell(cell_id)

            rel_velo = {}
            for i in range(0, 3):
                rel_velo[i] = cell.data[CUBA.VELOCITY][i] - \
                                list(par.data[CUBA.VELOCITY])[i]
            mag_rel_velo = math.sqrt(sum(rel_velo[i]**2 for i in range(0, 3)))

        else:
            rel_velo = [1.0e-8, 0.0, 0.0]

        dragforce = np.zeros(3)
        for i in range(0, 3):
            if force_type == "Stokes":
                dragforce[i] = 3.0 * math.pi * visco_OF * \
                                par.data[CUBA.RADIUS] * 2.0 * rel_velo[i]
            elif force_type == "Dala":
                Rnumber = dens_liquid*abs(rel_velo) * \
                                par.data[CUBA.RADIUS] * 2.0/visco_OF
                Cd = (0.63+4.8/math.sqrt(Rnumber))**2
                dragforce[i] = 0.5*Cd*math.pi * par.data[CUBA.RADIUS]**2 * \
                    dens_liquid * abs(rel_velo)*rel_velo[i]
            elif force_type == "Coul":
                Rnumber = dens_liquid * abs(rel_velo) * \
                                par.data[CUBA.RADIUS] * 2.0 / visco_OF
                force[m] = math.pi * \
                    par.data[CUBA.RADIUS]**2 * \
                    dens_liquid * \
                    abs(rel_velo) * \
                    (1.84 * Rnumber**(-0.31) +
                        0.293*Rnumber**(0.06))**(3.45)
            else:
                print "Error: Unknown force_type! Must be Stokes,Coul or Dala."
                sys.exit(1)

        par.data[CUBA.EXTERNAL_APPLIED_FORCE] = tuple(dragforce)
        pc_wflow.update_particles([par])

    run_drag_end = time.time()
    time_drag = time_drag + run_drag_end - run_drag_start

    run_LGT_start = time.time()

    print ("RUNNNING LIGGGHTS for {} timesteps with size {}".format(
        num_timesteps_DEM, dem_wrapper.CM[CUBA.TIME_STEP]))

    # Perform LIGGGHTS calculations
    dem_wrapper.run()

    # ******* Missing: Visualisation of particle trajectories*******

    run_LGT_end = time.time()
    time_LGT = time_LGT + run_LGT_end - run_LGT_start


# Compute total run time
runend = time.time()

print "\ntotal time needed", runend - runstart

print "Fractions"
print ("Reading OpenFoam mesh: {}".format(time_read_OF/(runend - runstart)))
print ("Running OpenFoam: {}".format(time_OF/(runend - runstart)))
print ("Reading liggghts atoms: {}".format(time_read_LM/(runend - runstart)))
print ("Running liggghts: {}".format(time_LGT/(runend - runstart)))
print ("Computing drag forces: {}".format(time_drag/(runend - runstart)))
