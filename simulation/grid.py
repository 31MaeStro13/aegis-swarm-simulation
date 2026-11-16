
"""Grid management for the AEGIS SAR search simulation."""

import numpy as np


class SearchGrid:
    """Represent a 2D search area and track cell coverage."""

    def __init__(self, cols: int = 40, rows: int = 40):
        if not isinstance(cols, int) or isinstance(cols, bool) or cols <= 0:
            raise ValueError("cols must be a positive integer")

        if not isinstance(rows, int) or isinstance(rows, bool) or rows <= 0:
            raise ValueError("rows must be a positive integer")

        self.cols = cols
        self.rows = rows

        # Array shape is (rows, cols), indexed as [y, x].
        self.coverage = np.zeros((rows, cols), dtype=np.int64)

    @property
    def grid_size(self) -> list[int]:
        """Return grid dimensions as [columns, rows]."""
        return [self.cols, self.rows]

    def is_in_bounds(self, x: int, y: int) -> bool:
        """Check whether a coordinate belongs to the grid."""
        return 0 <= x < self.cols and 0 <= y < self.rows

    def mark_searched(self, x: int, y: int) -> None:
        """Record one search visit to a cell."""
        if not self.is_in_bounds(x, y):
            raise ValueError(f"Cell ({x}, {y}) is outside the grid")

        self.coverage[y, x] += 1

    def get_coverage(self, x: int, y: int) -> int:
        """Return the number of searches recorded for a cell."""
        if not self.is_in_bounds(x, y):
            raise ValueError(f"Cell ({x}, {y}) is outside the grid")

        return int(self.coverage[y, x])

    def reset(self) -> None:
        """Clear all recorded search visits."""
        self.coverage.fill(0)

    def to_list(self) -> list[list[int]]:
        """Convert coverage data into JSON-friendly Python lists."""
        return self.coverage.tolist()
