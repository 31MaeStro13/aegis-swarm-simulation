
"""Contiguous-sector search allocation for the AEGIS SAR swarm."""

from contracts.models import SearchTask


def allocate_search_tasks(
    cols: int,
    rows: int,
    drone_ids: list[str],
) -> dict[str, list[SearchTask]]:
    """Divide the grid into balanced horizontal sectors.

    Each drone receives a contiguous group of rows.
    Cells within each row follow a serpentine search order.
    Every cell is assigned exactly once.
    """
    if not isinstance(cols, int) or isinstance(cols, bool) or cols <= 0:
        raise ValueError("cols must be a positive integer")

    if not isinstance(rows, int) or isinstance(rows, bool) or rows <= 0:
        raise ValueError("rows must be a positive integer")

    if not drone_ids:
        raise ValueError("At least one drone is required")

    if any(not isinstance(drone_id, str) or not drone_id for drone_id in drone_ids):
        raise ValueError("Drone IDs must be non-empty strings")

    if len(set(drone_ids)) != len(drone_ids):
        raise ValueError("Drone IDs must be unique")

    assignments = {drone_id: [] for drone_id in drone_ids}

    total_cells = cols * rows

    for y in range(rows):
        # Assign each complete row to one drone.
        drone_index = min(
            (y * len(drone_ids)) // rows,
            len(drone_ids) - 1,
        )
        drone_id = drone_ids[drone_index]

        # Alternate direction on each row to create a serpentine path.
        x_positions = range(cols) if y % 2 == 0 else range(cols - 1, -1, -1)

        for x in x_positions:
            cell_index = y * cols + x
            priority = 1.0 - (cell_index / max(total_cells - 1, 1))

            task = SearchTask(
                task_id=f"cell-{x}-{y}",
                x=x,
                y=y,
                priority=priority,
                assigned_drone_id=drone_id,
            )

            assignments[drone_id].append(task)

    return assignments
