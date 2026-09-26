import os
import ast
import math
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


def validate_result(
    result,
    matrix,
    poi_ids,
    start_poi,
    end_poi
):

    if not result["feasible"]:
        return False, "Unexpected infeasible result"

    route = result["route"]

    # ---------------------------------------------------------
    # Start / end
    # ---------------------------------------------------------

    if route[0] != start_poi:
        return False, "Incorrect start POI"

    if route[-1] != end_poi:
        return False, "Incorrect end POI"

    # ---------------------------------------------------------
    # Route length
    # ---------------------------------------------------------

    if len(route) != len(poi_ids):
        return False, "Incorrect route length"

    # ---------------------------------------------------------
    # Every POI exactly once
    # ---------------------------------------------------------

    if len(set(route)) != len(route):
        return False, "Duplicate POI"

    if set(route) != set(poi_ids):
        return False, "POI set mismatch"

    # ---------------------------------------------------------
    # Directed edge feasibility
    # ---------------------------------------------------------

    actual_distance = 0.0

    for i in range(len(route) - 1):

        source = route[i]
        target = route[i + 1]

        distance = float(
            matrix.loc[
                source,
                target
            ]
        )

        if not math.isfinite(distance):
            return False, (
                f"Unreachable leg: "
                f"{source} -> {target}"
            )

        actual_distance += distance

    # ---------------------------------------------------------
    # Distance validation
    # ---------------------------------------------------------

    reported_distance = float(
        result["distance_km"]
    )

    if not math.isclose(
        reported_distance,
        actual_distance,
        rel_tol=1e-9,
        abs_tol=1e-9
    ):
        return False, (
            f"Distance mismatch: "
            f"reported={reported_distance}, "
            f"actual={actual_distance}"
        )

    return True, "PASS"


def main():

    cases = pd.read_csv(
        CASES_FILE
    )

    total = len(cases)
    passed = 0
    failed = 0

    print("=" * 70)
    print("GENETIC ALGORITHM CORRECTNESS TEST")
    print("=" * 70)

    for _, case in cases.iterrows():

        case_id = str(
            case["case_id"]
        )

        poi_ids = parse_list(
            case["poi_ids"]
        )

        start_poi = str(
            case["start_poi_id"]
        )

        end_poi = str(
            case["end_poi_id"]
        )

        matrix = load_matrix(
            case_id
        )

        print(
            f"\nTesting {case_id}..."
        )

        result = genetic_algorithm(
            distance_matrix=matrix,
            poi_ids=poi_ids,
            start_poi=start_poi,
            end_poi=end_poi,
            seed=42
        )

        # -----------------------------------------------------
        # Expected infeasible case
        # -----------------------------------------------------

        if case_id == "M002":

            if not result["feasible"]:

                print(
                    "  Expected infeasible case"
                )

                passed += 1

            else:

                print(
                    "  FAIL: M002 should be infeasible"
                )

                failed += 1

            continue

        # -----------------------------------------------------
        # Validate feasible case
        # -----------------------------------------------------

        valid, message = validate_result(
            result,
            matrix,
            poi_ids,
            start_poi,
            end_poi
        )

        if valid:

            print("  PASS")

            print(
                f"  Distance: "
                f"{result['distance_km']:.6f} km"
            )

            print(
                f"  Route length: "
                f"{len(result['route'])}"
            )

            passed += 1

        else:

            print(
                f"  FAIL: {message}"
            )

            failed += 1

    accuracy = (
        passed / total * 100
        if total > 0
        else 0
    )

    print("\n" + "=" * 70)
    print("GENETIC ALGORITHM TEST SUMMARY")
    print("=" * 70)

    print(
        f"Total cases : {total}"
    )

    print(
        f"Passed      : {passed}"
    )

    print(
        f"Failed      : {failed}"
    )

    print(
        f"Validation accuracy: "
        f"{accuracy:.2f}%"
    )

    if failed == 0:

        print(
            "\nALL GENETIC ALGORITHM "
            "CORRECTNESS TESTS PASSED"
        )

    else:

        print(
            "\nGENETIC ALGORITHM "
            "CORRECTNESS TEST FAILED"
        )


if __name__ == "__main__":
    main()