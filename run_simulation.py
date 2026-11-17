
"""Main entry point for the AEGIS SAR simulation."""

import json
from pathlib import Path

from simulation.engine import SwarmSimulation


# Mission configuration
GRID_COLS = 40
GRID_ROWS = 40
NUM_DRONES = 5
RANDOM_SEED = 42
MAX_TICKS = 10000

# Output directory
OUTPUT_DIR = Path("outputs") / "simulation"


def main():
    """Run the mission and export its results."""

    print("=" * 55)
    print("       AEGIS SAR - MULTI-UAV SIMULATION")
    print("=" * 55)

    print("\nInitializing search mission...")

    simulation = SwarmSimulation(
        cols=GRID_COLS,
        rows=GRID_ROWS,
        num_drones=NUM_DRONES,
        seed=RANDOM_SEED,
    )

    print(f"Grid: {GRID_COLS} x {GRID_ROWS}")
    print(f"Drones: {NUM_DRONES}")
    print(f"Random seed: {RANDOM_SEED}")

    print("\nRunning simulation...")

    simulation.run(max_ticks=MAX_TICKS)

    # Collect final mission results.
    summary = simulation.summary()
    telemetry = simulation.get_telemetry()

    # Create the output directory.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Export final telemetry.
    telemetry_path = OUTPUT_DIR / "telemetry.json"

    with telemetry_path.open("w", encoding="utf-8") as file:
        json.dump(
            telemetry.model_dump(mode="json"),
            file,
            indent=2,
        )

    # Export mission summary.
    summary_path = OUTPUT_DIR / "mission_summary.json"

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    # Display mission results.
    print("\n" + "=" * 55)
    print("                 MISSION RESULTS")
    print("=" * 55)

    print(f"Mission ID: {summary['mission_id']}")
    print(f"Simulation ticks: {summary['ticks']}")
    print(f"Total search cells: {summary['total_cells']}")
    print(f"Searched cells: {summary['searched_cells']}")
    print(f"Grid coverage: {summary['grid_coverage']:.2%}")
    print(
        "Probability coverage: "
        f"{summary['probability_coverage']:.2%}"
    )

    print("\nCompleted tasks per drone:")

    for drone_id, count in summary["completed_tasks"].items():
        print(f"  {drone_id}: {count}")

    print(f"\nFailed drones: {summary['failed_drones']}")

    print("\nExported files:")
    print(f"  {telemetry_path}")
    print(f"  {summary_path}")

    print("\nSimulation completed.")


if __name__ == "__main__":
    main()
