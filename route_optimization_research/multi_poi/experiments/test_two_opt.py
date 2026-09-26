import json
from pathlib import Path

import pandas as pd

from route_optimization_research.multi_poi.algorithms.two_opt import (
    two_opt,
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


def validate_route(
    route,
    poi_ids,
    start_poi,
    end_poi,
    matrix,
):
    """
    Validate:
    - correct start
    - correct end
    - every POI exactly once
    - every leg reachable
    - route distance correct
    """

    if not route:
        return False, "Empty route"

    if route[0] != start_poi:
        return False, "Incorrect start"

    if route[-1] != end_poi:
        return False, "Incorrect end"

    if len(route) != len(poi_ids):
        return False, "Incorrect route length"

    if len(set(route)) != len(route):
        return False, "Duplicate POI"

    if set(route) != set(poi_ids):
        return False, "POI set mismatch"

    total_distance = 0.0

    for i in range(
        len(route) - 1
    ):

        source = route[i]
        target = route[i + 1]

        distance = matrix.loc[
            source,
            target,
        ]

        if pd.isna(distance):
            return False, (
                f"Unreachable leg: "
                f"{source} -> {target}"
            )

        total_distance += float(
            distance
        )

    return True, total_distance


# ============================================================
# TEST
# ============================================================

print("=" * 70)
print("2-OPT CORRECTNESS TEST")
print("=" * 70)

cases = pd.read_csv(
    CASES_FILE
)

passed = 0
failed = 0

for _, case in cases.iterrows():

    case_id = case["case_id"]

    print()
    print(
        f"Testing {case_id}..."
    )

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

    result = two_opt(
        distance_matrix=matrix,
        poi_ids=poi_ids,
        start_poi=start_poi,
        end_poi=end_poi,
    )

    # M002 is intentionally infeasible.
    if not result["feasible"]:

        if case_id == "M002":

            print(
                "  Expected infeasible case"
            )

            passed += 1

        else:

            print(
                "  FAIL: unexpected infeasible route"
            )

            failed += 1

        continue

    valid, detail = validate_route(
        result["route"],
        poi_ids,
        start_poi,
        end_poi,
        matrix,
    )

    if not valid:

        print(
            "  FAIL:",
            detail
        )

        failed += 1
        continue

    expected_distance = float(
        detail
    )

    difference = abs(
        result["distance_km"]
        - expected_distance
    )

    if difference > 1e-9:

        print(
            "  FAIL: distance mismatch"
        )

        failed += 1
        continue

    print(
        "  PASS"
    )

    print(
        f"  Distance: "
        f"{result['distance_km']:.6f} km"
    )

    print(
        f"  Route length: "
        f"{len(result['route'])}"
    )

    passed += 1


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("2-OPT TEST SUMMARY")
print("=" * 70)

print(
    "Total cases :",
    len(cases),
)

print(
    "Passed      :",
    passed,
)

print(
    "Failed      :",
    failed,
)

accuracy = (
    passed / len(cases) * 100
    if len(cases)
    else 0
)

print(
    f"Validation accuracy: "
    f"{accuracy:.2f}%"
)

if failed == 0:

    print()
    print(
        "ALL 2-OPT CORRECTNESS TESTS PASSED"
    )

else:

    print()
    print(
        "2-OPT CORRECTNESS TEST FAILED"
    )