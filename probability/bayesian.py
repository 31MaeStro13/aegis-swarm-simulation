
"""Bayesian probability mapping for the AEGIS SAR simulator."""

import numpy as np
from scipy.ndimage import gaussian_filter


class BayesianSearchMap:
    """Maintain and update the probability of a target's location."""

    def __init__(
        self,
        cols: int = 40,
        rows: int = 40,
        lkp_x: float = 20.0,
        lkp_y: float = 20.0,
        sigma: float = 6.0,
    ):
        if cols <= 0 or rows <= 0:
            raise ValueError("Grid dimensions must be positive")

        if sigma <= 0:
            raise ValueError("sigma must be greater than zero")

        if not (0 <= lkp_x < cols and 0 <= lkp_y < rows):
            raise ValueError("LKP must be inside the grid")

        self.cols = cols
        self.rows = rows

        x = np.arange(cols)
        y = np.arange(rows)
        xx, yy = np.meshgrid(x, y)

        # Create a Gaussian prior centred on the LKP.
        self.probability = np.exp(
            -(
                (xx - lkp_x) ** 2
                + (yy - lkp_y) ** 2
            ) / (2 * sigma**2)
        )

        self._normalize()

    def _normalize(self) -> None:
        """Make all probabilities sum to one."""
        total = self.probability.sum()

        if not np.isfinite(total) or total <= 0:
            raise ValueError("Probability map cannot be normalized")

        self.probability /= total

    def update_after_search(
        self,
        x: int,
        y: int,
        p_detect: float = 0.8,
        search_radius: int = 0,
    ) -> None:
        """Update probabilities after an unsuccessful search.

        Cells within the search area receive likelihood (1 - p_detect).
        Cells outside it retain likelihood 1.
        """
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            raise ValueError("Search coordinate is outside the grid")

        if not (0.0 < p_detect < 1.0):
            raise ValueError("p_detect must be between 0 and 1")

        if not isinstance(search_radius, int) or search_radius < 0:
            raise ValueError("search_radius must be a non-negative integer")

        y_min = max(0, y - search_radius)
        y_max = min(self.rows, y + search_radius + 1)
        x_min = max(0, x - search_radius)
        x_max = min(self.cols, x + search_radius + 1)

        self.probability[y_min:y_max, x_min:x_max] *= (1.0 - p_detect)
        self._normalize()

    def smooth(self, sigma: float = 1.0) -> None:
        """Smooth the probability distribution and renormalize it."""
        if sigma < 0:
            raise ValueError("sigma cannot be negative")

        self.probability = gaussian_filter(
            self.probability,
            sigma=sigma,
            mode="nearest",
        )
        self._normalize()

    def to_list(self) -> list[list[float]]:
        """Return a JSON-friendly probability matrix."""
        return self.probability.tolist()

    def total_probability(self) -> float:
        """Return the sum of all cell probabilities."""
        return float(self.probability.sum())
