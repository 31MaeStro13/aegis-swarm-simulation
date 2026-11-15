"""
Aegis SAR Data Contracts - MVP 0.1
Authoritative Pydantic models with strict validation, zero field drift, and deterministic simulation timing.
"""

from enum import Enum
import math
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel, Field, ConfigDict, PositiveInt, model_validator


class DroneStatus(str, Enum):
    """Operational status of an individual UAV in the swarm."""
    IDLE = "idle"
    SEARCHING = "searching"
    RETURNING = "returning"
    FAILED = "failed"


class DroneState(BaseModel):
    """Discrete state of a single drone within the simulation grid."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, description="Unique drone identifier (e.g. 'drone_1')")
    x: int = Field(..., ge=0, description="Column index (0-indexed)")
    y: int = Field(..., ge=0, description="Row index (0-indexed)")
    battery: float = Field(..., ge=0.0, le=100.0, description="Battery level percentage (0.0 - 100.0)")
    status: DroneStatus = Field(..., description="Current operational state")


class SearchTask(BaseModel):
    """Elementary cell search assignment."""
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(..., min_length=1, description="Unique task identifier (e.g. 'task_042')")
    x: int = Field(..., ge=0, description="Target column index")
    y: int = Field(..., ge=0, description="Target row index")
    priority: float = Field(..., ge=0.0, le=1.0, description="Prior probability density in cell [0.0, 1.0]")
    assigned_drone_id: Optional[str] = Field(None, description="Assigned drone ID or None if pending")


class FailoverEvent(BaseModel):
    """Event triggered upon simulated UAV failure and sector reassignment."""
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(..., min_length=1, description="Unique event identifier")
    tick: int = Field(..., ge=0, description="Simulation step when failure occurred")
    failed_drone_id: str = Field(..., min_length=1, description="ID of the failed drone")
    reason: str = Field("simulated_hardware_failure", description="Reason for failure")
    reassigned_cells: Dict[str, List[Tuple[int, int]]] = Field(
        default_factory=dict,
        description="Reassigned cells mapping: drone_id -> [(x, y), ...]"
    )


class TelemetryPacket(BaseModel):
    """
    Consolidated state snapshot broadcasted at each simulation step.
    Strictly deterministic: uses sim_time_s instead of wall-clock time for repeatable seed runs.
    """
    model_config = ConfigDict(extra="forbid")

    mission_id: str = Field(..., min_length=1, description="Unique mission run identifier")
    tick: int = Field(..., ge=0, description="Discrete simulation step counter (0, 1, 2...)")
    sim_time_s: float = Field(..., ge=0.0, description="Simulation time in seconds from start")
    grid_size: Tuple[PositiveInt, PositiveInt] = Field((40, 40), description="Grid dimensions (cols, rows)")
    drones: List[DroneState] = Field(..., description="List of all drone states")
    probability_map: List[List[float]] = Field(..., description="Normalized float probability matrix (rows x cols)")
    coverage_map: List[List[int]] = Field(..., description="Integer visit counter matrix (rows x cols)")
    event_log: List[FailoverEvent] = Field(default_factory=list, description="Recent failover events log")

    @model_validator(mode="after")
    def validate_simulation_consistency(self) -> "TelemetryPacket":
        cols, rows = self.grid_size

        # 1. Validate probability_map dimensions and properties
        if len(self.probability_map) != rows:
            raise ValueError(
                f"probability_map height ({len(self.probability_map)}) does not match grid rows ({rows})"
            )
        prob_sum = 0.0
        for r_idx, row in enumerate(self.probability_map):
            if len(row) != cols:
                raise ValueError(
                    f"probability_map row {r_idx} length ({len(row)}) does not match grid cols ({cols})"
                )
            for c_idx, val in enumerate(row):
                if not math.isfinite(val) or val < 0.0 or val > 1.0:
                    raise ValueError(
                        f"probability_map[{r_idx}][{c_idx}] = {val} is not a valid probability in [0.0, 1.0]"
                    )
                prob_sum += val

        # Allow slight floating point tolerance for normalized sum
        if not (0.95 <= prob_sum <= 1.05):
            raise ValueError(f"Sum of probability_map cells ({prob_sum:.4f}) must be approximately 1.0")

        # 2. Validate coverage_map dimensions and non-negativity
        if len(self.coverage_map) != rows:
            raise ValueError(
                f"coverage_map height ({len(self.coverage_map)}) does not match grid rows ({rows})"
            )
        for r_idx, row in enumerate(self.coverage_map):
            if len(row) != cols:
                raise ValueError(
                    f"coverage_map row {r_idx} length ({len(row)}) does not match grid cols ({cols})"
                )
            for c_idx, val in enumerate(row):
                if val < 0:
                    raise ValueError(
                        f"coverage_map[{r_idx}][{c_idx}] = {val} cannot be negative"
                    )

        # 3. Validate drone coordinates are within grid bounds
        for drone in self.drones:
            if drone.x >= cols:
                raise ValueError(f"Drone {drone.id} coordinate x={drone.x} exceeds grid width {cols}")
            if drone.y >= rows:
                raise ValueError(f"Drone {drone.id} coordinate y={drone.y} exceeds grid height {rows}")

        return self
