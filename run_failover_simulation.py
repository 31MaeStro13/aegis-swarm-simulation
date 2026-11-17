
"""Run and export an AEGIS SAR mission with drone failure recovery."""

import json
from pathlib import Path

from simulation.engine import SwarmSimulation


OUTPUT_DIR = Path("outputs") / "failover"


def main():
    """Run a five-drone mission and export its recovery results."""

    print("=" * 55)
    print("       AEGIS SAR - FAILOVER MISSION")
    print("=" * 55)

    simulation = SwarmSimulation(
        cols=40,
        rows=40,
        num_drones=5,
        seed=42,
        failure_tick=2,
    )

    print("\nMission configuration:")
    print("Grid: 40 x 40")
    print("Initial drones: 5")
    print("Scheduled failure: tick 2")
    print("Random seed: 42")

    print("\nRunning mission...")
    simulation.run(max_ticks=10000)

    summary = simulation.summary()
    telemetry = simulation.get_telemetry()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    telemetry_path = OUTPUT_DIR / "failover_telemetry.json"
    summary_path = OUTPUT_DIR / "failover_summary.json"

    with telemetry_path.open("w", encoding="utf-8") as file:
        json.dump(
            telemetry.model_dump(mode="json"),
            file,
            indent=2,
        )

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    print("\nMission results:")
    print(f"Simulation ticks: {summary['ticks']}")
    print(f"Grid coverage: {summary['grid_coverage']:.2%}")
    print(
        "Probability coverage: "
        f"{summary['probability_coverage']:.2%}"
    )
    print(f"Failed drones: {summary['failed_drones']}")

    print("\nCompleted tasks per drone:")
    for drone_id, count in summary["completed_tasks"].items():
        print(f"  {drone_id}: {count}")

    print(f"\nFailover events: {len(telemetry.event_log)}")

    print("\nExported files:")
    print(f"  {telemetry_path}")
    print(f"  {summary_path}")

    print("\nFailover mission export completed.")


if __name__ == "__main__":
    main()
