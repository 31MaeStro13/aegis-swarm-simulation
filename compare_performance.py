
"""Compare one-drone and five-drone AEGIS SAR performance."""

from simulation.engine import SwarmSimulation


TARGET_COVERAGE = 0.90
MAX_TICKS = 10000
DRONE_COUNTS = [1, 5]


def run_experiment(num_drones: int) -> dict:
    """Run a mission until it reaches the target probability coverage."""

    simulation = SwarmSimulation(
        cols=40,
        rows=40,
        num_drones=num_drones,
        seed=42,
    )

    while (
        simulation.tick < MAX_TICKS
        and simulation.probability_coverage() < TARGET_COVERAGE
    ):
        simulation.step()

    coverage = simulation.probability_coverage()

    return {
        "drones": num_drones,
        "ticks": simulation.tick,
        "coverage": coverage,
        "reached_target": coverage >= TARGET_COVERAGE,
    }


def main():
    """Run and display both performance experiments."""

    print("=" * 55)
    print("       AEGIS SAR PERFORMANCE COMPARISON")
    print("=" * 55)

    results = {}

    for count in DRONE_COUNTS:
        result = run_experiment(count)
        results[count] = result

        print(
            f"\n{count} drone(s): "
            f"{result['ticks']} ticks | "
            f"{result['coverage']:.2%} probability coverage"
        )

        print(
            "90% target reached:",
            result["reached_target"],
        )

    if all(item["reached_target"] for item in results.values()):
        one_drone_ticks = results[1]["ticks"]
        five_drone_ticks = results[5]["ticks"]

        improvement = one_drone_ticks / five_drone_ticks
        time_saved = (
            (one_drone_ticks - five_drone_ticks)
            / one_drone_ticks
        ) * 100

        print("\n" + "=" * 55)
        print("                 COMPARISON")
        print("=" * 55)

        print(f"One drone:  {one_drone_ticks} ticks")
        print(f"Five drones: {five_drone_ticks} ticks")
        print(f"Speed improvement: {improvement:.2f}x")
        print(f"Reduction in ticks: {time_saved:.2f}%")

    else:
        print("\nThe 90% target was not reached in every experiment.")


if __name__ == "__main__":
    main()
