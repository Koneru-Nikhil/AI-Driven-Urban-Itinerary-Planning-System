import pandas as pd
import math

from route_optimization_research.multi_poi.algorithms.road_distance import (
    load_road_graph,
    shortest_path_distance,
)


EDGES_FILE = (
    r"C:\Users\nikhi\Downloads\Hyderabad_Route_Research"
    r"\Hyderabad_Largest_Component_Edges.csv"
)

MAPPING_FILE = (
    "route_optimization_research/"
    "multi_poi/results/"
    "Hyderabad_Itinerary_POI_Road_Mapping.csv"
)


print("=" * 60)
print("POI ROAD-DISTANCE VALIDATION")
print("=" * 60)


# ---------------------------------------------------------
# Load graph
# ---------------------------------------------------------

print("Loading road network...")

graph = load_road_graph(
    EDGES_FILE
)

print(
    "Graph nodes with outgoing edges:",
    len(graph)
)


# ---------------------------------------------------------
# Load POI mapping
# ---------------------------------------------------------

pois = pd.read_csv(
    MAPPING_FILE
)

pois = pois.copy()

pois = pois.reset_index(
    drop=True
)

print(
    "Mapped itinerary POIs:",
    len(pois)
)


# ---------------------------------------------------------
# Select deterministic test POIs
# ---------------------------------------------------------

# Use fixed positions so the test is reproducible.

test_indices = [
    0,
    100,
    500,
    1000,
    2000,
    3000,
    4000,
    5000,
    6000,
    7000 - 1,
]

test_indices = [
    i for i in test_indices
    if i < len(pois)
]

test_pois = pois.iloc[
    test_indices
].copy()


print()
print("Test POIs:")

print(
    test_pois[
        [
            "poi_id",
            "name",
            "itinerary_category",
            "nearest_road_node"
        ]
    ].to_string(index=False)
)


# ---------------------------------------------------------
# Test pair distances
# ---------------------------------------------------------

print()
print("=" * 60)
print("PAIRWISE ROAD DISTANCES")
print("=" * 60)


results = []

for i in range(len(test_pois)):

    source = test_pois.iloc[i]

    for j in range(i + 1, len(test_pois)):

        target = test_pois.iloc[j]

        source_node = int(
            source["nearest_road_node"]
        )

        target_node = int(
            target["nearest_road_node"]
        )

        distance = shortest_path_distance(
            graph,
            source_node,
            target_node
        )

        results.append({
            "poi_a": source["poi_id"],
            "poi_b": target["poi_id"],
            "name_a": source["name"],
            "name_b": target["name"],
            "node_a": source_node,
            "node_b": target_node,
            "distance_km": (
                round(distance, 6)
                if math.isfinite(distance)
                else None
            ),
            "reachable": math.isfinite(distance)
        })


result_df = pd.DataFrame(results)


print(
    result_df.to_string(index=False)
)


# ---------------------------------------------------------
# Validation summary
# ---------------------------------------------------------

print()
print("=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)

total_pairs = len(result_df)

reachable_pairs = result_df[
    result_df["reachable"] == True
]

unreachable_pairs = result_df[
    result_df["reachable"] == False
]

print(
    f"Total test pairs       : {total_pairs}"
)

print(
    f"Reachable pairs        : {len(reachable_pairs)}"
)

print(
    f"Unreachable pairs      : {len(unreachable_pairs)}"
)

if len(reachable_pairs) > 0:

    print(
        "Minimum distance (km) : "
        f"{reachable_pairs['distance_km'].min():.6f}"
    )

    print(
        "Maximum distance (km) : "
        f"{reachable_pairs['distance_km'].max():.6f}"
    )

    print(
        "Average distance (km) : "
        f"{reachable_pairs['distance_km'].mean():.6f}"
    )

print()
print("ROAD-DISTANCE TEST COMPLETED")