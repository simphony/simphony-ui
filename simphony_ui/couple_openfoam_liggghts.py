from __future__ import division
import math

import numpy as np
from simphony.core.cuba import CUBA

from simphony_ui.liggghts_model.liggghts_wrapper_creation import (
    create_liggghts_wrapper, create_liggghts_datasets)
from simphony_ui.openfoam_model.openfoam_wrapper_creation import (
    create_openfoam_wrapper, create_openfoam_mesh)


def run_calc(global_settings, openfoam_settings,
             liggghts_settings, progress_callback, event_lock=None):
    """ Main routine which creates the wrappers and run the calculation

    Parameters
    ----------
    global_settings : GlobalParametersModel
        The trait model containing the global parameters of the calculation
    openfoam_settings : OpenfoamModel
        The trait model containing the Openfoam parameters
    liggghts_settings : LiggghtsModel
        The trait model containing the Liggghts parameters
    progress_callback
        A callback function which will return the progress of the computation
        which will be called with the progress state of the calculation as an
        integer in the range [0, 100]
    event_lock: threading.Event
        An event to trigger the continuation of the calculation so that
        the callback routine has a chance for copying the datasets.
        The callback routine must .set() the event, otherwise the
        calculation will be suspended and eventually timeout.
        The default None disables the check and let the evaluation continues
        to the end.

    Returns
    -------
    datasets:
        A tuple containing the datasets from openfoam and ligghts.
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

    datasets = None
    # Repeating OF calculation several times with modified pressure drop last
    # result from previous iteration as input for new iteration
    for numrun in xrange(global_settings.num_iterations):
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

            dragforce = compute_drag_force(
                global_settings.force_type,
                particle.data[CUBA.RADIUS],
                rel_velo,
                viscosity,
                density
            )

            particle.data[CUBA.EXTERNAL_APPLIED_FORCE] = tuple(dragforce)
            flow_dataset.update_particles([particle])

        # Perform Liggghts calculations
        liggghts_wrapper.run()

        datasets = (
            openfoam_wrapper.get_dataset('mesh'),
            liggghts_wrapper.get_dataset('flow_particles'),
            liggghts_wrapper.get_dataset('wall_particles'))

        if numrun % global_settings.update_frequency == 0:
            progress_callback(datasets,
                              numrun,
                              global_settings.num_iterations)
            if event_lock is not None:
                # We wait 10 seconds for the UI to give us the chance
                # to continue. The operation should actually be fast
                # (we just copy the datasets). If we timeout, it's likely
                # that the UI is stuck, so we want to quit.
                if not event_lock.wait(10.0):
                    return None
                event_lock.clear()

    return datasets


def compute_drag_force(force_type, radius, rel_velo, viscosity, density):
    """ Function which compute the force applied on a particle

    Parameters
    ----------
    force_type : Str
        The type of the applied force. Supported force types are
        "Stokes", "Dala" and "Coul"
    radius : Float
        The radius of the particle
    rel_velo : List
        The relative velocity of the particle
    viscosity : Float
        The fluid viscosity
    density : Float
        The fluid density

    Returns
    -------
    dragforce : List
        The computed force applied on the particle
    """
    dragforce = np.zeros(3)

    for i in range(3):
        if force_type == "Stokes":
            dragforce[i] = \
                3.0 * math.pi * viscosity * \
                radius * 2.0 * rel_velo[i]
        elif force_type == "Dala":
            reynold_number = \
                density * np.linalg.norm(rel_velo) * radius * 2.0 / viscosity
            coeff = (0.63 + 4.8 / math.sqrt(reynold_number)) ** 2
            dragforce[i] = \
                0.5 * coeff * math.pi * radius ** 2 * \
                density * np.linalg.norm(rel_velo) * rel_velo[i]
        elif force_type == "Coul":
            reynold_number = \
                density * np.linalg.norm(rel_velo) * \
                radius * 2.0 / viscosity
            dragforce[i] = \
                math.pi * radius ** 2 * \
                density * np.linalg.norm(rel_velo) * \
                (1.84 * reynold_number ** (-0.31) +
                 0.293 * reynold_number ** 0.06) ** 3.45
        else:
            raise ValueError(
                '{} is not a supported force '
                'type'.format(force_type))

    return dragforce
