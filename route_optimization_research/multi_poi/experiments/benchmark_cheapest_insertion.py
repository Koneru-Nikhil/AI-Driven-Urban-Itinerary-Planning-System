import json
from pathlib import Path

import pandas as pd

from route_optimization_research.multi_poi.algorithms.cheapest_insertion import (
    cheapest_insertion,
)


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

RESULTS_DIR = Path(
    "route_optimization_research/"
    "multi_poi/results/"
    "benchmarks"
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# LOAD CASES
# ============================================================

cases = pd.read_csv(
    CASES_FILE
)


results = []


print("=" * 80)
print("CHEAPEST INSERTION PERFORMANCE BENCHMARK")
print("=" * 80)


# ============================================================
# RUN BENCHMARK
# ============================================================

for _, case in cases.iterrows():

    case_id = case["case_id"]

    poi_count = int(
        case["poi_count"]
    )

    profile = case["interest_profile"]

    poi_ids = json.loads(
        case["poi_ids"]
    )

    start_poi = case[
        "start_poi_id"
    ]

    end_poi = case[
        "end_poi_id"
    ]

    matrix_file = (
        MATRIX_DIR
        / f"{case_id}_distance_matrix.csv"
    )

    matrix = pd.read_csv(
        matrix_file,
        index_col=0,
    )

    matrix = matrix.apply(
        pd.to_numeric,
        errors="coerce",
    )

    result = cheapest_insertion(
        distance_matrix=matrix,
        poi_ids=poi_ids,
        start_poi=start_poi,
        end_poi=end_poi,
    )

    print(
        f"{case_id}: "
        f"{result['execution_time_ms']:.4f} ms | "
        f"{result['distance_km']:.6f} km | "
        f"feasible={result['feasible']}"
    )

    results.append(
        {
            "case_id": case_id,
            "profile": profile,
            "poi_count": poi_count,
            "geographic_spread_km": case[
                "geographic_spread_km"
            ],
            "feasible": result[
                "feasible"
            ],
            "execution_time_ms": result[
                "execution_time_ms"
            ],
            "route_distance_km": (
                result["distance_km"]
                if result["feasible"]
                else None
            ),
            "candidate_evaluations": result[
                "nodes_evaluated"
            ],
            "route_length": (
                len(result["route"])
                if result["feasible"]
                else 0
            ),
        }
    )


# ============================================================
# SAVE CASE-LEVEL RESULTS
# ============================================================

results_df = pd.DataFrame(
    results
)

output_file = (
    RESULTS_DIR
    / "cheapest_insertion_benchmark.csv"
)

results_df.to_csv(
    output_file,
    index=False,
)

print()
print(
    f"Saved: {output_file}"
)


# ============================================================
# FEASIBLE CASES
# ============================================================

feasible_df = results_df[
    results_df["feasible"]
].copy()


# ============================================================
# OVERALL SUMMARY
# ============================================================

print()
print("=" * 80)
print("OVERALL SUMMARY")
print("=" * 80)

print(
    "Total cases:",
    len(results_df)
)

print(
    "Feasible cases:",
    len(feasible_df)
)

print(
    "Infeasible cases:",
    len(results_df)
    - len(feasible_df)
)

if len(feasible_df) > 0:

    print(
        f"Average execution time: "
        f"{feasible_df['execution_time_ms'].mean():.6f} ms"
    )

    print(
        f"Median execution time: "
        f"{feasible_df['execution_time_ms'].median():.6f} ms"
    )

    print(
        f"Minimum execution time: "
        f"{feasible_df['execution_time_ms'].min():.6f} ms"
    )

    print(
        f"Maximum execution time: "
        f"{feasible_df['execution_time_ms'].max():.6f} ms"
    )

    print(
        f"Average route distance: "
        f"{feasible_df['route_distance_km'].mean():.6f} km"
    )

    print(
        f"Median route distance: "
        f"{feasible_df['route_distance_km'].median():.6f} km"
    )

    print(
        f"Average candidate evaluations: "
        f"{feasible_df['candidate_evaluations'].mean():.2f}"
    )


# ============================================================
# BY ITINERARY SIZE
# ============================================================

size_summary = (
    feasible_df
    .groupby("poi_count")
    .agg(
        cases=("case_id", "count"),
        average_time_ms=(
            "execution_time_ms",
            "mean",
        ),
        median_time_ms=(
            "execution_time_ms",
            "median",
        ),
        average_distance_km=(
            "route_distance_km",
            "mean",
        ),
        median_distance_km=(
            "route_distance_km",
            "median",
        ),
        average_candidate_evaluations=(
            "candidate_evaluations",
            "mean",
        ),
    )
    .reset_index()
)


size_file = (
    RESULTS_DIR
    / "cheapest_insertion_by_size.csv"
)

size_summary.to_csv(
    size_file,
    index=False,
)


print()
print("=" * 80)
print("BY ITINERARY SIZE")
print("=" * 80)

print(
    size_summary.to_string(
        index=False
    )
)


# ============================================================
# BY PROFILE
# ============================================================

profile_summary = (
    feasible_df
    .groupby("profile")
    .agg(
        cases=("case_id", "count"),
        average_time_ms=(
            "execution_time_ms",
            "mean",
        ),
        median_time_ms=(
            "execution_time_ms",
            "median",
        ),
        average_distance_km=(
            "route_distance_km",
            "mean",
        ),
        average_spread_km=(
            "geographic_spread_km",
            "mean",
        ),
        average_candidate_evaluations=(
            "candidate_evaluations",
            "mean",
        ),
    )
    .reset_index()
)


profile_file = (
    RESULTS_DIR
    / "cheapest_insertion_by_profile.csv"
)

profile_summary.to_csv(
    profile_file,
    index=False,
)


print()
print("=" * 80)
print("BY INTEREST PROFILE")
print("=" * 80)

print(
    profile_summary.to_string(
        index=False
    )
)


# ============================================================
# FINISH
# ============================================================

print()
print("=" * 80)
print("CHEAPEST INSERTION BENCHMARK COMPLETE")
print("=" * 80)

print(
    f"Case results : {output_file}"
)

print(
    f"Size summary : {size_file}"
)

print(
    f"Profile summary : {profile_file}"
)