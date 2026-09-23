import pandas as pd

from route_optimization_research.algorithms.shortest_path import (
    dijkstra,
    astar
)

from route_optimization_research.algorithms.bidirectional_dijkstra import (
    bidirectional_dijkstra
)

from route_optimization_research.algorithms.bidirectional_astar import (
    bidirectional_astar
)


# =========================================================
# DATASET
# =========================================================

BASE = r"C:\Users\nikhi\Downloads\Hyderabad_Route_Research\connected_subsets"

nodes_file = BASE + r"\Hyderabad_10K_Nodes.csv"
edges_file = BASE + r"\Hyderabad_10K_Edges.csv"


# =========================================================
# LOAD DATA
# =========================================================

nodes_df = pd.read_csv(nodes_file)
edges_df = pd.read_csv(edges_file)

print("=" * 70)
print("BIDIRECTIONAL A* SINGLE ROUTE TEST")
print("=" * 70)

print(f"Nodes loaded: {len(nodes_df):,}")
print(f"Edges loaded: {len(edges_df):,}")
print()


# =========================================================
# COORDINATES
# =========================================================

coordinates = {
    int(row.node_id): (
        float(row.latitude),
        float(row.longitude)
    )
    for row in nodes_df.itertuples()
}


# =========================================================
# BUILD DIRECTED GRAPH
# =========================================================

graph = {}
reverse_graph = {}

for node in coordinates:
    graph[node] = []
    reverse_graph[node] = []


for row in edges_df.itertuples():

    source = int(row.source)
    target = int(row.target)
    distance = float(row.distance_km)

    graph[source].append(
        (target, distance)
    )

    reverse_graph[target].append(
        (source, distance)
    )


# =========================================================
# SELECT ROUTE
# =========================================================

source = int(
    nodes_df.iloc[0]["node_id"]
)

target = int(
    nodes_df.iloc[-1]["node_id"]
)

print(f"Source: {source}")
print(f"Target: {target}")
print()


# =========================================================
# RUN ALGORITHMS
# =========================================================

print("Running algorithms...")
print()

dijkstra_result = dijkstra(
    graph,
    source,
    target
)

astar_result = astar(
    graph,
    coordinates,
    source,
    target
)

bidijkstra_result = bidirectional_dijkstra(
    graph,
    reverse_graph,
    source,
    target
)

biastar_result = bidirectional_astar(
    graph,
    reverse_graph,
    coordinates,
    source,
    target
)


# =========================================================
# DISPLAY RESULTS
# =========================================================

results = [
    dijkstra_result,
    astar_result,
    bidijkstra_result,
    biastar_result
]

print("-" * 70)
print("RESULTS")
print("-" * 70)

for result in results:

    print(
        f"{result['algorithm']:<25} "
        f"{result['distance_km']:.10f} km | "
        f"{result['execution_time_ms']:.3f} ms | "
        f"{result['nodes_explored']:,} nodes | "
        f"found={result['found']}"
    )


# =========================================================
# DISTANCE COMPARISON
# =========================================================

print()
print("-" * 70)
print("DISTANCE COMPARISON")
print("-" * 70)

base_distance = dijkstra_result["distance_km"]

for result in results:

    difference = abs(
        result["distance_km"]
        - base_distance
    )

    print(
        f"{result['algorithm']:<25} "
        f"difference = {difference:.10f} km"
    )


# =========================================================
# BIDIRECTIONAL A* PATH VALIDATION
# =========================================================

print()
print("-" * 70)
print("BIDIRECTIONAL A* PATH VALIDATION")
print("-" * 70)

path = biastar_result["path"]

valid = True


# Check path exists

if not path:

    valid = False
    print("FAIL: Empty path")


# Check source

elif path[0] != source:

    valid = False
    print("FAIL: Path does not start at source")


# Check target

elif path[-1] != target:

    valid = False
    print("FAIL: Path does not end at target")


# =========================================================
# CHECK EVERY EDGE
# =========================================================

if valid:

    actual_distance = 0.0

    for u, v in zip(path, path[1:]):

        found_edge = False

        for neighbor, weight in graph.get(
            u,
            []
        ):

            if neighbor == v:

                actual_distance += weight
                found_edge = True
                break

        if not found_edge:

            valid = False

            print(
                f"FAIL: Invalid edge {u} -> {v}"
            )

            break


# =========================================================
# DISTANCE VALIDATION
# =========================================================

if valid:

    distance_difference = abs(
        actual_distance
        - biastar_result["distance_km"]
    )

    print("Path validation: PASS")

    print(
        f"Path nodes: {len(path):,}"
    )

    print(
        f"Reported distance: "
        f"{biastar_result['distance_km']:.10f} km"
    )

    print(
        f"Actual path distance: "
        f"{actual_distance:.10f} km"
    )

    print(
        f"Distance difference: "
        f"{distance_difference:.10f} km"
    )

    if distance_difference < 1e-9:

        print("Distance validation: PASS")

    else:

        print("Distance validation: FAIL")


# =========================================================
# FINAL CORRECTNESS CHECK
# =========================================================

print()
print("-" * 70)
print("CORRECTNESS CHECK")
print("-" * 70)

all_found = all(
    result["found"]
    for result in results
)

same_distance = all(
    abs(
        result["distance_km"]
        - base_distance
    ) < 1e-9
    for result in results
)


if all_found and same_distance and valid:

    print("ALL CHECKS PASSED")
    print(
        "Bidirectional A* produced the same "
        "shortest-path distance as the other algorithms."
    )

else:

    print("CHECK FAILED")
    print(
        "Bidirectional A* did not match "
        "the reference shortest-path result."
    )


print()
print("=" * 70)