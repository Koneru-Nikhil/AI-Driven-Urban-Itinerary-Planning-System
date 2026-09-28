import ast
import math
import os

import pandas as pd

from route_optimization_research.multi_poi.algorithms.tabu_search import (
    tabu_search,
)


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CASES_FILE = os.path.join(
    BASE_DIR,
    "results",
    "benchmark_cases",
    "benchmark_cases.csv",
)

MATRIX_DIR = os.path.join(
    BASE_DIR,
    "results",
    "distance_matrices",
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results",
)


def load_matrix(case_id):
    path = os.path.join(
        MATRIX_DIR,
        f"{case_id}_distance_matrix.csv",
    )

    matrix = pd.read_csv(
        path,
        index_col=0,
    )

    matrix.index = matrix.index.astype(str)
    matrix.columns = matrix.columns.astype(str)

    return matrix


def parse_poi_ids(value):
    parsed = ast.literal_eval(value)

    return [
        str(poi)
        for poi in parsed
    ]


def main():

    cases = pd.read_csv(
        CASES_FILE
    )

    results = []

    print("=" * 80)
    print("TABU SEARCH BENCHMARK")
    print("=" * 80)

    for _, row in cases.iterrows():

        case_id = str(
            row["case_id"]
        )

        interest_profile = str(
            row["interest_profile"]
        )

        poi_count = int(
            row["poi_count"]
        )

        geographic_spread = float(
            row["geographic_spread_km"]
        )

        matrix = load_matrix(
            case_id
        )

        poi_ids = parse_poi_ids(
            row["poi_ids"]
        )

        start_poi = str(
            row["start_poi_id"]
        )

        end_poi = str(
            row["end_poi_id"]
        )

        result = tabu_search(
            distance_matrix=matrix,
            poi_ids=poi_ids,
            start_poi=start_poi,
            end_poi=end_poi,
            seed=42,
            max_iterations=500,
            tabu_tenure=15,
        )

        distance = result["distance_km"]

        if math.isfinite(distance):
            distance_value = distance
        else:
            distance_value = math.nan

        results.append(
            {
                "case_id": case_id,
                "interest_profile": interest_profile,
                "poi_count": poi_count,
                "geographic_spread_km": geographic_spread,
                "feasible": result["feasible"],
                "route_distance_km": distance_value,
                "execution_time_ms": result[
                    "execution_time_ms"
                ],
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

        if math.isfinite(distance):
            distance_text = f"{distance:.6f}"
        else:
            distance_text = "INF"

        print(
            f"{case_id}: "
            f"{poi_count} POIs | "
            f"{interest_profile} | "
            f"time={result['execution_time_ms']:.3f} ms | "
            f"distance={distance_text} km | "
            f"evaluations={result['nodes_evaluated']} | "
            f"feasible={result['feasible']}"
        )

    df = pd.DataFrame(results)

    output_file = os.path.join(
        RESULTS_DIR,
        "tabu_search_benchmark.csv",
    )

    df.to_csv(
        output_file,
        index=False,
    )

    feasible_df = df[
        df["feasible"] == True
    ]

    print()
    print("=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)

    print(
        f"Total cases       : {len(df)}"
    )

    print(
        f"Feasible cases    : {len(feasible_df)}"
    )

    print(
        f"Infeasible cases  : "
        f"{len(df) - len(feasible_df)}"
    )

    if len(feasible_df) > 0:

        print(
            f"Average time      : "
            f"{feasible_df['execution_time_ms'].mean():.6f} ms"
        )

        print(
            f"Median time       : "
            f"{feasible_df['execution_time_ms'].median():.6f} ms"
        )

        print(
            f"Minimum time      : "
            f"{feasible_df['execution_time_ms'].min():.6f} ms"
        )

        print(
            f"Maximum time      : "
            f"{feasible_df['execution_time_ms'].max():.6f} ms"
        )

        print(
            f"Average distance  : "
            f"{feasible_df['route_distance_km'].mean():.6f} km"
        )

        print(
            f"Median distance   : "
            f"{feasible_df['route_distance_km'].median():.6f} km"
        )

        print(
            f"Average evaluations: "
            f"{feasible_df['candidate_evaluations'].mean():.2f}"
        )

    # ---------------------------------------------------------
    # Summary by POI count
    # ---------------------------------------------------------
    print()
    print("=" * 80)
    print("SUMMARY BY POI COUNT")
    print("=" * 80)

    size_summary = (
        feasible_df
        .groupby("poi_count")
        .agg(
            cases=("case_id", "count"),
            avg_time_ms=(
                "execution_time_ms",
                "mean",
            ),
            median_time_ms=(
                "execution_time_ms",
                "median",
            ),
            avg_distance_km=(
                "route_distance_km",
                "mean",
            ),
            median_distance_km=(
                "route_distance_km",
                "median",
            ),
            avg_candidate_evaluations=(
                "candidate_evaluations",
                "mean",
            ),
        )
        .reset_index()
    )

    print(
        size_summary.to_string(
            index=False
        )
    )

    size_output = os.path.join(
        RESULTS_DIR,
        "tabu_search_benchmark_by_size.csv",
    )

    size_summary.to_csv(
        size_output,
        index=False,
    )

    # ---------------------------------------------------------
    # Summary by interest profile
    # ---------------------------------------------------------
    print()
    print("=" * 80)
    print("SUMMARY BY INTEREST PROFILE")
    print("=" * 80)

    profile_summary = (
        feasible_df
        .groupby("interest_profile")
        .agg(
            cases=("case_id", "count"),
            avg_time_ms=(
                "execution_time_ms",
                "mean",
            ),
            median_time_ms=(
                "execution_time_ms",
                "median",
            ),
            avg_distance_km=(
                "route_distance_km",
                "mean",
            ),
            avg_geographic_spread_km=(
                "geographic_spread_km",
                "mean",
            ),
            avg_candidate_evaluations=(
                "candidate_evaluations",
                "mean",
            ),
        )
        .reset_index()
    )

    print(
        profile_summary.to_string(
            index=False
        )
    )

    profile_output = os.path.join(
        RESULTS_DIR,
        "tabu_search_benchmark_by_profile.csv",
    )

    profile_summary.to_csv(
        profile_output,
        index=False,
    )

    print()
    print("=" * 80)
    print("FILES SAVED")
    print("=" * 80)

    print(output_file)
    print(size_output)
    print(profile_output)


if __name__ == "__main__":
    main()