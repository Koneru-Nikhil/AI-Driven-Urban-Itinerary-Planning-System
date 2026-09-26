import json
from pathlib import Path

import pandas as pd

from route_optimization_research.multi_poi.algorithms.nearest_neighbor import (
    nearest_neighbor,
)


# ============================================================
# CONFIGURATION
# ============================================================

CASES_FILE = (
    "route_optimization_research/"
    "multi_poi/results/"
    "benchmark_cases/"
    "benchmark_cases.csv"
)

MATRIX_DIR = Path(
    "route_optimization_research/"
    "multi_poi/results/"
    "distance_matrices"
)

OUTPUT_DIR = Path(
    "route_optimization_research/"
    "multi_poi/results/"
    "benchmarks"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD CASES
# ============================================================

cases = pd.read_csv(
    CASES_FILE
)

results = []


print("=" * 70)
print("NEAREST NEIGHBOR PERFORMANCE BENCHMARK")
print("=" * 70)

print(
    "Benchmark cases:",
    len(cases)
)


# ============================================================
# BENCHMARK
# ============================================================

for _, case in cases.iterrows():

    case_id = case["case_id"]

    print()
    print(
        f"Running {case_id}..."
    )

    # --------------------------------------------------------
    # Load POI IDs
    # --------------------------------------------------------

    poi_ids = json.loads(
        case["poi_ids"]
    )

    start_poi = case[
        "start_poi_id"
    ]

    end_poi = case[
        "end_poi_id"
    ]

    # --------------------------------------------------------
    # Load distance matrix
    # --------------------------------------------------------

    matrix_file = (
        MATRIX_DIR
        / f"{case_id}_distance_matrix.csv"
    )

    matrix = pd.read_csv(
        matrix_file,
        index_col=0
    )

    matrix = matrix.apply(
        pd.to_numeric,
        errors="coerce"
    )

    # --------------------------------------------------------
    # Run algorithm
    # --------------------------------------------------------

    result = nearest_neighbor(
        distance_matrix=matrix,
        poi_ids=poi_ids,
        start_poi=start_poi,
        end_poi=end_poi,
    )

    # --------------------------------------------------------
    # Store result
    # --------------------------------------------------------

    results.append({
        "case_id": case_id,
        "interest_profile": case[
            "interest_profile"
        ],
        "poi_count": len(poi_ids),
        "geographic_spread_km": float(
            case["geographic_spread_km"]
        ),
        "shared_road_node_count": int(
            case["shared_road_node_count"]
        ),
        "start_poi_id": start_poi,
        "end_poi_id": end_poi,
        "algorithm": result[
            "algorithm"
        ],
        "feasible": result[
            "feasible"
        ],
        "route_distance_km": (
            result["distance_km"]
            if result["feasible"]
            else None
        ),
        "execution_time_ms": result[
            "execution_time_ms"
        ],
        "nodes_evaluated": result[
            "nodes_evaluated"
        ],
        "route_length": (
            len(result["route"])
            if result["feasible"]
            else 0
        ),
    })

    if result["feasible"]:

        print(
            f"  Distance: "
            f"{result['distance_km']:.6f} km"
        )

        print(
            f"  Time: "
            f"{result['execution_time_ms']:.6f} ms"
        )

        print(
            f"  Evaluations: "
            f"{result['nodes_evaluated']}"
        )

    else:

        print(
            "  INFEASIBLE"
        )


# ============================================================
# SAVE RESULTS
# ============================================================

results_df = pd.DataFrame(
    results
)

output_file = (
    OUTPUT_DIR
    / "nearest_neighbor_benchmark.csv"
)

results_df.to_csv(
    output_file,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

feasible = results_df[
    results_df["feasible"] == True
]

infeasible = results_df[
    results_df["feasible"] == False
]

print()
print("=" * 70)
print("NEAREST NEIGHBOR BENCHMARK SUMMARY")
print("=" * 70)

print(
    "Total cases:",
    len(results_df)
)

print(
    "Feasible cases:",
    len(feasible)
)

print(
    "Infeasible cases:",
    len(infeasible)
)

if len(feasible) > 0:

    print()
    print(
        "Average execution time:",
        f"{feasible['execution_time_ms'].mean():.6f} ms"
    )

    print(
        "Median execution time:",
        f"{feasible['execution_time_ms'].median():.6f} ms"
    )

    print(
        "Minimum execution time:",
        f"{feasible['execution_time_ms'].min():.6f} ms"
    )

    print(
        "Maximum execution time:",
        f"{feasible['execution_time_ms'].max():.6f} ms"
    )

    print()
    print(
        "Average route distance:",
        f"{feasible['route_distance_km'].mean():.6f} km"
    )

    print(
        "Median route distance:",
        f"{feasible['route_distance_km'].median():.6f} km"
    )

    print(
        "Average candidate evaluations:",
        f"{feasible['nodes_evaluated'].mean():.2f}"
    )

    print(
        "Average route length:",
        f"{feasible['route_length'].mean():.2f}"
    )


# ============================================================
# RESULTS BY POI COUNT
# ============================================================

print()
print("=" * 70)
print("RESULTS BY ITINERARY SIZE")
print("=" * 70)

if len(feasible) > 0:

    size_summary = (
        feasible
        .groupby("poi_count")
        .agg(
            cases=("case_id", "count"),
            avg_time_ms=(
                "execution_time_ms",
                "mean"
            ),
            median_time_ms=(
                "execution_time_ms",
                "median"
            ),
            avg_distance_km=(
                "route_distance_km",
                "mean"
            ),
            avg_evaluations=(
                "nodes_evaluated",
                "mean"
            ),
        )
        .reset_index()
    )

    print(
        size_summary.to_string(
            index=False
        )
    )

    size_summary.to_csv(
        OUTPUT_DIR
        / "nearest_neighbor_by_size.csv",
        index=False
    )


# ============================================================
# RESULTS BY INTEREST PROFILE
# ============================================================

print()
print("=" * 70)
print("RESULTS BY INTEREST PROFILE")
print("=" * 70)

if len(feasible) > 0:

    profile_summary = (
        feasible
        .groupby("interest_profile")
        .agg(
            cases=("case_id", "count"),
            avg_time_ms=(
                "execution_time_ms",
                "mean"
            ),
            avg_distance_km=(
                "route_distance_km",
                "mean"
            ),
            avg_spread_km=(
                "geographic_spread_km",
                "mean"
            ),
        )
        .reset_index()
    )

    print(
        profile_summary.to_string(
            index=False
        )
    )

    profile_summary.to_csv(
        OUTPUT_DIR
        / "nearest_neighbor_by_profile.csv",
        index=False
    )


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print(
    "Detailed results saved:",
    output_file
)

if len(infeasible) > 0:

    print()
    print(
        "Infeasible cases:"
    )

    print(
        infeasible[
            [
                "case_id",
                "interest_profile",
                "poi_count",
            ]
        ].to_string(
            index=False
        )
    )

print()
print(
    "NEAREST NEIGHBOR BENCHMARK COMPLETE"
)