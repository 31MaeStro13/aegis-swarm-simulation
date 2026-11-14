# Aegis SAR Swarm: Autonomous Multi-UAV Search & Rescue Coordination

Autonomous multi-UAV coordination platform designed for wilderness Search and Rescue (SAR) missions.

## Architecture & Vision
Aegis SAR provides an intelligent coordination layer for a swarm of small UAVs to search large forest and wetland areas under tree canopies. It maintains a Bayesian target probability heatmap, dynamically partitions search areas, tracks battery reserves, and autonomously reallocates unfinished tasks if any drone becomes unavailable.

## Quickstart (via `uv`)

```bash
# Clone the repository
git clone git@github.com:31MaeStro13/aegis-swarm-simulation.git
cd aegis-swarm-simulation

# Run tests
uv run pytest

# Run the 2D simulation entry point
uv run python main.py
```

## Project Structure
- `simulation/`: Grid environment, cell models, drone states, and mission ticks.
- `algorithms/`: Initial grid partitioning and dynamic failure reallocation.
- `probability/`: Prior LKP generation and Bayesian non-detection updates.
- `evaluation/`: Metrics (coverage, time, battery) and experiment scenarios.
- `visualisation/`: Matplotlib plotting of heatmaps, routes, and searched zones.
- `crates/aegis_sar_core/`: High-performance Rust core (MAVLink telemetry, SITL).
- `docs/`: Technical specifications and workstream documentation for team members.
