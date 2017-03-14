import math
import numpy as np
from simphony.core.cuba import CUBA
from simphony_ui.openfoam_wrapper_creation import (
    create_openfoam_wrapper, create_openfoam_mesh)
from simphony_ui.liggghts_wrapper_creation import (
    create_liggghts_wrapper, create_liggghts_datasets)


def run_calc(global_settings, openfoam_settings, liggghts_settings):
    """ Main routine which creates the wrappers and run the calculation

    Parameters
    ----------
    global_settings : GlobalParametersModel
        The trait model containing the global parameters of the calculation
    openfoam_settings : OpenfoamModel
        The trait model containing the Openfoam parameters
    liggghts_settings : LiggghtsModel
        The trait model containing the Liggghts parameters

    Returns
    -------
    openfoam_wrapper, liggghts_wrapper:
        A tuple containing the wrapper of Openfoam and the wrapper of Liggghts
    """
    # Create Openfoam wrapper
    openfoam_wrapper = create_openfoam_wrapper(openfoam_settings)

    density = openfoam_wrapper.SP[CUBA.DENSITY]
    viscosity = openfoam_wrapper.SP[CUBA.DYNAMIC_VISCOSITY]

    channel_size = [
        openfoam_settings.channel_size_x,
        openfoam_settings.channel_size_y,
        openfoam_settings.channel_size_z
    ]
    num_grid = [
        openfoam_settings.num_grid_x,
        openfoam_settings.num_grid_y,
        openfoam_settings.num_grid_z
    ]

    openfoam_mesh = create_openfoam_mesh(openfoam_wrapper, openfoam_settings)

    # Create Liggghts wrapper
    liggghts_wrapper = create_liggghts_wrapper(liggghts_settings)

    flow_dataset, wall_dataset = create_liggghts_datasets(liggghts_settings)

    liggghts_wrapper.add_dataset(flow_dataset)
    liggghts_wrapper.add_dataset(wall_dataset)

    flow_dataset = liggghts_wrapper.get_dataset(flow_dataset.name)

    # Generate cell list
    cellmat = {}
    index = np.zeros(3, dtype=np.int)
    gridsize = [
        channel_size[0] / num_grid[0],
        channel_size[1] / num_grid[1],
        channel_size[2] / num_grid[2]
    ]

    for cell in openfoam_mesh.iter_cells():
        lln = [
            channel_size[0] * 2,
            channel_size[1] * 2,
            channel_size[2] * 2]
        for k in range(8):
            for i in range(3):
                if openfoam_mesh.get_point(
                        cell.points[k]).coordinates[i] < lln[i]:
                    lln[i] = openfoam_mesh.get_point(
                        cell.points[k]).coordinates[i]

        for i in range(0, 3):
            index[i] = round(lln[i]/gridsize[i])

        cellmat[index[0], index[1], index[2]] = cell.uid

    # Main loop

    # Repeating OF calculation several times with modified pressure drop last
    # result from previous iteration as input for new iteration
    for numrun in range(global_settings.num_iterations):
        # Perform Openfoam calculations
        openfoam_wrapper.run()

        # Compute relative velocity & drag force
        for particle in flow_dataset.iter_particles():
            testpoint = particle.coordinates
            index = np.zeros(3, dtype=np.int)

            for i in range(3):
                index[i] = int(math.floor(
                    testpoint[i] / (channel_size[i] /
                                    float(num_grid[i]))))

                if index[i] == num_grid[i]:
                    index[i] = 0
                elif index[i] == -1:
                    index[i] = num_grid[i] - 1

            cell_id = cellmat[index[0], index[1], index[2]]
            cell = openfoam_mesh.get_cell(cell_id)

            rel_velo = np.zeros(3, dtype=np.int)
            for i in range(3):
                rel_velo[i] = cell.data[CUBA.VELOCITY][i] - \
                    list(particle.data[CUBA.VELOCITY])[i]

            dragforce = np.zeros(3)
            for i in range(3):
                if global_settings.force_type == "Stokes":
                    dragforce[i] = \
                        3.0 * math.pi * viscosity * \
                        particle.data[CUBA.RADIUS] * 2.0 * rel_velo[i]
                elif global_settings.force_type == "Dala":
                    reynold_number = \
                        density * np.linalg.norm(rel_velo) * \
                        particle.data[CUBA.RADIUS] * 2.0 / viscosity
                    coeff = (0.63+4.8/math.sqrt(reynold_number))**2
                    dragforce[i] = \
                        0.5*coeff*math.pi * particle.data[CUBA.RADIUS]**2 * \
                        density * np.linalg.norm(rel_velo)*rel_velo[i]
                elif global_settings.force_type == "Coul":
                    reynold_number = \
                        density * np.linalg.norm(rel_velo) * \
                        particle.data[CUBA.RADIUS] * 2.0 / viscosity
                    dragforce[i] = \
                        math.pi * particle.data[CUBA.RADIUS]**2 * \
                        density * np.linalg.norm(rel_velo) * \
                        (1.84 * reynold_number**(-0.31) +
                            0.293*reynold_number**0.06)**3.45
                else:
                    raise ValueError(
                        '{} is not a supported force '
                        'type'.format(global_settings.force_type))

            particle.data[CUBA.EXTERNAL_APPLIED_FORCE] = tuple(dragforce)
            flow_dataset.update_particles([particle])

        # Perform Liggghts calculations
        liggghts_wrapper.run()

    return openfoam_wrapper, liggghts_wrapper
