
"""Main simulation engine for the AEGIS SAR swarm."""

from collections import deque

from contracts.models import (
    DroneState,
    DroneStatus,
    FailoverEvent,
    SearchTask,
    TelemetryPacket,
)

from algorithms.allocation import allocate_search_tasks
from probability.bayesian import BayesianSearchMap
from simulation.drone import SearchDrone
from simulation.grid import SearchGrid


class SwarmSimulation:
    """Coordinate a multi-drone search-and-rescue simulation."""

    def __init__(
        self,
        cols: int = 40,
        rows: int = 40,
        num_drones: int = 5,
        seed: int = 42,
        p_detect: float = 0.8,
        failure_tick: int | None = None,
        dt: float = 1.0,
    ):
        if num_drones < 1 or num_drones > 10:
            raise ValueError("Number of drones must be between 1 and 10")

        if not (0.0 < p_detect < 1.0):
            raise ValueError("p_detect must be between 0 and 1")

        if failure_tick is not None and failure_tick < 1:
            raise ValueError("failure_tick must be positive")

        if dt <= 0:
            raise ValueError("dt must be greater than zero")

        self.cols = cols
        self.rows = rows
        self.num_drones = num_drones
        self.seed = seed
        self.p_detect = p_detect
        self.failure_tick = failure_tick
        self.dt = dt

        self.tick = 0
        self.mission_id = f"AEGIS-SAR-{seed}"

        self.grid = SearchGrid(cols, rows)
        self.probability_map = BayesianSearchMap(cols, rows)
        self.initial_probability = self.probability_map.probability.copy()

        drone_ids = [
            f"UAV-{number:02d}"
            for number in range(1, num_drones + 1)
        ]

        allocations = allocate_search_tasks(cols, rows, drone_ids)

        self.drones = {}
        self.task_queues = {}

        for drone_id in drone_ids:
            tasks = allocations[drone_id]

            # Start each drone at the first cell in its assigned sector.
            first_task = tasks[0]

            self.drones[drone_id] = SearchDrone(
                drone_id=drone_id,
                start_x=first_task.x,
                start_y=first_task.y,
            )

            self.task_queues[drone_id] = deque(tasks)

        self.event_log = []
        self.failover_events = []
        self.failed_drone_ids = set()

    def _reassign_tasks(self, failed_drone_id: str) -> None:
        """Redistribute unfinished tasks from a failed drone."""

        unfinished = list(self.task_queues[failed_drone_id])
        self.task_queues[failed_drone_id].clear()

        active_ids = [
            drone_id
            for drone_id, drone in self.drones.items()
            if drone_id != failed_drone_id
            and drone.state.status != DroneStatus.FAILED
        ]

        reassigned = {drone_id: [] for drone_id in active_ids}

        if not active_ids:
            self.event_log.append({
                "tick": self.tick,
                "type": "no_active_drones_for_reassignment",
                "failed_drone_id": failed_drone_id,
            })
            return

        for index, task in enumerate(unfinished):
            recipient_id = active_ids[index % len(active_ids)]

            reassigned_task = SearchTask(
                task_id=task.task_id,
                x=task.x,
                y=task.y,
                priority=task.priority,
                assigned_drone_id=recipient_id,
            )

            self.task_queues[recipient_id].append(reassigned_task)

            reassigned[recipient_id].append(
                (task.x, task.y)
            )

        event = FailoverEvent(
            event_id=f"FAILOVER-{len(self.failover_events) + 1:03d}",
            tick=self.tick,
            failed_drone_id=failed_drone_id,
            reassigned_cells={
                drone_id: cells
                for drone_id, cells in reassigned.items()
                if cells
            },
        )

        self.failover_events.append(event)

        self.event_log.append({
            "tick": self.tick,
            "type": "drone_failure",
            "failed_drone_id": failed_drone_id,
            "reassigned_cells": {
                drone_id: len(cells)
                for drone_id, cells in reassigned.items()
            },
        })

    def _apply_scheduled_failure(self) -> None:
        """Trigger the configured drone failure once."""

        if self.failure_tick != self.tick:
            return

        if not self.drones:
            return

        for drone_id, drone in self.drones.items():
            if drone.state.status != DroneStatus.FAILED:
                drone.fail()
                self.failed_drone_ids.add(drone_id)

                self._reassign_tasks(drone_id)
                break

    def step(self) -> TelemetryPacket:
        """Advance the mission by one simulation tick."""

        self.tick += 1

        for drone_id, drone in self.drones.items():
            if drone.state.status == DroneStatus.FAILED:
                continue

            if not self.task_queues[drone_id]:
                drone.return_to_idle()
                continue

            task = self.task_queues[drone_id][0]

            # Move one adjacent cell towards the assigned task.
            if (drone.state.x, drone.state.y) != (task.x, task.y):
                current_x = drone.state.x
                current_y = drone.state.y

                if current_x != task.x:
                    next_x = current_x + (
                        1 if task.x > current_x else -1
                    )
                    drone.move_to(next_x, current_y)
                else:
                    next_y = current_y + (
                        1 if task.y > current_y else -1
                    )
                    drone.move_to(current_x, next_y)

                continue

            # Record the search only after reaching the task cell.
            drone.start_search()

            self.grid.mark_searched(task.x, task.y)

            self.probability_map.update_after_search(
                task.x,
                task.y,
                p_detect=self.p_detect,
            )

            drone.completed_tasks += 1
            self.task_queues[drone_id].popleft()

        self._apply_scheduled_failure()

        return self.get_telemetry()

    def get_telemetry(self) -> TelemetryPacket:
        """Build a validated telemetry packet for the frontend."""

        drone_states = [
            DroneState.model_validate(drone.state.model_dump())
            for drone in self.drones.values()
        ]

        return TelemetryPacket(
            mission_id=self.mission_id,
            tick=self.tick,
            sim_time_s=self.tick * self.dt,
            grid_size=(self.cols, self.rows),
            drones=drone_states,
            probability_map=self.probability_map.to_list(),
            coverage_map=self.grid.to_list(),
            event_log=self.failover_events,
        )

    def run(self, max_ticks: int = 10000) -> list[TelemetryPacket]:
        """Run the simulation until all tasks finish or the limit is reached."""

        if max_ticks < 1:
            raise ValueError("max_ticks must be positive")

        history = []

        while self.tick < max_ticks:
            active_tasks = sum(
                len(queue)
                for drone_id, queue in self.task_queues.items()
                if self.drones[drone_id].state.status != DroneStatus.FAILED
            )

            if active_tasks == 0:
                break

            history.append(self.step())

        return history

    def probability_coverage(self, threshold: float = 0.9) -> float:
        """Measure original probability mass inside searched cells."""

        if not (0.0 <= threshold <= 1.0):
            raise ValueError("threshold must be between 0 and 1")

        searched = self.grid.coverage > 0

        covered_probability = self.initial_probability[searched].sum()

        return float(covered_probability)

    def summary(self) -> dict:
        """Return a compact summary of the mission."""

        total_cells = self.cols * self.rows
        searched_cells = int((self.grid.coverage > 0).sum())

        return {
            "mission_id": self.mission_id,
            "ticks": self.tick,
            "total_cells": total_cells,
            "searched_cells": searched_cells,
            "grid_coverage": searched_cells / total_cells,
            "probability_coverage": self.probability_coverage(),
            "failed_drones": sorted(self.failed_drone_ids),
            "completed_tasks": {
                drone_id: drone.completed_tasks
                for drone_id, drone in self.drones.items()
            },
        }
