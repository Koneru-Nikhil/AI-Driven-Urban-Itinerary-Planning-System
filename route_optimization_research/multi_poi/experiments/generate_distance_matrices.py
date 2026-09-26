import json
import heapq
import math
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

EDGES_FILE = (
    r"C:\Users\nikhi\Downloads\Hyderabad_Route_Research"
    r"\Hyderabad_Largest_Component_Edges.csv"
)

POI_FILE = (
    "route_optimization_research/"
    "multi_poi/results/"
    "Hyderabad_Itinerary_POIs.csv"
)

MAPPING_FILE = (
    "route_optimization_research/"
    "multi_poi/results/"
    "Hyderabad_Itinerary_POI_Road_Mapping.csv"
)

CASES_FILE = (
    "route_optimization_research/"
    "multi_poi/results/"
    "benchmark_cases/"
    "benchmark_cases.csv"
)

OUTPUT_DIR = Path(
    "route_optimization_research/"
    "multi_poi/results/"
    "distance_matrices"
)


# ============================================================
# LOAD ROAD GRAPH
# ============================================================

print("=" * 70)
print("MULTI-POI DISTANCE MATRIX GENERATION")
print("=" * 70)

print()
print("Loading road network...")

edges = pd.read_csv(
    EDGES_FILE
)

graph = {}

for row in edges.itertuples(index=False):

    source = int(row.source)
    target = int(row.target)
    distance = float(row.distance_km)

    graph.setdefault(
        source,
        []
    ).append(
        (target, distance)
    )

print(
    "Graph nodes with outgoing edges:",
    len(graph)
)

print(
    "Road edges:",
    len(edges)
)


# ============================================================
# LOAD POI DATA
# ============================================================

pois = pd.read_csv(
    POI_FILE
)

mapping = pd.read_csv(
    MAPPING_FILE
)

cases = pd.read_csv(
    CASES_FILE
)

mapping_small = mapping[
    [
        "poi_id",
        "nearest_road_node"
    ]
].copy()

mapping_small["nearest_road_node"] = (
    mapping_small["nearest_road_node"]
    .astype("int64")
)

pois = pois.merge(
    mapping_small,
    on="poi_id",
    how="inner"
)

print(
    "Mapped POIs:",
    len(pois)
)

print(
    "Benchmark cases:",
    len(cases)
)


# ============================================================
# DIJKSTRA FROM ONE SOURCE
# ============================================================

def dijkstra_all(graph, source):
    """
    Compute shortest-path distances from one source
    to every reachable node.
    """

    distances = {
        source: 0.0
    }

    heap = [
        (0.0, source)
    ]

    while heap:

        current_distance, current_node = (
            heapq.heappop(heap)
        )

        if current_distance != distances.get(
            current_node,
            math.inf
        ):
            continue

        for neighbor, edge_distance in graph.get(
            current_node,
            []
        ):

            new_distance = (
                current_distance
                + edge_distance
            )

            if new_distance < distances.get(
                neighbor,
                math.inf
            ):

                distances[neighbor] = (
                    new_distance
                )

                heapq.heappush(
                    heap,
                    (
                        new_distance,
                        neighbor
                    )
                )

    return distances


# ============================================================
# OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# PROCESS EACH BENCHMARK CASE
# ============================================================

summary = []

for case_index, case in cases.iterrows():

    case_id = case["case_id"]

    print()
    print("-" * 70)
    print(
        f"Processing {case_id} "
        f"({case_index + 1}/{len(cases)})"
    )
    print("-" * 70)

    # --------------------------------------------------------
    # Recover POI IDs
    # --------------------------------------------------------

    poi_ids = json.loads(
        case["poi_ids"]
    )

    case_pois = pois[
        pois["poi_id"].isin(poi_ids)
    ].copy()

    # Preserve exact order from benchmark case
    case_pois["order"] = case_pois[
        "poi_id"
    ].map(
        {
            poi_id: i
            for i, poi_id in enumerate(poi_ids)
        }
    )

    case_pois = case_pois.sort_values(
        "order"
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Check
    # --------------------------------------------------------

    if len(case_pois) != len(poi_ids):

        print(
            "ERROR: POI count mismatch."
        )

        continue

    road_nodes = (
        case_pois[
            "nearest_road_node"
        ]
        .astype("int64")
        .tolist()
    )

    unique_nodes = list(
        dict.fromkeys(
            road_nodes
        )
    )

    print(
        "POIs:",
        len(poi_ids)
    )

    print(
        "Unique road nodes:",
        len(unique_nodes)
    )

    # --------------------------------------------------------
    # Calculate distances
    # --------------------------------------------------------

    matrix = []

    # Cache Dijkstra results by source node.
    # If multiple POIs share a road node, we only
    # run Dijkstra once for that source.
    source_cache = {}

    for source_index, source_node in enumerate(
        road_nodes
    ):

        if source_node not in source_cache:

            print(
                f"  Dijkstra source "
                f"{source_index + 1}/{len(road_nodes)}"
            )

            source_cache[source_node] = (
                dijkstra_all(
                    graph,
                    source_node
                )
            )

        distances = source_cache[
            source_node
        ]

        row = []

        for target_node in road_nodes:

            distance = distances.get(
                target_node,
                math.inf
            )

            if math.isinf(distance):

                row.append(None)

            else:

                row.append(
                    round(
                        distance,
                        6
                    )
                )

        matrix.append(row)

    matrix_df = pd.DataFrame(
        matrix,
        index=poi_ids,
        columns=poi_ids
    )

    matrix_df.index.name = (
        "source_poi_id"
    )

    # --------------------------------------------------------
    # Save matrix
    # --------------------------------------------------------

    matrix_file = (
        OUTPUT_DIR
        / f"{case_id}_distance_matrix.csv"
    )

    matrix_df.to_csv(
        matrix_file
    )

    # --------------------------------------------------------
    # Save POI metadata for this case
    # --------------------------------------------------------

    metadata_columns = [
        "poi_id",
        "name",
        "itinerary_category",
        "latitude",
        "longitude",
        "nearest_road_node",
    ]

    metadata_file = (
        OUTPUT_DIR
        / f"{case_id}_poi_metadata.csv"
    )

    case_pois[
        [
            c
            for c in metadata_columns
            if c in case_pois.columns
        ]
    ].to_csv(
        metadata_file,
        index=False
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    numeric_values = (
        matrix_df
        .apply(
            pd.to_numeric,
            errors="coerce"
        )
        .values
    )

    total_entries = (
        len(poi_ids)
        * len(poi_ids)
    )

    reachable_entries = (
        pd.notna(numeric_values)
        .sum()
    )

    unreachable_entries = (
        total_entries
        - reachable_entries
    )

    diagonal_ok = True

    for poi_id in poi_ids:

        value = matrix_df.loc[
            poi_id,
            poi_id
        ]

        if (
            pd.isna(value)
            or abs(float(value)) > 1e-9
        ):

            diagonal_ok = False
            break

    summary.append({
        "case_id": case_id,
        "poi_count": len(poi_ids),
        "unique_road_nodes": len(
            unique_nodes
        ),
        "total_matrix_entries": total_entries,
        "reachable_entries": int(
            reachable_entries
        ),
        "unreachable_entries": int(
            unreachable_entries
        ),
        "diagonal_zero": diagonal_ok,
        "matrix_file": str(
            matrix_file
        ),
    })

    print(
        "Reachable entries:",
        reachable_entries,
        "/",
        total_entries
    )

    print(
        "Unreachable entries:",
        unreachable_entries
    )

    print(
        "Diagonal zero:",
        diagonal_ok
    )


# ============================================================
# SAVE SUMMARY
# ============================================================

summary_df = pd.DataFrame(
    summary
)

summary_file = (
    OUTPUT_DIR
    / "distance_matrix_summary.csv"
)

summary_df.to_csv(
    summary_file,
    index=False
)


print()
print("=" * 70)
print("DISTANCE MATRIX GENERATION COMPLETE")
print("=" * 70)

print(
    "Cases processed:",
    len(summary_df)
)

print(
    "Output directory:",
    OUTPUT_DIR
)

print()
print(
    summary_df[
        [
            "case_id",
            "poi_count",
            "unique_road_nodes",
            "reachable_entries",
            "unreachable_entries",
            "diagonal_zero",
        ]
    ].to_string(index=False)
)