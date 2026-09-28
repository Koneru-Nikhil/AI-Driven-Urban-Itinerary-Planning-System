import ast
import math
import os

import pandas as pd

from route_optimization_research.multi_poi.algorithms.ant_colony_optimization import (
    ant_colony_optimization,
    route_distance,
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


def load_distance_matrix(case_id):

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


def validate_route(
    route,
    poi_ids,
    start_poi,
    end_poi,
    distance_matrix,
    reported_distance
):

    # --------------------------------------------------
    # 1. Route must exist
    # --------------------------------------------------

    if not route:

        return False, "Route is empty"


    # --------------------------------------------------
    # 2. Correct start
    # --------------------------------------------------

    if route[0] != start_poi:

        return False, "Incorrect start POI"


    # --------------------------------------------------
    # 3. Correct end
    # --------------------------------------------------

    if route[-1] != end_poi:

        return False, "Incorrect end POI"


    # --------------------------------------------------
    # 4. Correct number of POIs
    # --------------------------------------------------

    if len(route) != len(poi_ids):

        return False, (
            f"Incorrect route length: "
            f"{len(route)} instead of {len(poi_ids)}"
        )


    # --------------------------------------------------
    # 5. No duplicate POIs
    # --------------------------------------------------

    if len(set(route)) != len(route):

        return False, "Duplicate POI found"


    # --------------------------------------------------
    # 6. No missing POIs
    # --------------------------------------------------

    if set(route) != set(poi_ids):

        return False, "Some POIs are missing"


    # --------------------------------------------------
    # 7. Every consecutive leg must be reachable
    # --------------------------------------------------

    for i in range(len(route) - 1):

        source = route[i]
        target = route[i + 1]

        distance = distance_matrix.get(
            (source, target),
            math.inf
        )

        if not math.isfinite(distance):

            return False, (
                f"Unreachable leg: "
                f"{source} -> {target}"
            )


    # --------------------------------------------------
    # 8. Recalculate route distance independently
    # --------------------------------------------------

    calculated_distance = route_distance(
        route,
        distance_matrix
    )

    if not math.isfinite(calculated_distance):

        return False, "Calculated distance is infinite"


    # --------------------------------------------------
    # 9. Compare algorithm distance with matrix distance
    # --------------------------------------------------

    distance_difference = abs(
        reported_distance
        - calculated_distance
    )

    if distance_difference > 1e-9:

        return False, (
            f"Distance mismatch: "
            f"reported={reported_distance}, "
            f"calculated={calculated_distance}"
        )


    return True, "PASS"


def main():

    cases = pd.read_csv(
        CASES_FILE
    )

    total_cases = len(cases)

    passed = 0
    failed = 0

    feasible_cases = 0
    expected_infeasible_cases = 0

    print("=" * 75)
    print("ANT COLONY OPTIMIZATION - CORRECTNESS VALIDATION")
    print("=" * 75)

    for _, row in cases.iterrows():

        case_id = row["case_id"]

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

        distance_matrix = load_distance_matrix(
            case_id
        )

        result = ant_colony_optimization(
            distance_matrix=distance_matrix,
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

        # --------------------------------------------------
        # M002 is known to be infeasible
        # --------------------------------------------------

        if case_id == "M002":

            expected_infeasible_cases += 1

            if not result["feasible"]:

                print(
                    f"{case_id}: PASS "
                    f"(expected infeasible)"
                )

                passed += 1

            else:

                print(
                    f"{case_id}: FAIL "
                    f"(expected infeasible but ACO "
                    f"returned a feasible route)"
                )

                failed += 1

            continue


        # --------------------------------------------------
        # All other cases should be feasible
        # --------------------------------------------------

        feasible_cases += 1

        if not result["feasible"]:

            print(
                f"{case_id}: FAIL "
                f"(unexpected infeasible)"
            )

            failed += 1
            continue


        # --------------------------------------------------
        # Validate route structure
        # --------------------------------------------------

        valid, message = validate_route(
            route=result["route"],
            poi_ids=poi_ids,
            start_poi=start_poi,
            end_poi=end_poi,
            distance_matrix=distance_matrix,
            reported_distance=result["distance_km"]
        )

        if not valid:

            print(
                f"{case_id}: FAIL - {message}"
            )

            failed += 1
            continue


        print(
            f"{case_id}: PASS | "
            f"Distance = "
            f"{result['distance_km']:.6f} km | "
            f"Evaluations = "
            f"{result['nodes_evaluated']}"
        )

        passed += 1


    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    accuracy = (
        passed / total_cases * 100
        if total_cases > 0
        else 0
    )

    print()
    print("=" * 75)
    print("VALIDATION SUMMARY")
    print("=" * 75)

    print(
        f"Total cases              : "
        f"{total_cases}"
    )

    print(
        f"Feasible cases           : "
        f"{feasible_cases}"
    )

    print(
        f"Expected infeasible     : "
        f"{expected_infeasible_cases}"
    )

    print(
        f"Passed                   : "
        f"{passed}"
    )

    print(
        f"Failed                   : "
        f"{failed}"
    )

    print(
        f"Validation accuracy      : "
        f"{accuracy:.2f}%"
    )

    if failed == 0:

        print()
        print(
            "ALL ANT COLONY OPTIMIZATION "
            "CHECKS PASSED"
        )

    else:

        print()
        print(
            "SOME ANT COLONY OPTIMIZATION "
            "CHECKS FAILED"
        )


if __name__ == "__main__":
    main()