
"""Drone movement and state management for AEGIS SAR."""

from contracts.models import DroneState, DroneStatus, SearchTask


class SearchDrone:
    """Represent one simulated search-and-rescue drone."""

    def __init__(
        self,
        drone_id: str,
        start_x: int = 0,
        start_y: int = 0,
        battery: float = 100.0,
    ):
        self.state = DroneState(
            id=drone_id,
            x=start_x,
            y=start_y,
            battery=battery,
            status=DroneStatus.IDLE,
        )

        self.completed_tasks = 0

    def start_search(self) -> None:
        """Set the drone status to searching."""
        if self.state.status == DroneStatus.FAILED:
            raise RuntimeError("A failed drone cannot start searching")

        self.state.status = DroneStatus.SEARCHING

    def move_to(self, x: int, y: int) -> None:
        """Move one cell at a time using Manhattan movement."""
        if self.state.status == DroneStatus.FAILED:
            raise RuntimeError("A failed drone cannot move")

        if abs(x - self.state.x) + abs(y - self.state.y) != 1:
            raise ValueError("Drone can only move to an adjacent cell")

        if self.state.battery <= 0:
            raise RuntimeError("Drone battery is depleted")

        self.state.x = x
        self.state.y = y
        self.state.battery = max(0.0, self.state.battery - 0.01)
        self.state.status = DroneStatus.SEARCHING

    def execute_task(self, task: SearchTask) -> None:
        """Move to an assigned task and record its completion."""
        if task.assigned_drone_id != self.state.id:
            raise ValueError("This task belongs to another drone")

        self.start_search()

        while (self.state.x, self.state.y) != (task.x, task.y):
            current_x = self.state.x
            current_y = self.state.y

            if current_x != task.x:
                next_x = current_x + (1 if task.x > current_x else -1)
                self.move_to(next_x, current_y)
            else:
                next_y = current_y + (1 if task.y > current_y else -1)
                self.move_to(current_x, next_y)

        self.completed_tasks += 1

    def fail(self) -> None:
        """Mark the drone as failed."""
        self.state.status = DroneStatus.FAILED

    def return_to_idle(self) -> None:
        """Set a healthy drone back to idle."""
        if self.state.status != DroneStatus.FAILED:
            self.state.status = DroneStatus.IDLE
