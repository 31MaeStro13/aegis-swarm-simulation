
"""Automated tests for the AEGIS SAR simulator."""

import numpy as np
import pytest

from algorithms.allocation import allocate_search_tasks
from probability.bayesian import BayesianSearchMap
from simulation.drone import SearchDrone
from simulation.engine import SwarmSimulation
from simulation.grid import SearchGrid


def test_grid_creation_and_coverage():
    grid = SearchGrid(cols=40, rows=40)

    assert grid.grid_size == [40, 40]
    assert grid.get_coverage(5, 10) == 0

    grid.mark_searched(5, 10)
    grid.mark_searched(5, 10)

    assert grid.get_coverage(5, 10) == 2
    assert grid.coverage.shape == (40, 40)


def test_grid_rejects_out_of_bounds_cell():
    grid = SearchGrid(cols=40, rows=40)

    with pytest.raises(ValueError):
        grid.mark_searched(40, 10)


def test_bayesian_probability_map():
    probability_map = BayesianSearchMap(cols=40, rows=40)

    assert probability_map.probability.shape == (40, 40)
    assert np.isclose(probability_map.total_probability(), 1.0)

    original_probability = probability_map.probability[20, 20]

    probability_map.update_after_search(
        x=20,
        y=20,
        p_detect=0.8,
    )

    assert probability_map.probability[20, 20] < original_probability
    assert np.isclose(probability_map.total_probability(), 1.0)


def test_search_task_allocation():
    drone_ids = [
        "UAV-01",
        "UAV-02",
        "UAV-03",
        "UAV-04",
        "UAV-05",
    ]

    assignments = allocate_search_tasks(40, 40, drone_ids)

    assert set(assignments) == set(drone_ids)
    assert all(len(tasks) == 320 for tasks in assignments.values())

    all_cells = {
        (task.x, task.y)
        for tasks in assignments.values()
        for task in tasks
    }

    assert len(all_cells) == 1600


def test_drone_movement_and_task_execution():
    drone = SearchDrone("UAV-01", start_x=0, start_y=0)

    assignments = allocate_search_tasks(
        40,
        40,
        ["UAV-01"],
    )

    task = assignments["UAV-01"][1]

    drone.execute_task(task)

    assert (drone.state.x, drone.state.y) == (task.x, task.y)
    assert drone.completed_tasks == 1
    assert drone.state.battery < 100.0


def test_failover_redistributes_unfinished_tasks():
    simulation = SwarmSimulation(
        cols=40,
        rows=40,
        num_drones=5,
        seed=42,
        failure_tick=2,
    )

    simulation.step()
    telemetry = simulation.step()

    assert simulation.tick == 2
    assert len(simulation.failover_events) == 1
    assert simulation.failover_events[0].failed_drone_id == "UAV-01"

    failed_drone = simulation.drones["UAV-01"]

    assert failed_drone.state.status.value == "failed"
    assert len(simulation.task_queues["UAV-01"]) == 0
    assert len(telemetry.event_log) == 1


def test_mission_completes_after_drone_failure():
    simulation = SwarmSimulation(
        cols=40,
        rows=40,
        num_drones=5,
        seed=42,
        failure_tick=2,
    )

    simulation.run(max_ticks=10000)

    summary = simulation.summary()

    assert summary["grid_coverage"] == 1.0
    assert np.isclose(summary["probability_coverage"], 1.0)
    assert summary["failed_drones"] == ["UAV-01"]
    assert sum(summary["completed_tasks"].values()) == 1600
    assert summary["ticks"] < 10000
