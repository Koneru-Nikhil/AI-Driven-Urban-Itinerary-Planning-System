import os
import ast
import pandas as pd

from route_optimization_research.multi_poi.algorithms.genetic_algorithm import (
    genetic_algorithm
)


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CASES_FILE = os.path.join(
    BASE_DIR,
    "results",
    "benchmark_cases",
    "benchmark_cases.csv"
)

MATRIX_DIR = os.path.join(
    BASE_DIR,
    "results",
    "distance_matrices"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "results",
    "genetic_algorithm"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_list(value):
    value = str(value).strip()

    if value.startswith("[") and value.endswith("]"):
        return [
            str(x)
            for x in ast.literal_eval(value)
        ]

    if "|" in value:
        return [
            x.strip()
            for x in value.split("|")
        ]

    if "," in value:
        return [
            x.strip()
            for x in value.split(",")
        ]

    return [value]


def load_matrix(case_id):

    path = os.path.join(
        MATRIX_DIR,
        f"{case_id}_distance_matrix.csv"
    )

    matrix = pd.read_csv(
        path,
        index_col=0
    )

    matrix.index = matrix.index.astype(str)
    matrix.columns = matrix.columns.astype(str)

    return matrix


def run_benchmark():

    cases = pd.read_csv(CASES_FILE)

    results = []

    print("=" * 70)
    print("GENETIC ALGORITHM BENCHMARK")
    print("=" * 70)

    for _, case in cases.iterrows():

        case_id = str(case["case_id"])
        profile = case["interest_profile"]
        poi_count = int(case["poi_count"])

        poi_ids = parse_list(
            case["poi_ids"]
        )

        start_poi = str(
            case["start_poi_id"]
        )

        end_poi = str(
            case["end_poi_id"]
        )

        matrix = load_matrix(case_id)

        # -----------------------------------------------------
        # Case consistency check
        # -----------------------------------------------------

        if len(poi_ids) != poi_count:
            raise ValueError(
                f"{case_id}: Expected {poi_count} POIs, "
                f"but parsed {len(poi_ids)} POIs."
            )

        print(f"\nRunning {case_id}...")
        print(f"  Profile: {profile}")
        print(f"  POIs: {poi_count}")

        result = genetic_algorithm(
            distance_matrix=matrix,
            poi_ids=poi_ids,
            start_poi=start_poi,
            end_poi=end_poi,
            seed=42,
            population_size=50,
            generations=100,
            mutation_rate=0.10,
            elite_size=2,
            tournament_size=3
        )

        results.append({
            "case_id": case_id,
            "interest_profile": profile,
            "poi_count": poi_count,
            "geographic_spread_km": float(
                case["geographic_spread_km"]
            ),
            "algorithm": result["algorithm"],
            "feasible": result["feasible"],
            "distance_km": result["distance_km"],
            "execution_time_ms": result["execution_time_ms"],
            "candidate_evaluations": result["nodes_evaluated"],
            "route_length": len(result["route"])
        })

        if result["feasible"]:

            print(
                f"  Distance: "
                f"{result['distance_km']:.6f} km"
            )

            print(
                f"  Time: "
                f"{result['execution_time_ms']:.4f} ms"
            )

            print(
                f"  Candidate evaluations: "
                f"{result['nodes_evaluated']}"
            )

        else:
            print("  Infeasible")

    df = pd.DataFrame(results)

    # =========================================================
    # OVERALL SUMMARY
    # =========================================================

    feasible = df[
        df["feasible"] == True
    ]

    summary = {
        "total_cases": len(df),
        "feasible_cases": len(feasible),
        "infeasible_cases": len(df) - len(feasible),
        "avg_execution_time_ms": feasible[
            "execution_time_ms"
        ].mean(),
        "median_execution_time_ms": feasible[
            "execution_time_ms"
        ].median(),
        "min_execution_time_ms": feasible[
            "execution_time_ms"
        ].min(),
        "max_execution_time_ms": feasible[
            "execution_time_ms"
        ].max(),
        "avg_distance_km": feasible[
            "distance_km"
        ].mean(),
        "median_distance_km": feasible[
            "distance_km"
        ].median(),
        "avg_candidate_evaluations": feasible[
            "candidate_evaluations"
        ].mean()
    }

    summary_df = pd.DataFrame(
        [summary]
    )

    # =========================================================
    # BY POI SIZE
    # =========================================================

    by_size = (
        feasible
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

            avg_distance_km=(
                "distance_km",
                "mean"
            ),

            median_distance_km=(
                "distance_km",
                "median"
            ),

            avg_candidate_evaluations=(
                "candidate_evaluations",
                "mean"
            )
        )
        .reset_index()
    )

    # =========================================================
    # BY INTEREST PROFILE
    # =========================================================

    by_profile = (
        feasible
        .groupby("interest_profile")
        .agg(
            cases=("case_id", "count"),

            avg_execution_time_ms=(
                "execution_time_ms",
                "mean"
            ),

            avg_distance_km=(
                "distance_km",
                "mean"
            ),

            avg_geographic_spread_km=(
                "geographic_spread_km",
                "mean"
            ),

            avg_candidate_evaluations=(
                "candidate_evaluations",
                "mean"
            )
        )
        .reset_index()
    )

    # =========================================================
    # SAVE RESULTS
    # =========================================================

    df.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "genetic_algorithm_benchmark.csv"
        ),
        index=False
    )

    summary_df.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "genetic_algorithm_summary.csv"
        ),
        index=False
    )

    by_size.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "genetic_algorithm_by_size.csv"
        ),
        index=False
    )

    by_profile.to_csv(
        os.path.join(
            OUTPUT_DIR,
            "genetic_algorithm_by_profile.csv"
        ),
        index=False
    )

    # =========================================================
    # PRINT SUMMARY
    # =========================================================

    print("\n" + "=" * 70)
    print("GENETIC ALGORITHM BENCHMARK SUMMARY")
    print("=" * 70)

    print(
        f"Total cases       : "
        f"{summary['total_cases']}"
    )

    print(
        f"Feasible cases    : "
        f"{summary['feasible_cases']}"
    )

    print(
        f"Infeasible cases  : "
        f"{summary['infeasible_cases']}"
    )

    print(
        f"Average time      : "
        f"{summary['avg_execution_time_ms']:.6f} ms"
    )

    print(
        f"Median time       : "
        f"{summary['median_execution_time_ms']:.6f} ms"
    )

    print(
        f"Min time          : "
        f"{summary['min_execution_time_ms']:.6f} ms"
    )

    print(
        f"Max time          : "
        f"{summary['max_execution_time_ms']:.6f} ms"
    )

    print(
        f"Average distance  : "
        f"{summary['avg_distance_km']:.6f} km"
    )

    print(
        f"Median distance   : "
        f"{summary['median_distance_km']:.6f} km"
    )

    print(
        f"Average candidate evaluations: "
        f"{summary['avg_candidate_evaluations']:.2f}"
    )

    print("\nBy POI size:")
    print(
        by_size.to_string(index=False)
    )

    print("\nBy interest profile:")
    print(
        by_profile.to_string(index=False)
    )

    print("\nResults saved to:")
    print(OUTPUT_DIR)


if __name__ == "__main__":
    run_benchmark()