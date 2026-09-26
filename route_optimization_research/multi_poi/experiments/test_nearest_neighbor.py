import math
from pathlib import Path

import pandas as pd

from route_optimization_research.multi_poi.algorithms.nearest_neighbor import (
    nearest_neighbor,
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
    Validate that:

    1. Route starts correctly.
    2. Route ends correctly.
    3. Every POI is visited exactly once.
    4. No extra POIs are included.
    5. Every consecutive leg is reachable.
    6. Reported distance matches matrix distance.
    """

    if not route:
        return False, "Empty route"

    if route[0] != start_poi:
        return False, "Incorrect start"

    if route[-1] != end_poi:
        return False, "Incorrect end"

    # Every POI must occur exactly once.
    if len(route) != len(poi_ids):
        return False, (
            f"Route length {len(route)} "
            f"!= POI count {len(poi_ids)}"
        )

    if len(set(route)) != len(route):
        return False, "Duplicate POI in route"

    if set(route) != set(poi_ids):
        return False, "Route POI set mismatch"

    # Validate every leg.
    total_distance = 0.0

    for i in range(
        len(route) - 1
    ):

        source = route[i]
        target = route[i + 1]

        distance = matrix.loc[
            source,
            target
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
# RUN TESTS
# ============================================================

print("=" * 70)
print("NEAREST NEIGHBOR CORRECTNESS TEST")
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

    poi_ids = eval(
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
        index_col=0
    )

    matrix = matrix.apply(
        pd.to_numeric,
        errors="coerce"
    )

    result = nearest_neighbor(
        distance_matrix=matrix,
        poi_ids=poi_ids,
        start_poi=start_poi,
        end_poi=end_poi,
    )

    if not result["feasible"]:

        # M002 is intentionally directed-infeasible
        # for the fixed start, so an infeasible result
        # is expected rather than an algorithm failure.
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

    distance_difference = abs(
        result["distance_km"]
        - expected_distance
    )

    if distance_difference > 1e-9:

        print(
            "  FAIL: distance mismatch"
        )

        print(
            "  Reported:",
            result["distance_km"]
        )

        print(
            "  Calculated:",
            expected_distance
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
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("NEAREST NEIGHBOR TEST SUMMARY")
print("=" * 70)

print(
    "Total cases :",
    len(cases)
)

print(
    "Passed      :",
    passed
)

print(
    "Failed      :",
    failed
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
        "ALL NEAREST NEIGHBOR "
        "CORRECTNESS TESTS PASSED"
    )

else:

    print()
    print(
        "NEAREST NEIGHBOR "
        "CORRECTNESS TEST FAILED"
    )