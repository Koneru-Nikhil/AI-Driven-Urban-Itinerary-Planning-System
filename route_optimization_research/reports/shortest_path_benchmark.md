# Shortest-Path Algorithm Benchmark

## AI-Driven Personalized Urban Itinerary Planning System

---

## 1. Objective

The objective of this experiment is to evaluate the performance and scalability of different shortest-path algorithms on a large-scale Hyderabad road network extracted from OpenStreetMap (OSM).

The initial algorithms evaluated are:

1. Dijkstra's Algorithm
2. A* Search
3. Bidirectional Dijkstra

The algorithms are evaluated using multiple graph sizes ranging from 10,000 to 500,000 nodes.

The purpose of this experiment is to understand how different routing algorithms behave as the size of the road network increases and to identify suitable algorithms for the route-optimization component of the personalized urban itinerary planning system.

---

## 2. Dataset

The road network was extracted from OpenStreetMap data using PyOsmium.

The Hyderabad study area was approximately bounded by:

- Minimum longitude: 78.20
- Maximum longitude: 78.70
- Minimum latitude: 17.20
- Maximum latitude: 17.60

The extracted road network contained:

- 730,195 unique road nodes
- 833,954 road segments
- 1,578,661 directed edges

The largest weakly connected component contained:

- 727,986 nodes
- 1,574,570 directed edges

The experiments were performed on connected subsets of this road network.

---

## 3. Experimental Graph Sizes

Six graph sizes were used for the scalability experiment:

| Dataset | Nodes |
|---|---:|
| 10K | 10,000 |
| 25K | 25,000 |
| 50K | 50,000 |
| 100K | 100,000 |
| 250K | 250,000 |
| 500K | 500,000 |

Each subset was verified to contain one connected component when considering road connectivity.

The underlying road graph remains directed for shortest-path computation.

---

## 4. Algorithms

### 4.1 Dijkstra

Dijkstra's algorithm calculates the shortest path between a source and target node by progressively exploring the node with the smallest known distance.

It serves as the baseline algorithm for this experiment.

---

### 4.2 A*

A* extends the shortest-path search by using a heuristic to estimate the remaining distance to the target.

The implementation uses geographic coordinates and the Haversine distance as the heuristic.

The heuristic helps guide the search toward the destination rather than exploring the network uniformly.

---

### 4.3 Bidirectional Dijkstra

Bidirectional Dijkstra performs simultaneous shortest-path searches:

- Forward from the source
- Backward from the target

The searches meet at an intermediate node, reducing the search space in suitable cases.

A reverse graph is used for the backward search.

---

## 5. Experimental Setup

For every dataset:

- 30 reproducible source-target pairs were generated.
- The same random seed was used for reproducibility.
- Each source-target pair was evaluated using all three algorithms.
- Returned paths were independently validated.
- The actual distance of every returned path was recalculated from the graph edges.
- Algorithm-reported distances were compared against the actual path distances.

The following metrics were recorded:

1. Execution time
2. Number of nodes explored
3. Route distance
4. Path validity
5. Distance difference
6. Path-distance difference

---

## 6. Correctness Validation

For every returned route, the following conditions were checked:

- The path is non-empty.
- The path starts at the source node.
- The path ends at the target node.
- Every consecutive pair of nodes represents a valid directed graph edge.
- The distance obtained by summing the actual graph edges matches the reported route distance.

This prevents an algorithm from appearing faster because of an invalid or incomplete path.

---

# 7. Experimental Results

## 7.1 Execution Time

| Dataset | Dijkstra (ms) | A* (ms) | Bidirectional Dijkstra (ms) |
|---|---:|---:|---:|
| 10K | 8.501 | 5.733 | 7.724 |
| 25K | 20.486 | 11.359 | 17.822 |
| 50K | 41.376 | 19.836 | 36.644 |
| 100K | 81.588 | 36.132 | 69.693 |
| 250K | 193.347 | 77.083 | 165.638 |
| 500K | 857.960 | 316.022 | 673.684 |

The execution times represent the average over the valid common source-target routes for each dataset.

---

## 7.2 Nodes Explored

| Dataset | Dijkstra | A* | Bidirectional Dijkstra |
|---|---:|---:|---:|
| 10K | 4,691 | 1,457 | 3,216 |
| 25K | 16,187 | 4,712 | 10,667 |
| 50K | 24,633 | 6,656 | 16,642 |
| 100K | 56,844 | 14,733 | 37,191 |
| 250K | 126,987 | 29,358 | 84,797 |
| 500K | 297,772 | 65,199 | 190,300 |

The number of explored nodes was measured during each algorithm execution.

---

## 7.3 Speedup Relative to Dijkstra

| Dataset | A* Speedup | Bidirectional Dijkstra Speedup |
|---|---:|---:|
| 10K | 1.48x | 1.10x |
| 25K | 1.80x | 1.15x |
| 50K | 2.09x | 1.13x |
| 100K | 2.26x | 1.17x |
| 250K | 2.51x | 1.17x |
| 500K | 2.71x | 1.27x |

Speedup is calculated relative to the average Dijkstra execution time for the corresponding dataset.

---

## 7.4 Node Reduction

| Dataset | A* Node Reduction | Bidirectional Dijkstra Node Reduction |
|---|---:|---:|
| 10K | 68.95% | 31.45% |
| 25K | 70.89% | 34.10% |
| 50K | 72.98% | 32.44% |
| 100K | 74.08% | 34.57% |
| 250K | 76.88% | 33.22% |
| 500K | 78.10% | 36.09% |

Node reduction is calculated relative to the average number of nodes explored by Dijkstra.

---

# 8. Route Correctness

All three algorithms produced matching route distances in the completed benchmark datasets.

For the 500K experiment:

- Total route pairs: 30
- Valid common routes: 30
- Maximum distance difference: 0 km
- Maximum path-distance difference: 0 km

The same zero-distance-difference result was observed across the completed benchmark scales.

This indicates that the tested implementations produced equivalent shortest-path distances for the evaluated source-target pairs.

---

# 9. Observations

### Observation 1: A* explored substantially fewer nodes

A* consistently explored fewer nodes than Dijkstra.

The reduction increased from approximately 69% at 10K to approximately 78% at 500K.

---

### Observation 2: A* execution-time advantage increased with graph scale

The measured A* speedup relative to Dijkstra increased across the tested graph sizes.

At 500K nodes:

- Dijkstra: 857.960 ms
- A*: 316.022 ms
- A* speedup: 2.71x

---

### Observation 3: Bidirectional Dijkstra reduced search effort

Bidirectional Dijkstra explored fewer nodes than standard Dijkstra across the tested datasets.

At 500K nodes:

- Dijkstra: 297,772 nodes
- Bidirectional Dijkstra: 190,300 nodes
- Node reduction: 36.09%

---

### Observation 4: Route distance remained consistent

The tested algorithms produced the same average route distance for each benchmark scale.

The 500K experiment reported:

- Dijkstra: 21.364848 km
- A*: 21.364848 km
- Bidirectional Dijkstra: 21.364848 km

---

## 10. Scalability

The experiments demonstrate that graph size has a significant effect on shortest-path computation time.

The largest tested graph contained 500,000 nodes and more than one million directed edges.

At this scale, the measured average execution times were:

- Dijkstra: 857.960 ms
- A*: 316.022 ms
- Bidirectional Dijkstra: 673.684 ms

The experiment therefore provides a basis for evaluating more advanced routing techniques on the same road network.

---

# 11. Research Interpretation

The benchmark demonstrates that different shortest-path algorithms behave differently as the road network grows.

The results indicate that heuristic-guided search can reduce the number of nodes explored compared with the baseline Dijkstra search for the tested Hyderabad road network and source-target pairs.

However, the benchmark does not establish that one algorithm is universally optimal for every road network or every routing request.

Performance can depend on:

- Road-network structure
- Source-target location
- Geographic distance
- Graph density
- Directionality
- Search heuristic
- Hardware and runtime conditions

Therefore, additional algorithms and routing strategies should be evaluated before designing the final adaptive algorithm-selection component.

---

# 12. Limitations

The current experiment has several limitations:

1. The benchmark uses one geographic study area.
2. The experiments use 30 reproducible source-target pairs per dataset.
3. Execution times depend on the hardware and runtime environment.
4. The current benchmark focuses on shortest-path routing rather than the complete multi-POI itinerary optimization problem.
5. The connected subsets were constructed using connectivity of the road network; directed reachability can still depend on the selected source and target.
6. The current edge weight represents road-segment distance rather than live traffic travel time.
7. Only three shortest-path algorithms have been evaluated so far.

These limitations motivate further experimentation.

---

# 13. Reproducibility

The experiments use:

- Hyderabad OpenStreetMap road data
- PyOsmium for OSM extraction
- Python
- NetworkX
- Pandas
- A fixed random seed for source-target generation

The following files contain the benchmark implementations and datasets/results:

```text
route_optimization_research/
├── algorithms/
│   ├── shortest_path.py
│   └── bidirectional_dijkstra.py
│
├── experiments/
│   └── benchmark_shortest_path.py
│
├── results/
│   ├── shortest_path_10K_comparison.csv
│   ├── shortest_path_25K_comparison.csv
│   ├── shortest_path_50K_comparison.csv
│   ├── shortest_path_100K_comparison.csv
│   ├── shortest_path_250K_comparison.csv
│   └── shortest_path_500K_comparison.csv
│
└── reports/
    └── shortest_path_benchmark.md