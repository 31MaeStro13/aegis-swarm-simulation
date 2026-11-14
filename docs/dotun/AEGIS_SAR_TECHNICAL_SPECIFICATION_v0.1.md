# Aegis Technologies
# Autonomous Swarm UAV Coordination for Search and Rescue
## Technical Project Specification - Version 0.1 (For Review)

**Document status:** Draft for internal technical review; not approved for operational use  
**Version:** 0.1  
**Date:** 13 November 2026  
**Prepared for:** Oleg Irshko and the Aegis Technologies project team  
**Prepared by:** Oluwasomidotun Odumosu  
**Copyright:** © 2026 Aegis Technologies. All Rights Reserved.

---

## 1. Purpose of this document

This document defines the first software prototype of an autonomous multi-UAV search and rescue (SAR) coordination platform. It gives the team a shared description of the problem, first version scope, system behaviour, technical responsibilities, evaluation plan and acceptance criteria.

This is a **working specification for review**, not a final product specification, flight approval, safety case or claim of standards compliance. Oleg, as Systems Architect and Backend Lead, should approve the system boundaries and interfaces before they become team wide commitments.

## 2. Project vision and problem statement

Search teams may need to search large or difficult areas with limited time, aircraft, battery capacity, communications and incomplete information about a missing person's location.

The proposed platform will help an authorised search operator coordinate multiple UAVs by:
- dividing a search area into manageable cells or zones;
- assigning search tasks to available drones;
- maintaining a probability estimate of where the missing person may be;
- recording which cells have been searched and with what assumed detection capability;
- updating search priorities when new information or observations arrive; and
- reallocating unfinished tasks when a drone becomes unavailable.

**Core product idea:** a specialised multi-UAV search intelligence and coordination layer, not merely a drone monitoring dashboard and not a drone manufacturing program.

## 3. First milestone objective

**MVP 0.1 - Five-UAV Probabilistic Search and Dynamic Task Reallocation Simulator**

Build a reproducible 2D Python simulation with 5 abstract drones. The simulation must demonstrate:
1. a defined 2D search area represented as a grid;
2. 5 drones with position, status, battery and assigned work;
3. initial search-area allocation;
4. a probability distribution over possible target locations;
5. drone movement and cell-search events;
6. probability updates after search observations;
7. failure or unavailability of one drone during a mission;
8. reassignment of its unfinished tasks to the remaining active drones; and
9. quantitative evaluation and visualisation of the mission.

The first milestone is an algorithm and software prototype. It does **not** control real aircraft.

## 4. Scope

### 4.1 In scope for MVP 0.1
- A 40 × 40 grid as an initial configurable test environment.
- 5 simulated drones (configurable in code).
- Abstract 2D movement between cell centres.
- Grid-based zone allocation as the baseline.
- A target location hidden from the search policy but retained by the simulator for evaluation.
- A normalised prior probability map over grid cells.
- A separate searched/coverage map.
- A configurable detection probability for a searched cell.
- Bayesian-style probability updates after detection/non-detection.
- Battery consumption using a simple documented model.
- A simulated drone failure event.
- Dynamic reassignment of unfinished tasks.
- Fixed-seed repeatable experiments.
- Plots, metrics, logs and automated tests.

### 4.2 Out of scope for MVP 0.1
- Real drone flight, hardware-in-the-loop or live mission control.
- Real-time flight control commands.
- Certified collision avoidance, detect and avoid or airspace separation.
- Real forest terrain, weather, RF propagation or sensor physics.
- Production desktop dashboard.
- Integration with PX4, ROS 2, Gazebo, MAVLink or a live drone fleet.
- Reinforcement learning.
- Use of real missing person records, identifiable imagery or sensitive LizaAlert data.
- Claims that the prototype is ready for operational rescue deployment.

These may be considered in later phases after technical review, user research and safety assessment.

## 5. Users and operational assumptions

### 5.1 Intended user (initial concept)
An authorised search coordinator or mission planner who defines the search area, reviews available information, monitors simulated drone tasks and approves or evaluates task changes.

### 5.2 Initial modelling assumptions
- The search area is a bounded 2D rectangle.
- It is discretised into square cells.
- Five identical abstract drones start at configured positions.
- Each drone can search one cell at a time.
- A drone has a finite battery budget.
- A cell can be searched more than once, but repeated effort is recorded.
- The target is stationary during MVP 0.1.
- Search detection is probabilistic, not guaranteed.
- A failure event makes a drone unavailable; the first version does not model why it failed.
- All parameters are synthetic and clearly identified as assumptions.

The assumptions must be revisited after operational feedback from rescue practitioners. They must not be presented as facts about LizaAlert or any other rescue organisation.

## 6. Core concepts and data separation

The simulation must keep the following concepts separate:

1. **Target-location probability:** the model's current estimate that the target is in each cell. The values across all cells must sum to 1, within numerical tolerance.
2. **Search coverage:** whether a cell has been visited/searched.
3. **Detection capability:** the assumed probability of detecting the target if it is present in a particular cell during a search.
4. **Drone state:** each drone's position, battery, status and assigned tasks.
5. **Ground truth:** the simulator only target location, used to calculate evaluation results. It must not be exposed to the search allocation algorithm as an input.

A high search coverage percentage is not the same as a high probability of finding the target.

## 7. Functional requirements

| ID | Requirement | MVP 0.1 acceptance condition |
|---|---|---|
| FR-01 | Create search grid | Configurable grid is created with valid dimensions. |
| FR-02 | Initialise drones | Exactly five drones are created by default with unique IDs and valid starting positions. |
| FR-03 | Allocate cells | Every searchable cell is assigned or explicitly marked unassigned; no invalid cell indices. |
| FR-04 | Initialise probability map | All probabilities are finite, non-negative and sum to 1 within tolerance. |
| FR-05 | Move drones | Active drones move according to valid routes and remain within the grid. |
| FR-06 | Record search | Search events update coverage and mission logs. |
| FR-07 | Update probability | Non-detection updates probability using the configured detection model and renormalises the map. |
| FR-08 | Simulate detection | Detection is sampled using a documented probability model; ground truth is not leaked to the planner. |
| FR-09 | Track battery | Battery decreases according to a documented movement/search cost model and cannot become negative. |
| FR-10 | Simulate failure | A selected drone can transition from active to failed/unavailable during a mission. |
| FR-11 | Reallocate tasks | Unfinished tasks of a failed drone are reassigned to eligible active drones, or explicitly left unassigned if infeasible. |
| FR-12 | Log decisions | Allocation, movement, search, battery, detection, failure and reassignment events are recorded. |
| FR-13 | Evaluate mission | The system calculates the metrics in Section 11. |
| FR-14 | Reproduce runs | A configured random seed reproduces the same stochastic run. |
| FR-15 | Visualise | The run can display drone positions, assignments, searched cells and target-probability heatmap as separate layers. |

### 7.1 Non-functional requirements and proposed MVP targets

These are project-defined simulator targets, not limits imposed by the standards.

| ID | Quality area | Proposed measurable target | Verification |
|---|---|---|---|
| NFR-01 | Performance | 40 × 40 grid, five drones and 1,000 ticks complete in ≤5 seconds on an agreed reference machine. | Timed benchmark; record machine/software versions. |
| NFR-02 | Probability integrity | All updates are finite, non-negative and sum to 1 within 1e-9. | Automated tests. |
| NFR-03 | Reproducibility | Same configuration and seed produce identical logs, metrics and final state. | Repeat-run comparison. |
| NFR-04 | Reliability | All required tests pass with no unhandled exception in acceptance scenarios. | Test/CI report. |
| NFR-05 | Maintainability | Simulation, allocation, probability and evaluation remain separate documented modules. | Code review. |
| NFR-06 | Observability | Every search, detection, failure and reassignment event records tick/time and entity/task/cell IDs. | Log-schema validation. |
| NFR-07 | Data protection | Synthetic target and sensor data only; no identifiable rescue data in MVP. | Dataset/repository review. |
| NFR-08 | Results | Each run exports a CSV or JSON summary and required plots. | Output check. |


## 8. Mathematical model - initial baseline

### 8.1 Search grid
Let the search area be a set of cells:

$$
\mathcal{C} = \{c_1, c_2, \ldots, c_N\}
$$

For the initial 40 × 40 grid, \(N=1600\).


### 8.2 Drones

Let:

$$
\mathcal{U} = \{u_1,u_2,u_3,u_4,u_5\}
$$

Each drone has position \(x_k\), battery \(b_k\), status \(s_k\), and a set of assigned tasks \(A_k\).


### 8.3 Prior Target-Location Probability

For each cell \(i\), define \(P_i\), where:

$$
P_i \geq 0,\qquad \sum_{i=1}^{N} P_i = 1
$$

MVP 0.1 may initialise this map with a synthetic distribution centred on a configurable last-known location. The prior-generation method and parameters must be documented.

### 8.4 Detection and Non-Detection Update

Let \(q_i\) be the assumed probability of detecting the target when cell \(i\) is searched and the target is present there.

After searching cell \(i\) and observing no detection, the likelihood of that observation is \(1-q_i\) if the target is in cell \(i\), and 1 for every other cell.

The posterior is therefore:

$$
P_j' =
\begin{cases}
\displaystyle \frac{P_i(1-q_i)}{1-P_iq_i}, & j=i, \\
\displaystyle \frac{P_j}{1-P_iq_i}, & j\ne i.
\end{cases}
$$

The denominator is the probability of observing no detection, \(1-P_iq_i\).

**Only the searched cell receives the non-detection likelihood penalty.** Other cells retain their relative probability ratios and are adjusted only by normalisation.

This assumes one stationary target, mutually exclusive target location cells, and a cell-specific detection probability. The implementation must safely handle a zero or near-zero denominator, reject invalid detection probabilities, and test that the posterior is finite, non-negative and normalised.

For a positive detection, MVP 0.1 may record a detection event and terminate the mission as a simulated find. More detailed sensor likelihood models are deferred.

### 8.5 Baseline allocation
Use a simple deterministic grid partition as the first allocation method. The partition should balance cell counts as evenly as possible and be reproducible. Voronoi and Particle Swarm Optimisation (PSO) are comparison methods for later increments, not prerequisites for the first working run.

### 8.6 Movement and battery
Use a simple, explicit movement model (for example, one grid step per simulation tick). Define movement and search energy costs as configurable synthetic parameters. Do not describe these values as real aircraft battery performance.

### 8.7 Failure and task reallocation
When a drone fails:
- change its status to `FAILED`;
- stop issuing it new movement or search tasks;
- identify its unfinished tasks;
- determine which active drones are eligible to receive them;
- assign tasks using a transparent baseline rule (for example, nearest active drone with sufficient remaining simulated battery);\n- check that reassignment respects the receiving drone’s remaining simulated battery and does not duplicate active tasks;\n- preserve task IDs and record old owner, new owner, reason and simulation tick;
- record tasks that cannot be reassigned; and
- continue the mission with the remaining drones.

The system must never silently discard unfinished tasks.

## 9. Proposed software architecture

Keep the first version modular and independent of flight hardware.

| Module | Responsibility |
|---|---|
| `simulation/environment.py` | Grid dimensions, cell state and environment configuration |
| `simulation/drone.py` | Drone state, movement, battery and availability |
| `simulation/mission.py` | Mission lifecycle, simulation clock and event orchestration |
| `simulation/search_area.py` | Cell indexing, neighbours and spatial helpers |
| `algorithms/grid_allocation.py` | Initial deterministic zone assignment |
| `algorithms/voronoi.py` | Later allocation comparison |
| `algorithms/pso.py` | Later optimisation experiment |
| `algorithms/path_planning.py` | Baseline route generation and later route alternatives |
| `probability/heatmap.py` | Prior probability-map creation and validation |
| `probability/bayesian_update.py` | Probability updates after observations |
| `evaluation/metrics.py` | Coverage, detection, time, battery, overlap and reallocation metrics |
| `evaluation/experiments.py` | Repeatable scenarios and multi-run comparisons |
| `visualisation/plots.py` | Map, routes, probability and coverage plots |
| `main.py` | Configuration and execution entry point |
| `tests/` | Unit and integration tests |

### 9.1 Initial technology choices
- Python 3.x (team to agree a supported version).
- NumPy for arrays and numerical calculations.
- SciPy where useful for spatial or optimisation routines.
- Matplotlib for initial visualisation.
- Pandas for experiment tables and result summaries.
- pytest for automated tests.
- Git for version control.

Do not introduce ROS 2, PX4 or Gazebo into MVP 0.1. PX4's multi-vehicle simulation documentation provides a later route for progressing from an abstract model to simulated vehicles.

## 10. Proposed team responsibilities

These are proposed workstream boundaries for Oleg's confirmation. They do not override anyone's agreed project title.

| Contributor | Proposed workstream | Main deliverables |
|---|---|---|
| Oleg Irshko | Product owner, systems architecture and backend lead | Product scope, architecture approval, integration contracts, backend direction, priorities and review decisions |
| Anastasia Prudnikova | Systems and high-performance core engineering | Review computational boundaries, advise on performance critical design, core implementation/integration when required |
| Oluwasomidotun Odumosu | Search modelling, swarm algorithms and simulation experiments | Problem formulation, probability model, baseline allocation, task reallocation logic, Python prototype, metrics, experiment report |
| Nikita Gritsynin | Desktop UI and frontend engineering | Later desktop application, mission/map visualisation integration and operator-facing presentation |
| Taisiya Golets | Product and UI/UX design | User journeys, operator workflows, wireframes, usability requirements and visual design guidance |

### 10.1 Responsibility boundary for Oluwasomidotun Odumosu
**Accountable for delivering the modelling and algorithm prototype**, including:
- defining and documenting modelling assumptions;
- implementing and testing the target location probability map;
- implementing the baseline grid allocation;
- implementing the simulated drone and search-task logic in coordination with the agreed architecture;
- implementing the failure and task-reallocation experiment;
- defining and calculating evaluation metrics;
- documenting limitations, results and reproducible experiment settings.

**Not independently responsible for:**
- approving the overall product architecture;
- defining production backend APIs or database architecture;
- implementing the desktop frontend or visual design;
- writing flight-controller firmware or controlling real aircraft;
- approving aviation safety, operational deployment or regulatory compliance;
- making product or commercial commitments on behalf of Aegis Technologies.

Interfaces and shared modules must be agreed with Oleg and Anastasia before implementation overlaps occur.

## 11. Evaluation plan

Run comparable experiments with identical grid, starting positions, target prior, detection assumptions and random seeds.

### Required initial scenarios
- **Scenario A - Normal mission:** five drones search with the baseline allocation.
- **Scenario B - Drone failure:** one drone fails part-way through the mission; unfinished tasks are reassigned.
- **Scenario C - No reallocation baseline:** one drone fails, but its tasks remain unassigned. This provides a comparison for the benefit of reallocation.

### Required metrics
- **Search coverage (%):** unique searched cells divided by total searchable cells.
- **Detection outcome / simulated detection probability:** report actual simulated finds separately from model-estimated probability. Do not present an estimated probability as a guaranteed real-world success rate.
- **Mission duration:** simulation ticks or modelled time to the stopping condition.
- **Battery consumption:** simulated energy consumed per drone and in total.
- **Duplicate coverage (%):** repeated cell visits divided by all cell visits, with the exact formula stated.
- **Reallocation time:** simulation ticks between failure detection and completion of reassignment.
- **Unassigned workload:** number of unfinished tasks not reassigned.

**Use multiple random seeds for stochastic comparisons.** Report mean and spread (for example, standard deviation or confidence interval) when enough runs are available. A single illustrative run is not sufficient evidence of algorithm superiority.

## 12. Testing and acceptance

### Unit tests
- Grid indexing and boundary handling.
- Unique drone identifiers and valid initial states.
- Probability values are finite, non-negative and normalised.
- Bayesian non-detection applies the likelihood penalty only to the searched cell; unsearched cells preserve relative probability ratios.\n- Test q=0, q=1, near-zero denominator, invalid q and normalisation.
- Battery never becomes negative.
- Failed drones receive no new tasks.
- Reallocation does not duplicate or silently lose task identifiers.
- No drone moves outside the grid.

### Integration tests
- A complete 5 drone mission runs from initialisation to a stopping condition.
- A mid-mission failure triggers reassignment.
- The mission continues with the remaining active drones.
- Event logs and metrics are produced.
- A fixed seed produces repeatable results.\n- Reassignment preserves task IDs, avoids duplicate active assignments and respects simulated battery feasibility.\n- NFR-01 benchmark and required log/export checks pass.

### MVP 0.1 acceptance gate
The milestone is ready for Oleg's demonstration/review when:
1. the prototype runs from documented setup instructions;
2. five drones appear and move in the 2D environment;
3. the probability and coverage layers are displayed separately;
4. a non-detection updates the probability map correctly;
5. a drone failure is detected by the simulation;
6. unfinished tasks are reassigned or explicitly marked infeasible;
7. the mission continues after failure;
8. key metrics and event logs are generated;
9. automated tests pass; and
10. limitations and assumptions are documented.

No claim of real world rescue effectiveness is made at this gate.

## 13. Development stages and review gates

| Stage | Work | Reviewable output |
|---|---|---|
| 0 – Specification and setup | Review this document, agree interfaces, create repository and environment | Approved v0.1 scope and runnable project skeleton |
| 1 – Environment | Grid, five drone objects, states and visualisation | 5-drone 2D map |
| 2 – Baseline search | Grid allocation, movement, search events and coverage | Drones search assigned zones |
| 3 – Probability | Prior heatmap, detection assumptions and Bayesian updates | Separate probability and coverage maps |
| 4 – Failure recovery | Failure event, task reassignment and continuation | Demonstration of one drone dropping out |
| 5 – Evaluation | Scenarios, repeated runs, metrics, tests and report | Comparison tables, plots and technical report |
| 6 – Architecture review | Team review of algorithm boundaries and integration needs | Decision on next simulation/product increment |

## 14. Risks, safety and responsible use

The prototype is not an operational flight system. Before any real world trial, the team will need a separate safety and regulatory workstream covering at least:
- aircraft and operator permissions in the relevant jurisdiction;
- airspace restrictions and separation from crewed aircraft;
- command and control loss and contingency procedures;
- collision avoidance and geofencing;
- GNSS degradation and navigation uncertainty;
- weather, visibility and sensor limitations;
- battery reserve and safe return/landing behaviour;
- human supervision, override and mission abort;
- privacy, data minimisation, access control and retention;
- field validation and documented operational procedures.

**Do not ingest real missing person information, identifiable imagery or rescue team operational data without explicit permission and an agreed data protection process.**

**Proposed first technical demonstration:** a 5 drone search in a 40 × 40 grid, with separate coverage and target probability maps, followed by one simulated drone failure and reassignment of its unfinished tasks.

---


## 15. Standards, regulations and applicability

### 15.1 Compliance status

These references form a review baseline; their inclusion does **not** mean MVP 0.1
complies with, is certified under, or is approved by any standard or aviation authority.
The current milestone is software-only simulation. Obtain and review complete official
texts, assess applicability to the aircraft, operation, operator and jurisdiction, and
maintain a compliance matrix before real-world trials. Standards may be voluntary unless
incorporated into law, contract, certification or approval conditions.

### 15.2 International Standards

| Reference | Subject | Project relevance |
|---|---|---|
| ISO 21384-3:2026, Edition 3 | Uncrewed aircraft systems - Part 3: Operational procedures. | Later operational procedures, fleet roles, safety and C2 arrangements; not an approval or substitute for local law. |
| ISO/IEC/IEEE 29148:2018 | Systems and software engineering - Requirements engineering. | Requirements definition, traceability, validation and management. ISO reports this edition confirmed in 2024; revision work is underway. |
| ISO/IEC 25010:2023 | Systems and software engineering - SQuaRE - Product quality model. | Organises software quality requirements and evaluation. NFR targets here are project defined, not thresholds mandated by the standard. |

### 15.3 Russian National Standards

| Reference | Subject / scope summary | Applicability note |
|---|---|---|
| ГОСТ Р 56122-2026 | Беспилотные авиационные системы. Общие требования. | General requirements for civil UAS, including aircraft and remote-control station. Rosstandart lists it as effective 30 October 2026. |
| ГОСТ Р 59519-2026 | Беспилотные авиационные системы. Элементы беспилотных авиационных систем. Спецификация и общие требования. | Relevant to UAS composition/specification and element requirements. Effective 30 October 2026 per Rosstandart. |
| ГОСТ Р 72692-2026 | Беспилотные авиационные системы. Общие требования к системам информационного обеспечения беспилотных воздушных судов, не получающих диспетчерского обслуживания по эшелонированию. | Potentially relevant to future information-support functions. Check operation against the standard's scope; not automatically applicable to a 2D simulator. Effective 15 August 2026 per Rosstandart. |

### 15.4 Russian aviation regulations to assess

- **Government Resolution No. 138 of 11 March 2010**, Federal Rules for the Use of
  Airspace of the Russian Federation, using the current amended text. The legal reference
  checked identifies an amendment dated 29 September 2026 and a stated validity limit
  of 1 September 2027. Verify the official current text before any Russian operation.
- **Government Resolution No. 658 of 25 May 2019**, on state accounting of specified
  civil unmanned aircraft. The consolidated legal reference checked is amended through
  2 February 2026 and covers specified aircraft in the 0.15 kg to 30 kg MTOM range.
  Actual obligations depend on the aircraft and applicable rules.

These references are Russia specific and do not grant permission to operate elsewhere. Assess the relevant national aviation authority and local rules separately.

### 15.5 Compliance work before real-world operation

Create a compliance matrix listing the reference and exact clause, applicability rationale,
affected component, evidence required, responsible owner and verification/approval status.
Have the systems architect and a qualified aviation/regulatory specialist review it.
Do not claim compliance merely because a standard is listed.

## 16. Simulation-to-real-world boundary and safety gates

The MVP is an abstract software simulation. A successful run demonstrates only that the
implemented model behaves under its assumptions. It does not prove aircraft controllability,
sensor performance, collision avoidance, safe separation, radio reliability, battery endurance,
environmental robustness or rescue effectiveness.

Progression must be gated:

1. **MVP simulation:** synthetic data, abstract movement, simulated battery and failure.
2. **Higher-fidelity simulation:** documented sensor, environment, communications and
   vehicle models; scenario-based verification and independent review.
3. **Controlled software/hardware integration:** interface tests, fault injection,
   emergency-stop and loss-of-link behaviour, without public operation.
4. **Controlled field testing:** only after risk assessment, required approvals, operating
   permissions, trained personnel and emergency procedures.
5. **Operational use:** only after relevant authority/operator approvals, validated
   procedures, safety case and human supervision arrangements.

Define go/no-go criteria for each phase. A failed or uncertain safety check must lead to a
safe stop or hold, not automatic expansion of autonomy. A human operator must retain
authority to pause, abort or override a mission. This specification does not define certified
detect and avoid, airspace deconfliction or autonomous flight safety logic.

## 17. Reference sources checked for this revision

Official or legal reference pages checked on 13 November 2026. Their summaries establish
publication/status metadata and scope only; they do not replace the complete texts.

- Rosstandart, ГОСТ Р 56122-2026: https://protect.gost.ru/gost/details/cb02233c-303f-4e93-8f85-2fd3c827b538
- Rosstandart, ГОСТ Р 59519-2026: https://protect.gost.ru/gost/details/aecd38a2-9114-406b-8b55-41f87d4f9a69
- Rosstandart, ГОСТ Р 72692-2026: https://protect.gost.ru/gost/details/65aac09d-74a4-49bc-a66c-3e419afa8f67
- ISO, ISO 21384-3:2026: https://www.iso.org/standard/88660.html
- ISO, ISO/IEC/IEEE 29148:2018: https://www.iso.org/standard/72089.html
- ISO, ISO/IEC 25010:2023: https://www.iso.org/standard/78176.html
- ConsultantPlus, Government Resolution No. 138: https://www.consultant.ru/document/cons_doc_LAW_98957/
- ConsultantPlus, Government Resolution No. 658: https://www.consultant.ru/document/cons_doc_LAW_325695/c3eafa459077d1c774c0c59cad2b59c/

---

**End - Version 0.1**

