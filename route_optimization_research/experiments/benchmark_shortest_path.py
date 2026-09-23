import csv
import os
import random
import sys
import time
from collections import defaultdict

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

sys.path.insert(0, PROJECT_ROOT)

from route_optimization_research.algorithms.shortest_path import (
    dijkstra,
    astar
)

from route_optimization_research.algorithms.bidirectional_dijkstra import (
    bidirectional_dijkstra
)


# ============================================================
# CONFIGURATION
# ============================================================

SIZE = "500K"

NUM_PAIRS = 30

RANDOM_SEED = 42

DATA_DIR = r"C:\Users\nikhi\Downloads\Hyderabad_Route_Research\connected_subsets"

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "route_optimization_research",
    "results"
)

os.makedirs(RESULTS_DIR, exist_ok=True)


# ============================================================
# FILES
# ============================================================

nodes_file = os.path.join(
    DATA_DIR,
    f"Hyderabad_{SIZE}_Nodes.csv"
)

edges_file = os.path.join(
    DATA_DIR,
    f"Hyderabad_{SIZE}_Edges.csv"
)

results_file = os.path.join(
    RESULTS_DIR,
    f"shortest_path_{SIZE}_comparison.csv"
)


# ============================================================
# LOAD NODES
# ============================================================

print("=" * 70)
print("HYDERABAD SHORTEST-PATH ALGORITHM BENCHMARK")
print("=" * 70)

print(f"Dataset: {SIZE}")

print("Loading nodes...")

nodes = {}

with open(nodes_file, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    for row in reader:

        node_id = int(row["node_id"])

        nodes[node_id] = (
            float(row["latitude"]),
            float(row["longitude"])
        )

print(f"Loaded {len(nodes):,} nodes.")


# ============================================================
# LOAD FORWARD + REVERSE GRAPH
# ============================================================

print("Loading edges...")

graph = defaultdict(list)

reverse_graph = defaultdict(list)

edge_count = 0

start = time.perf_counter()

with open(edges_file, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f)

    for row in reader:

        source = int(row["source"])
        target = int(row["target"])
        distance = float(row["distance_km"])

        graph[source].append(
            (target, distance)
        )

        reverse_graph[target].append(
            (source, distance)
        )

        edge_count += 1

load_time = time.perf_counter() - start

print(f"Loaded {edge_count:,} directed edges.")

print()
print(
    f"Graph loading time: "
    f"{load_time:.2f} seconds"
)


# ============================================================
# GENERATE SAME 30 PAIRS
# ============================================================

print()
print(
    f"Generating {NUM_PAIRS} "
    "reproducible source-target pairs..."
)

random.seed(RANDOM_SEED)

node_list = list(nodes.keys())

pairs = []

while len(pairs) < NUM_PAIRS:

    source, target = random.sample(
        node_list,
        2
    )

    pairs.append(
        (source, target)
    )

print(f"Generated {len(pairs)} pairs.")

# ============================================================
# RUN
# ============================================================

print()
print("=" * 70)
print("RUNNING ROUTE BENCHMARK")
print("=" * 70)

results = []


def validate_path(path, source, target, graph):
    """
    Validate a returned route.

    Checks:
    1. Path exists.
    2. Path starts at source.
    3. Path ends at target.
    4. Every consecutive pair is a valid directed edge.
    5. Calculates actual path distance.
    """

    if not path:
        return False, None

    if path[0] != source:
        return False, None

    if path[-1] != target:
        return False, None

    total_distance = 0.0

    for u, v in zip(path, path[1:]):

        edge_found = False

        for neighbor, distance in graph.get(u, []):

            if neighbor == v:
                total_distance += distance
                edge_found = True
                break

        if not edge_found:
            return False, None

    return True, total_distance


# ============================================================
# RUN ALL ROUTES
# ============================================================

for i, (source, target) in enumerate(
    pairs,
    start=1
):

    print()
    print(f"Route {i}/{NUM_PAIRS}")

    print(f"Source: {source}")
    print(f"Target: {target}")

    # --------------------------------------------------------
    # DIJKSTRA
    # --------------------------------------------------------

    d = dijkstra(
        graph,
        source,
        target
    )

    print(
        f"Dijkstra: "
        f"{d['execution_time_ms']:.3f} ms | "
        f"{d['nodes_explored']:,} nodes"
    )

    # --------------------------------------------------------
    # A*
    # --------------------------------------------------------

    a = astar(
        graph,
        nodes,
        source,
        target
    )

    print(
        f"A*:       "
        f"{a['execution_time_ms']:.3f} ms | "
        f"{a['nodes_explored']:,} nodes"
    )

    # --------------------------------------------------------
    # BIDIRECTIONAL DIJKSTRA
    # --------------------------------------------------------

    b = bidirectional_dijkstra(
        graph,
        reverse_graph,
        source,
        target
    )

    print(
        f"Bi-Dijkstra: "
        f"{b['execution_time_ms']:.3f} ms | "
        f"{b['nodes_explored']:,} nodes"
    )

    # --------------------------------------------------------
    # PATH VALIDATION
    # --------------------------------------------------------

    d_path_valid, d_path_distance = validate_path(
        d["path"],
        source,
        target,
        graph
    )

    a_path_valid, a_path_distance = validate_path(
        a["path"],
        source,
        target,
        graph
    )

    b_path_valid, b_path_distance = validate_path(
        b["path"],
        source,
        target,
        graph
    )

    # --------------------------------------------------------
    # COMMON ROUTE VALIDATION
    # --------------------------------------------------------

    valid = (
        d["found"]
        and a["found"]
        and b["found"]
        and d_path_valid
        and a_path_valid
        and b_path_valid
    )

    if valid:

        distance_difference = max(
            abs(
                d["distance_km"]
                - a["distance_km"]
            ),

            abs(
                d["distance_km"]
                - b["distance_km"]
            ),

            abs(
                a["distance_km"]
                - b["distance_km"]
            )
        )

        path_distance_difference = max(
            abs(
                d["distance_km"]
                - d_path_distance
            ),

            abs(
                a["distance_km"]
                - a_path_distance
            ),

            abs(
                b["distance_km"]
                - b_path_distance
            )
        )

    else:

        distance_difference = None
        path_distance_difference = None

    # --------------------------------------------------------
    # PRINT VALIDATION
    # --------------------------------------------------------

    print(
        f"Path validation: "
        f"Dijkstra={'PASS' if d_path_valid else 'FAIL'}, "
        f"A*={'PASS' if a_path_valid else 'FAIL'}, "
        f"Bi-Dijkstra={'PASS' if b_path_valid else 'FAIL'}"
    )

    if valid:

        print(
            f"Path distance difference: "
            f"{path_distance_difference:.10f} km"
        )

    # --------------------------------------------------------
    # STORE RESULT
    # --------------------------------------------------------

    results.append({

        "route": i,

        "source": source,

        "target": target,

        "dijkstra_time_ms":
            d["execution_time_ms"],

        "astar_time_ms":
            a["execution_time_ms"],

        "bidirectional_dijkstra_time_ms":
            b["execution_time_ms"],

        "dijkstra_nodes":
            d["nodes_explored"],

        "astar_nodes":
            a["nodes_explored"],

        "bidirectional_dijkstra_nodes":
            b["nodes_explored"],

        "dijkstra_distance_km":
            d["distance_km"],

        "astar_distance_km":
            a["distance_km"],

        "bidirectional_dijkstra_distance_km":
            b["distance_km"],

        "dijkstra_path_valid":
            d_path_valid,

        "astar_path_valid":
            a_path_valid,

        "bidirectional_dijkstra_path_valid":
            b_path_valid,

        "valid":
            valid,

        "max_distance_difference_km":
            distance_difference,

        "path_distance_difference_km":
            path_distance_difference
    })


# ============================================================
# SAVE CSV
# ============================================================

with open(
    results_file,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=results[0].keys()
    )

    writer.writeheader()

    writer.writerows(results)


print()
print("Results saved to:")
print(results_file)


# ============================================================
# SUMMARY
# ============================================================

valid_results = [
    r for r in results
    if r["valid"]
]


print()
print("=" * 70)
print("EXPERIMENT SUMMARY")
print("=" * 70)

print(
    f"Dataset size       : {SIZE}"
)

print(
    f"Total route pairs  : {NUM_PAIRS}"
)

print(
    f"Valid common routes: "
    f"{len(valid_results)}"
)


if valid_results:

    def average(key):

        return sum(
            r[key]
            for r in valid_results
        ) / len(valid_results)


    def median(key):

        values = sorted(
            r[key]
            for r in valid_results
        )

        n = len(values)

        if n % 2 == 0:

            return (
                values[n // 2 - 1]
                +
                values[n // 2]
            ) / 2

        return values[n // 2]


    # --------------------------------------------------------
    # AVERAGES
    # --------------------------------------------------------

    d_time = average(
        "dijkstra_time_ms"
    )

    a_time = average(
        "astar_time_ms"
    )

    b_time = average(
        "bidirectional_dijkstra_time_ms"
    )


    d_nodes = average(
        "dijkstra_nodes"
    )

    a_nodes = average(
        "astar_nodes"
    )

    b_nodes = average(
        "bidirectional_dijkstra_nodes"
    )


    d_distance = average(
        "dijkstra_distance_km"
    )

    a_distance = average(
        "astar_distance_km"
    )

    b_distance = average(
        "bidirectional_dijkstra_distance_km"
    )


    # --------------------------------------------------------
    # PRINT AVERAGES
    # --------------------------------------------------------

    print()
    print("AVERAGE RESULTS")
    print("-" * 70)

    print(
        f"Dijkstra time       : "
        f"{d_time:.3f} ms"
    )

    print(
        f"A* time             : "
        f"{a_time:.3f} ms"
    )

    print(
        f"Bi-Dijkstra time    : "
        f"{b_time:.3f} ms"
    )

    print(
        f"Dijkstra nodes      : "
        f"{d_nodes:,.0f}"
    )

    print(
        f"A* nodes            : "
        f"{a_nodes:,.0f}"
    )

    print(
        f"Bi-Dijkstra nodes   : "
        f"{b_nodes:,.0f}"
    )


    # --------------------------------------------------------
    # DISTANCES
    # --------------------------------------------------------

    print()
    print(
        f"Dijkstra distance   : "
        f"{d_distance:.6f} km"
    )

    print(
        f"A* distance         : "
        f"{a_distance:.6f} km"
    )

    print(
        f"Bi-Dijkstra distance: "
        f"{b_distance:.6f} km"
    )


    # --------------------------------------------------------
    # MEDIANS
    # --------------------------------------------------------

    print()
    print("MEDIAN EXECUTION TIME")
    print("-" * 70)

    print(
        f"Dijkstra median     : "
        f"{median('dijkstra_time_ms'):.3f} ms"
    )

    print(
        f"A* median           : "
        f"{median('astar_time_ms'):.3f} ms"
    )

    print(
        f"Bi-Dijkstra median  : "
        f"{median('bidirectional_dijkstra_time_ms'):.3f} ms"
    )


    # --------------------------------------------------------
    # COMPARATIVE METRICS
    # --------------------------------------------------------

    print()
    print("COMPARATIVE METRICS")
    print("-" * 70)

    print(
        f"A* speedup              : "
        f"{d_time / a_time:.2f}x"
    )

    print(
        f"Bi-Dijkstra speedup     : "
        f"{d_time / b_time:.2f}x"
    )

    print(
        f"A* node reduction       : "
        f"{(1 - a_nodes / d_nodes) * 100:.2f}%"
    )

    print(
        f"Bi-Dijkstra node reduction: "
        f"{(1 - b_nodes / d_nodes) * 100:.2f}%"
    )


    # --------------------------------------------------------
    # MAX DISTANCE DIFFERENCE
    # --------------------------------------------------------

    max_difference = max(
        r["max_distance_difference_km"]
        for r in valid_results
    )

    max_path_difference = max(
        r["path_distance_difference_km"]
        for r in valid_results
    )


    print(
        f"Maximum distance difference: "
        f"{max_difference:.10f} km"
    )

    print(
        f"Maximum path-distance difference: "
        f"{max_path_difference:.10f} km"
    )


print()
print("=" * 70)