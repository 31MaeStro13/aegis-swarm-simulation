"""
Unit tests for Aegis SAR Data Contracts (MVP 0.1).
Verifies strict validation, extra=forbid, matrix consistency, and determinism.
"""

import pytest
from pydantic import ValidationError
from contracts.models import (
    DroneStatus,
    DroneState,
    SearchTask,
    FailoverEvent,
    TelemetryPacket,
)


def create_dummy_maps(cols: int = 40, rows: int = 40):
    val = 1.0 / (cols * rows)
    prob_map = [[val for _ in range(cols)] for _ in range(rows)]
    cov_map = [[0 for _ in range(cols)] for _ in range(rows)]
    return prob_map, cov_map


def test_drone_state_valid():
    drone = DroneState(id="drone_1", x=10, y=20, battery=85.5, status=DroneStatus.SEARCHING)
    assert drone.id == "drone_1"
    assert drone.x == 10
    assert drone.y == 20
    assert drone.battery == 85.5
    assert drone.status == "searching"


def test_drone_state_forbid_extra():
    with pytest.raises(ValidationError):
        DroneState(
            id="drone_1",
            x=10,
            y=20,
            battery=85.5,
            status=DroneStatus.SEARCHING,
            extra_field="malicious",  # Should trigger extra=forbid
        )


def test_search_task_priority_range():
    # Valid priority in [0.0, 1.0]
    task = SearchTask(task_id="task_1", x=5, y=5, priority=0.85)
    assert task.priority == 0.85

    # Invalid priority > 1.0
    with pytest.raises(ValidationError):
        SearchTask(task_id="task_1", x=5, y=5, priority=1.5)

    # Invalid negative priority
    with pytest.raises(ValidationError):
        SearchTask(task_id="task_1", x=5, y=5, priority=-0.1)


def test_telemetry_packet_deterministic_and_valid():
    prob_map, cov_map = create_dummy_maps(40, 40)
    drone = DroneState(id="drone_1", x=0, y=0, battery=100.0, status=DroneStatus.IDLE)

    packet = TelemetryPacket(
        mission_id="mission_001",
        tick=0,
        sim_time_s=0.0,
        grid_size=(40, 40),
        drones=[drone],
        probability_map=prob_map,
        coverage_map=cov_map,
        event_log=[],
    )

    json_str = packet.model_dump_json()
    assert "sim_time_s" in json_str
    assert "timestamp" not in json_str  # Determinism guaranteed

    reconstructed = TelemetryPacket.model_validate_json(json_str)
    assert reconstructed.tick == 0
    assert reconstructed.sim_time_s == 0.0


def test_telemetry_packet_drone_out_of_bounds():
    prob_map, cov_map = create_dummy_maps(40, 40)
    # Drone x=40 exceeds grid width 40 (indices 0..39)
    out_of_bounds_drone = DroneState(id="drone_1", x=40, y=10, battery=100.0, status=DroneStatus.IDLE)

    with pytest.raises(ValidationError, match="coordinate x=40 exceeds grid width 40"):
        TelemetryPacket(
            mission_id="mission_001",
            tick=0,
            sim_time_s=0.0,
            grid_size=(40, 40),
            drones=[out_of_bounds_drone],
            probability_map=prob_map,
            coverage_map=cov_map,
            event_log=[],
        )


def test_telemetry_packet_matrix_dimension_mismatch():
    prob_map, cov_map = create_dummy_maps(39, 40)  # cols = 39 instead of 40
    drone = DroneState(id="drone_1", x=0, y=0, battery=100.0, status=DroneStatus.IDLE)

    with pytest.raises(ValidationError, match="does not match grid cols"):
        TelemetryPacket(
            mission_id="mission_001",
            tick=0,
            sim_time_s=0.0,
            grid_size=(40, 40),
            drones=[drone],
            probability_map=prob_map,
            coverage_map=cov_map,
            event_log=[],
        )


def test_telemetry_packet_prob_sum_mismatch():
    cols, rows = 40, 40
    # Values sum to 2.0 instead of ~1.0
    prob_map = [[2.0 / (cols * rows) for _ in range(cols)] for _ in range(rows)]
    cov_map = [[0 for _ in range(cols)] for _ in range(rows)]
    drone = DroneState(id="drone_1", x=0, y=0, battery=100.0, status=DroneStatus.IDLE)

    with pytest.raises(ValidationError, match="must be approximately 1.0"):
        TelemetryPacket(
            mission_id="mission_001",
            tick=0,
            sim_time_s=0.0,
            grid_size=(40, 40),
            drones=[drone],
            probability_map=prob_map,
            coverage_map=cov_map,
            event_log=[],
        )
