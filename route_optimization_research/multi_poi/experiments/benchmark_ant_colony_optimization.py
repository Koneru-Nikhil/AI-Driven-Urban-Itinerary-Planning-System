import ast
import os

import pandas as pd

from route_optimization_research.multi_poi.algorithms.ant_colony_optimization import (
    ant_colony_optimization,
)


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

RESULTS_DIR = os.path.join(
    BASE_DIR,
    "results"
)

CASES_FILE = os.path.join(
    RESULTS_DIR,
    "benchmark_cases",
    "benchmark_cases.csv"
)

MATRIX_DIR = os.path.join(
    RESULTS_DIR,
    "distance_matrices"
)

OUTPUT_FILE = os.path.join(
    RESULTS_DIR,
    "ant_colony_optimization_benchmark.csv"
)

OUTPUT_PROFILE = os.path.join(
    RESULTS_DIR,
    "ant_colony_optimization_benchmark_by_profile.csv"
)

OUTPUT_SIZE = os.path.join(
    RESULTS_DIR,
    "ant_colony_optimization_benchmark_by_size.csv"
)


def load_distance_matrix(case_id):
    """
    Load the directed POI-to-POI road-distance matrix.
    """

    file_path = os.path.join(
        MATRIX_DIR,
        f"{case_id}_distance_matrix.csv"
    )

    df = pd.read_csv(
        file_path,
        index_col=0
    )

    matrix = {}

    for source in df.index:

        for target in df.columns:

            value = df.loc[source, target]

            if pd.notna(value):

                matrix[
                    (str(source), str(target))
                ] = float(value)

    return matrix


def main():

    cases = pd.read_csv(
        CASES_FILE
    )

    results = []

    print("=" * 75)
    print("ANT COLONY OPTIMIZATION BENCHMARK")
    print("=" * 75)

    for _, row in cases.iterrows():

        case_id = row["case_id"]

        interest_profile = row[
            "interest_profile"
        ]

        poi_count = int(
            row["poi_count"]
        )

        poi_ids = [
            str(x)
            for x in ast.literal_eval(
                row["poi_ids"]
            )
        ]

        start_poi = str(
            row["start_poi_id"]
        )

        end_poi = str(
            row["end_poi_id"]
        )

        geographic_spread = float(
            row["geographic_spread_km"]
        )

        matrix = load_distance_matrix(
            case_id
        )

        result = ant_colony_optimization(
            distance_matrix=matrix,
            poi_ids=poi_ids,
            start_poi=start_poi,
            end_poi=end_poi,
            ants=30,
            iterations=100,
            alpha=1.0,
            beta=3.0,
            evaporation_rate=0.5,
            pheromone_deposit=1.0,
            seed=42
        )

        results.append(
            {
                "case_id":
                    case_id,

                "interest_profile":
                    interest_profile,

                "poi_count":
                    poi_count,

                "geographic_spread_km":
                    geographic_spread,

                "feasible":
                    result["feasible"],

                "route_distance_km":
                    result["distance_km"],

                "execution_time_ms":
                    result["execution_time_ms"],

                "candidate_evaluations":
                    result["nodes_evaluated"],

                "route_length":
                    len(result["route"])
                    if result["route"]
                    else 0
            }
        )

        if result["feasible"]:

            print(
                f"{case_id} | "
                f"POIs={poi_count} | "
                f"Distance="
                f"{result['distance_km']:.6f} km | "
                f"Time="
                f"{result['execution_time_ms']:.3f} ms | "
                f"Evaluations="
                f"{result['nodes_evaluated']}"
            )

        else:

            print(
                f"{case_id} | "
                f"POIs={poi_count} | "
                f"INFEASIBLE"
            )

    df = pd.DataFrame(
        results
    )

    # --------------------------------------------------
    # Save case-level results
    # --------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------
    # Feasible cases for summaries
    # --------------------------------------------------

    feasible_df = df[
        df["feasible"] == True
    ].copy()

    # --------------------------------------------------
    # Summary by interest profile
    # --------------------------------------------------

    profile_summary = (
        feasible_df
        .groupby("interest_profile")
        .agg(
            cases=("case_id", "count"),

            avg_execution_time_ms=(
                "execution_time_ms",
                "mean"
            ),

            median_execution_time_ms=(
                "execution_time_ms",
                "median"
            ),

            avg_route_distance_km=(
                "route_distance_km",
                "mean"
            ),

            median_route_distance_km=(
                "route_distance_km",
                "median"
            ),

            avg_candidate_evaluations=(
                "candidate_evaluations",
                "mean"
            ),

            avg_geographic_spread_km=(
                "geographic_spread_km",
                "mean"
            )
        )
        .reset_index()
    )

    profile_summary.to_csv(
        OUTPUT_PROFILE,
        index=False
    )

    # --------------------------------------------------
    # Summary by POI count
    # --------------------------------------------------

    size_summary = (
        feasible_df
        .groupby("poi_count")
        .agg(
            cases=("case_id", "count"),

            avg_execution_time_ms=(
                "execution_time_ms",
                "mean"
            ),

            median_execution_time_ms=(
                "execution_time_ms",
                "median"
            ),

            avg_route_distance_km=(
                "route_distance_km",
                "mean"
            ),

            median_route_distance_km=(
                "route_distance_km",
                "median"
            ),

            avg_candidate_evaluations=(
                "candidate_evaluations",
                "mean"
            )
        )
        .reset_index()
    )

    size_summary.to_csv(
        OUTPUT_SIZE,
        index=False
    )

    # --------------------------------------------------
    # Overall summary
    # --------------------------------------------------

    total_cases = len(df)

    feasible_cases = len(
        feasible_df
    )

    infeasible_cases = (
        total_cases - feasible_cases
    )

    print()
    print("=" * 75)
    print("OVERALL SUMMARY")
    print("=" * 75)

    print(
        f"Total cases          : "
        f"{total_cases}"
    )

    print(
        f"Feasible cases       : "
        f"{feasible_cases}"
    )

    print(
        f"Infeasible cases     : "
        f"{infeasible_cases}"
    )

    if feasible_cases > 0:

        print(
            f"Average time         : "
            f"{feasible_df['execution_time_ms'].mean():.6f} ms"
        )

        print(
            f"Median time          : "
            f"{feasible_df['execution_time_ms'].median():.6f} ms"
        )

        print(
            f"Minimum time         : "
            f"{feasible_df['execution_time_ms'].min():.6f} ms"
        )

        print(
            f"Maximum time         : "
            f"{feasible_df['execution_time_ms'].max():.6f} ms"
        )

        print(
            f"Average distance     : "
            f"{feasible_df['route_distance_km'].mean():.6f} km"
        )

        print(
            f"Median distance      : "
            f"{feasible_df['route_distance_km'].median():.6f} km"
        )

        print(
            f"Average evaluations  : "
            f"{feasible_df['candidate_evaluations'].mean():.2f}"
        )

    print()
    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print(
        f"Saved: {OUTPUT_PROFILE}"
    )

    print(
        f"Saved: {OUTPUT_SIZE}"
    )


if __name__ == "__main__":
    main()