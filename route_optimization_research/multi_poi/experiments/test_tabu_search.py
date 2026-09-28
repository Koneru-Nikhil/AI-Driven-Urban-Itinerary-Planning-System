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
    """
    benchmark_cases.csv stores poi_ids as a Python-style
    list representation, for example:

    ["HYD001", "HYD002", "HYD003"]

    Use ast.literal_eval instead of split("|").
    """

    parsed = ast.literal_eval(value)

    return [
        str(poi)
        for poi in parsed
    ]


def route_distance(
    route,
    matrix,
):
    total = 0.0

    for i in range(len(route) - 1):

        source = str(route[i])
        target = str(route[i + 1])

        try:
            distance = float(
                matrix.loc[source, target]
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return math.inf

        if not math.isfinite(distance):
            return math.inf

        total += distance

    return total


def validate_result(
    row,
    result,
    matrix,
):
    poi_ids = parse_poi_ids(
        row["poi_ids"]
    )

    start_poi = str(
        row["start_poi_id"]
    )

    end_poi = str(
        row["end_poi_id"]
    )

    # ---------------------------------------------------------
    # Expected infeasible case
    # ---------------------------------------------------------
    if not result["feasible"]:

        if row["case_id"] == "M002":
            return True, "Expected infeasible case"

        return False, "Unexpected infeasible result"

    route = [
        str(poi)
        for poi in result["route"]
    ]

    # ---------------------------------------------------------
    # Start validation
    # ---------------------------------------------------------
    if len(route) == 0:
        return False, "Empty route"

    if route[0] != start_poi:
        return False, (
            "Route does not start at required POI"
        )

    # ---------------------------------------------------------
    # End validation
    # ---------------------------------------------------------
    if route[-1] != end_poi:
        return False, (
            "Route does not end at required POI"
        )

    # ---------------------------------------------------------
    # Route length
    # ---------------------------------------------------------
    if len(route) != len(poi_ids):
        return False, (
            f"Incorrect route length: "
            f"{len(route)} != {len(poi_ids)}"
        )

    # ---------------------------------------------------------
    # Uniqueness
    # ---------------------------------------------------------
    if len(set(route)) != len(route):
        return False, (
            "Route contains duplicate POIs"
        )

    # ---------------------------------------------------------
    # All required POIs
    # ---------------------------------------------------------
    if set(route) != set(poi_ids):
        return False, (
            "Route does not contain exactly "
            "the required POIs"
        )

    # ---------------------------------------------------------
    # Directed-leg validation
    # ---------------------------------------------------------
    for i in range(len(route) - 1):

        source = route[i]
        target = route[i + 1]

        try:
            distance = float(
                matrix.loc[source, target]
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return False, (
                f"Missing matrix entry: "
                f"{source} -> {target}"
            )

        if not math.isfinite(distance):
            return False, (
                f"Unreachable route leg: "
                f"{source} -> {target}"
            )

    # ---------------------------------------------------------
    # Distance validation
    # ---------------------------------------------------------
    actual_distance = route_distance(
        route,
        matrix,
    )

    reported_distance = float(
        result["distance_km"]
    )

    if not math.isclose(
        actual_distance,
        reported_distance,
        rel_tol=1e-9,
        abs_tol=1e-9,
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

    total = 0
    passed = 0
    failed = 0

    print("=" * 70)
    print("TABU SEARCH CORRECTNESS TEST")
    print("=" * 70)

    for _, row in cases.iterrows():

        total += 1

        case_id = str(
            row["case_id"]
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

        valid, message = validate_result(
            row,
            result,
            matrix,
        )

        if valid:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        distance = result["distance_km"]

        if math.isfinite(distance):
            distance_text = (
                f"{distance:.6f} km"
            )
        else:
            distance_text = "inf km"

        print(
            f"{case_id}: {status} | "
            f"distance={distance_text} | "
            f"feasible={result['feasible']} | "
            f"{message}"
        )

    accuracy = (
        passed / total * 100
        if total > 0
        else 0.0
    )

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Total cases     : {total}")
    print(f"Passed          : {passed}")
    print(f"Failed          : {failed}")
    print(f"Accuracy        : {accuracy:.2f}%")

    if failed == 0:
        print()
        print(
            "ALL TABU SEARCH "
            "CORRECTNESS CHECKS PASSED"
        )
    else:
        print()
        print(
            "TABU SEARCH "
            "CORRECTNESS CHECK FAILED"
        )


if __name__ == "__main__":
    main()