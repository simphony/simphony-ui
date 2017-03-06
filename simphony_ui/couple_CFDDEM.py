"""Example to solve 2D poiseuille flow

"""

# Imports general
import os
import sys
import math
import numpy as np
from . import OpenFoam_input

# Imports simphony general
from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem

# Imports simphony-openfoam
from simphony.engine import openfoam_file_io
from simphony.engine import openfoam_internal

# Imports simphony-liggghts
from simphony.engine import liggghts
from simliggghts import CUBAExtension


def main(output_path, mesh_name):
    mode_cfd = "internal"
    mesh_type = "block"

    # Defining the wrapper for OpenFoam
    if mode_cfd == "internal":
        cfd_wrapper = openfoam_internal.Wrapper()
        CUBAExt_cfd = openfoam_internal.CUBAExt
    elif mode_cfd == "io":
        cfd_wrapper = openfoam_file_io.Wrapper()
        CUBAExt_cfd = openfoam_file_io.CUBAExt
    else:
        print "Wrong mode_cfd!"
        sys.exit(1)

    # define the wrapper for LIGGGHTS
    dem_wrapper = liggghts.LiggghtsWrapper(use_internal_interface=True)

    # General settings
    number_iterations = 10

    force_type = "Stokes"

    # OF settings
    num_timesteps_cfd = 10
    timestep_cfd = 2.0e-4
    visco_cfd = 1.0e-3
    dens_liquid = 1000.0
    delta_p = 0.008

    # size of channel in OF
    chansize = [1.0e-1, 1.0e-2, 2.0e-3]

    # number of elements in all channel-directions
    numgrid = [400, 40, 1]

    # **** Liggghts settings *****************

    # The number of DEM steps in each cycle, this is the number of
    # steps that are run at each call of wrapper.run().
    num_timesteps_dem = 10

    # Time step for MD simulation
    timestep_dem = 1e-6

    restart_file = os.path.join(os.path.dirname(__file__), "DEM_input.dat")

    if mode_cfd != "none":

        # **********  Settings for OpenFoam wrapper  **********

        cfd_wrapper.CM[CUBA.NAME] = mesh_name

        cfd_wrapper.CM_extensions[CUBAExt_cfd.GE] = \
            (CUBAExt_cfd.INCOMPRESSIBLE, CUBAExt_cfd.LAMINAR_MODEL)
        # defines solver = simpleFoam
        # other options CUBAExt_cfd.VOF -> interFoam
        #               CUBAExt_cfd.NUMBER_OF_CORES = N -> parallel

        cfd_wrapper.SP[CUBA.TIME_STEP] = timestep_cfd
        cfd_wrapper.SP[CUBA.NUMBER_OF_TIME_STEPS] = num_timesteps_cfd
        cfd_wrapper.SP[CUBA.DENSITY] = dens_liquid
        cfd_wrapper.SP[CUBA.DYNAMIC_VISCOSITY] = visco_cfd

        # setting BCs
        cfd_wrapper.BC[CUBA.VELOCITY] = {
            'inlet': 'zeroGradient',
            'outlet': 'zeroGradient',
            'walls': ('fixedValue', (0, 0, 0)),
            'frontAndBack': 'empty'}
        cfd_wrapper.BC[CUBA.PRESSURE] = {
            'inlet': ('fixedValue', delta_p),
            'outlet': ('fixedValue', 0.0),
            'walls': 'zeroGradient',
            'frontAndBack': 'empty'}

        # Reading mesh and conversion to CUDS file

        if mesh_type == "block":
            path = output_path if mode_cfd == "internal" else "."

            openfoam_file_io.create_block_mesh(
                path, mesh_name, cfd_wrapper,
                OpenFoam_input.blockMeshDict
            )
        else:
            corner_points = [(0.0, 0.0, 0.0),
                             (chansize[0], 0.0, 0.0),
                             (chansize[0], chansize[1], 0.0),
                             (0.0, chansize[1], 0.0),
                             (0.0, 0.0, chansize[2]),
                             (chansize[0], 0.0, chansize[2]),
                             (chansize[0], chansize[1], chansize[2]),
                             (0.0, chansize[1], chansize[2])]

            openfoam_file_io.create_quad_mesh(output_path, mesh_name,
                                              cfd_wrapper, corner_points,
                                              numgrid[0], numgrid[1],
                                              numgrid[2])

        mesh_cfd = cfd_wrapper.get_dataset(mesh_name)

    # ********* Settings for liggghts wrapper **********

    # Reading particle file
    particles_list = liggghts.read_data_file(restart_file)

    pc_flow = particles_list[0]
    pc_wall = particles_list[1]

    pc_flow.name = "flow_chain"
    pc_wall.name = "wall"

    num_particles = pc_flow.count_of(CUDSItem.PARTICLE)

    # shift boxorigin to 0,0,0 and update particles accordingly
    boxorigin = pc_flow.data_extension[CUBAExtension.BOX_ORIGIN]

    for par in pc_flow.iter_particles():
        par.coordinates = (par.coordinates[0] - boxorigin[0],
                           par.coordinates[1] - boxorigin[1],
                           par.coordinates[2] - boxorigin[2])
        pc_flow.update_particles([par])

    pc_flow.data_extension[CUBAExtension.BOX_ORIGIN] = (0.0, 0.0, 0.0)
    # Reading input files: done

    # Add particle (containers) to wrapper
    dem_wrapper.add_dataset(pc_flow)
    dem_wrapper.add_dataset(pc_wall)
    pc_wflow = dem_wrapper.get_dataset(pc_flow.name)

    # define the CM component of the SimPhoNy application model:
    dem_wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = num_timesteps_dem
    dem_wrapper.CM[CUBA.TIME_STEP] = timestep_dem

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

    if mode_cfd is not "none":
        # Generate cell list
        cellmat = {}
        index = {}
        gridsize = [chansize[0]/numgrid[0],
                    chansize[1]/numgrid[1],
                    chansize[2]/numgrid[2]]

        for cell in mesh_cfd.iter_cells():
            LLN = [chansize[0]*2, chansize[1]*2, chansize[2]*2]
            for k in range(0, 8):
                for i in range(0, 3):
                    if mesh_cfd.get_point(cell.points[k]).coordinates[i] < \
                            LLN[i]:
                        LLN[i] = \
                            mesh_cfd.get_point(cell.points[k]).coordinates[i]

            for i in range(0, 3):
                index[i] = round(LLN[i]/gridsize[i])

            cellmat[index[0], index[1], index[2]] = cell.uid

    # ****************** MAIN LOOP *******************************

    # Repeating OF calculation several times with modified pressure drop last
    # result from previous iteration as input for new iteration
    for numrun in range(0, number_iterations):

        if mode_cfd != "none":
            # running OpenFoam
            cfd_wrapper.run()

        m = 0
        force = np.zeros(num_particles)

        # Compute relative velocity & drag force
        for par in pc_wflow.iter_particles():

            testpoint = par.coordinates

            if mode_cfd is not "none":

                index = {}
                for i in range(0, 3):

                    index[i] = int(math.floor(testpoint[i] /
                                              (chansize[i]/float(numgrid[i]))))

                    if index[i] == numgrid[i]:
                        index[i] = 0
                    elif index[i] == -1:
                        index[i] = numgrid[i]-1

                cell_id = cellmat[index[0], index[1], index[2]]
                cell = mesh_cfd.get_cell(cell_id)

                rel_velo = {}
                for i in range(0, 3):
                    rel_velo[i] = cell.data[CUBA.VELOCITY][i] - \
                        list(par.data[CUBA.VELOCITY])[i]

            else:
                rel_velo = [1.0e-8, 0.0, 0.0]

            dragforce = np.zeros(3)
            for i in range(0, 3):
                if force_type == "Stokes":
                    dragforce[i] = 3.0 * math.pi * visco_cfd * \
                        par.data[CUBA.RADIUS] * 2.0 * rel_velo[i]
                elif force_type == "Dala":
                    Rnumber = dens_liquid*abs(rel_velo) * \
                        par.data[CUBA.RADIUS] * 2.0/visco_cfd
                    Cd = (0.63+4.8/math.sqrt(Rnumber))**2
                    dragforce[i] = 0.5*Cd*math.pi * \
                        par.data[CUBA.RADIUS]**2 * dens_liquid * \
                        abs(rel_velo)*rel_velo[i]
                elif force_type == "Coul":
                    Rnumber = dens_liquid * abs(rel_velo) * \
                        par.data[CUBA.RADIUS] * 2.0 / visco_cfd
                    force[m] = math.pi * \
                        par.data[CUBA.RADIUS]**2 * \
                        dens_liquid * \
                        abs(rel_velo) * \
                        (1.84 * Rnumber**(-0.31) +
                            0.293*Rnumber**0.06)**3.45
                else:
                    print "Error: Unknown force_type! Must be " \
                          "Stokes,Coul or Dala."
                    sys.exit(1)

            par.data[CUBA.EXTERNAL_APPLIED_FORCE] = tuple(dragforce)
            pc_wflow.update_particles([par])

        # Perform LIGGGHTS calculations
        dem_wrapper.run()

        # ******* Missing: Visualisation of particle trajectories*******

    return dem_wrapper, cfd_wrapper
