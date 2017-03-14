"""Example to solve 2D poiseuille flow

"""

# Imports general
import os
import sys
import math
import numpy as np

# Imports simphony general
from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem

# Imports simphony-openfoam
from simphony.engine import openfoam_file_io
from simphony.engine import openfoam_internal

# Imports simphony-liggghts
from simphony.engine import liggghts
from simliggghts import CUBAExtension


def run_calc(output_path, mesh_name):
    """Executes the full calculation"""
    openfoam_mode = "internal"
    mesh_type = "block"

    # Defining the wrapper for OpenFoam
    if openfoam_mode == "internal":
        openfoam_wrapper = openfoam_internal.Wrapper()
        openfoam_cuba_ext = openfoam_internal.CUBAExt
    elif openfoam_mode == "io":
        openfoam_wrapper = openfoam_file_io.Wrapper()
        openfoam_cuba_ext = openfoam_file_io.CUBAExt
    else:
        print "Wrong mode_cfd!"
        sys.exit(1)

    # define the wrapper for LIGGGHTS
    liggghts_wrapper = liggghts.LiggghtsWrapper(use_internal_interface=True)

    # General settings
    global_number_iterations = 10
    global_force_type = "Stokes"

    # OF settings
    openfoam_num_timesteps = 10
    openfoam_timestep = 2.0e-4
    openfoam_viscosity = 1.0e-3
    openfoam_density = 1000.0
    openfoam_delta_p = 0.008

    # size of channel in OF
    openfoam_chansize = [1.0e-1, 1.0e-2, 2.0e-3]

    # number of elements in all channel-directions
    openfoam_numgrid = [400, 40, 1]

    # **** Liggghts settings *****************

    # The number of DEM steps in each cycle, this is the number of
    # steps that are run at each call of wrapper.run().
    liggghts_num_timesteps = 10

    # Time step for MD simulation
    liggghts_timestep = 1e-6

    restart_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "liggghts_input.dat")

    if openfoam_mode != "none":

        # **********  Settings for OpenFoam wrapper  **********

        openfoam_wrapper.CM[CUBA.NAME] = mesh_name

        openfoam_wrapper.CM_extensions[openfoam_cuba_ext.GE] = \
            (openfoam_cuba_ext.INCOMPRESSIBLE, openfoam_cuba_ext.LAMINAR_MODEL)
        # defines solver = simpleFoam
        # other options cuba_ext_cfd.VOF -> interFoam
        #               cuba_ext_cfd.NUMBER_OF_CORES = N -> parallel

        openfoam_wrapper.SP[CUBA.TIME_STEP] = openfoam_timestep
        openfoam_wrapper.SP[CUBA.NUMBER_OF_TIME_STEPS] = openfoam_num_timesteps
        openfoam_wrapper.SP[CUBA.DENSITY] = openfoam_density
        openfoam_wrapper.SP[CUBA.DYNAMIC_VISCOSITY] = openfoam_viscosity

        # setting BCs
        openfoam_wrapper.BC[CUBA.VELOCITY] = {
            'inlet': 'zeroGradient',
            'outlet': 'zeroGradient',
            'walls': ('fixedValue', (0, 0, 0)),
            'frontAndBack': 'empty'}
        openfoam_wrapper.BC[CUBA.PRESSURE] = {
            'inlet': ('fixedValue', openfoam_delta_p),
            'outlet': ('fixedValue', 0.0),
            'walls': 'zeroGradient',
            'frontAndBack': 'empty'}

        # Reading mesh and conversion to CUDS file

        if mesh_type == "block":
            path = output_path if openfoam_mode == "internal" else "."

            input_file = \
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'openfoam_input.txt'
                )

            with open(input_file, 'r') as input_file:
                input_mesh = input_file.read()

            openfoam_file_io.create_block_mesh(
                path, mesh_name, openfoam_wrapper,
                input_mesh
            )
        else:
            corner_points = [
                (0.0, 0.0, 0.0),
                (openfoam_chansize[0], 0.0, 0.0),
                (openfoam_chansize[0], openfoam_chansize[1], 0.0),
                (0.0, openfoam_chansize[1], 0.0),
                (0.0, 0.0, openfoam_chansize[2]),
                (openfoam_chansize[0], 0.0, openfoam_chansize[2]),
                (
                    openfoam_chansize[0],
                    openfoam_chansize[1],
                    openfoam_chansize[2]),
                (0.0, openfoam_chansize[1], openfoam_chansize[2])
            ]

            openfoam_file_io.create_quad_mesh(
                output_path, mesh_name,
                openfoam_wrapper, corner_points,
                openfoam_numgrid[0], openfoam_numgrid[1],
                openfoam_numgrid[2]
            )

        openfoam_mesh = openfoam_wrapper.get_dataset(mesh_name)

    # ********* Settings for liggghts wrapper **********

    # Reading particle file
    particles_list = liggghts.read_data_file(restart_file)

    particle_flow = particles_list[0]
    particle_wall = particles_list[1]

    particle_flow.name = "flow_chain"
    particle_wall.name = "wall"

    num_particles = particle_flow.count_of(CUDSItem.PARTICLE)
    num_particles_wall = particle_wall.count_of(CUDSItem.PARTICLE)
    # Just print the value so that flake8 doesn't complain...
    print "{} particles on the wall".format(num_particles_wall)

    # shift boxorigin to 0,0,0 and update particles accordingly
    boxorigin = particle_flow.data_extension[CUBAExtension.BOX_ORIGIN]

    for par in particle_flow.iter_particles():
        par.coordinates = (par.coordinates[0] - boxorigin[0],
                           par.coordinates[1] - boxorigin[1],
                           par.coordinates[2] - boxorigin[2])
        particle_flow.update_particles([par])

    particle_flow.data_extension[CUBAExtension.BOX_ORIGIN] = (0.0, 0.0, 0.0)
    # Reading input files: done

    # Add particle (containers) to wrapper
    liggghts_wrapper.add_dataset(particle_flow)
    liggghts_wrapper.add_dataset(particle_wall)
    pc_wflow = liggghts_wrapper.get_dataset(particle_flow.name)

    # define the CM component of the SimPhoNy application model:
    liggghts_wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = liggghts_num_timesteps
    liggghts_wrapper.CM[CUBA.TIME_STEP] = liggghts_timestep

    # Define the BC component of the SimPhoNy application model:
    liggghts_wrapper.BC_extension[liggghts.CUBAExtension.BOX_FACES] = [
        "periodic",
        "fixed",
        "periodic"
    ]

    # Information about fixed walls: 0: No fixation, 1: Particles are fixed
    liggghts_wrapper.BC_extension[liggghts.CUBAExtension.FIXED_GROUP] = [0, 1]

    # MATERIAL PARAMETERS INPUT
    liggghts_wrapper.SP[CUBA.YOUNG_MODULUS] = [2.e4, 2.e4]
    liggghts_wrapper.SP[CUBA.POISSON_RATIO] = [0.45, 0.45]
    liggghts_wrapper.SP[CUBA.RESTITUTION_COEFFICIENT] = \
        [0.95, 0.95, 0.95, 0.95]
    liggghts_wrapper.SP[CUBA.FRICTION_COEFFICIENT] = [0.0, 0.0, 0.0, 0.0]
    liggghts_wrapper.SP[CUBA.COHESION_ENERGY_DENSITY] = [0.0, 0.0, 0.0, 0.0]

    liggghts_wrapper.SP_extension[liggghts.CUBAExtension.PAIR_POTENTIALS] = \
        ['repulsion', 'cohesion']

    if openfoam_mode is not "none":
        # Generate cell list
        cellmat = {}
        index = {}
        gridsize = [openfoam_chansize[0] / openfoam_numgrid[0],
                    openfoam_chansize[1] / openfoam_numgrid[1],
                    openfoam_chansize[2] / openfoam_numgrid[2]]

        for cell in openfoam_mesh.iter_cells():
            lln = [
                openfoam_chansize[0] * 2,
                openfoam_chansize[1] * 2,
                openfoam_chansize[2] * 2]
            for k in range(0, 8):
                for i in range(0, 3):
                    if openfoam_mesh.get_point(
                            cell.points[k]).coordinates[i] < lln[i]:
                        lln[i] = openfoam_mesh.get_point(
                            cell.points[k]).coordinates[i]

            for i in range(0, 3):
                index[i] = round(lln[i]/gridsize[i])

            cellmat[index[0], index[1], index[2]] = cell.uid

    # ****************** MAIN LOOP *******************************

    # Repeating OF calculation several times with modified pressure drop last
    # result from previous iteration as input for new iteration
    for numrun in range(0, global_number_iterations):

        if openfoam_mode != "none":
            # running OpenFoam
            openfoam_wrapper.run()

        m = 0
        force = np.zeros(num_particles)

        # Compute relative velocity & drag force
        for par in pc_wflow.iter_particles():

            testpoint = par.coordinates

            if openfoam_mode is not "none":

                index = {}
                for i in range(0, 3):

                    index[i] = int(math.floor(
                        testpoint[i] / (openfoam_chansize[i] /
                                        float(openfoam_numgrid[i]))))

                    if index[i] == openfoam_numgrid[i]:
                        index[i] = 0
                    elif index[i] == -1:
                        index[i] = openfoam_numgrid[i] - 1

                cell_id = cellmat[index[0], index[1], index[2]]
                cell = openfoam_mesh.get_cell(cell_id)

                rel_velo = {}
                for i in range(0, 3):
                    rel_velo[i] = cell.data[CUBA.VELOCITY][i] - \
                        list(par.data[CUBA.VELOCITY])[i]

            else:
                rel_velo = [1.0e-8, 0.0, 0.0]

            dragforce = np.zeros(3)
            for i in range(0, 3):
                if global_force_type == "Stokes":
                    dragforce[i] = \
                        3.0 * math.pi * openfoam_viscosity * \
                        par.data[CUBA.RADIUS] * 2.0 * rel_velo[i]
                elif global_force_type == "Dala":
                    reynold_number = \
                        openfoam_density * abs(rel_velo) * \
                        par.data[CUBA.RADIUS] * 2.0 / openfoam_viscosity
                    coeff = (0.63+4.8/math.sqrt(reynold_number))**2
                    dragforce[i] = \
                        0.5*coeff*math.pi * par.data[CUBA.RADIUS]**2 * \
                        openfoam_density * abs(rel_velo)*rel_velo[i]
                elif global_force_type == "Coul":
                    reynold_number = \
                        openfoam_density * abs(rel_velo) * \
                        par.data[CUBA.RADIUS] * 2.0 / openfoam_viscosity
                    force[m] = \
                        math.pi * par.data[CUBA.RADIUS]**2 * \
                        openfoam_density * abs(rel_velo) * \
                        (1.84 * reynold_number**(-0.31) +
                            0.293*reynold_number**0.06)**3.45
                else:
                    print "Error: Unknown force_type! Must be " \
                          "Stokes,Coul or Dala."
                    sys.exit(1)

            par.data[CUBA.EXTERNAL_APPLIED_FORCE] = tuple(dragforce)
            pc_wflow.update_particles([par])

        # Perform LIGGGHTS calculations
        liggghts_wrapper.run()

        # ******* Missing: Visualisation of particle trajectories*******

    return liggghts_wrapper, openfoam_wrapper
