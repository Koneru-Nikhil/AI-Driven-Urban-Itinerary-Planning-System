import json
from pathlib import Path

import pandas as pd
import numpy as np


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
    "validation"
)


# ============================================================
# LOAD CASES
# ============================================================

print("=" * 70)
print("MULTI-POI BENCHMARK VALIDATION")
print("=" * 70)

cases = pd.read_csv(
    CASES_FILE
)

print(
    "Benchmark cases:",
    len(cases)
)


# ============================================================
# VALIDATION FUNCTION
# ============================================================

def validate_case(case):

    case_id = case["case_id"]

    poi_ids = json.loads(
        case["poi_ids"]
    )

    poi_count = len(poi_ids)

    matrix_file = (
        MATRIX_DIR
        / f"{case_id}_distance_matrix.csv"
    )

    result = {
        "case_id": case_id,
        "interest_profile": case[
            "interest_profile"
        ],
        "poi_count": poi_count,
        "unique_road_nodes": int(
            case["unique_road_nodes"]
        ),
        "shared_road_node_count": int(
            case["shared_road_node_count"]
        ),
        "geographic_spread_km": float(
            case["geographic_spread_km"]
        ),
        "matrix_exists": matrix_file.exists(),
        "matrix_shape_valid": False,
        "diagonal_zero": False,
        "unreachable_pairs": None,
        "reachable_pairs": None,
        "strongly_feasible": False,
        "start_to_all_reachable": False,
        "all_to_end_reachable": False,
        "full_order_feasible": False,
    }

    if not matrix_file.exists():
        return result

    # --------------------------------------------------------
    # Load matrix
    # --------------------------------------------------------

    matrix = pd.read_csv(
        matrix_file,
        index_col=0
    )

    matrix = matrix.apply(
        pd.to_numeric,
        errors="coerce"
    )

    # --------------------------------------------------------
    # Matrix shape
    # --------------------------------------------------------

    result["matrix_shape_valid"] = (
        matrix.shape
        == (poi_count, poi_count)
    )

    # --------------------------------------------------------
    # Diagonal
    # --------------------------------------------------------

    diagonal = np.diag(
        matrix.values
    )

    result["diagonal_zero"] = bool(
        np.allclose(
            diagonal,
            0.0,
            atol=1e-9
        )
    )

    # --------------------------------------------------------
    # Reachability
    # --------------------------------------------------------

    total_entries = (
        poi_count * poi_count
    )

    unreachable = int(
        matrix.isna().sum().sum()
    )

    reachable = (
        total_entries
        - unreachable
    )

    result["unreachable_pairs"] = unreachable
    result["reachable_pairs"] = reachable

    # --------------------------------------------------------
    # Start / end
    # --------------------------------------------------------

    start_poi = case[
        "start_poi_id"
    ]

    end_poi = case[
        "end_poi_id"
    ]

    # --------------------------------------------------------
    # Start can reach every POI?
    # --------------------------------------------------------

    if (
        start_poi in matrix.index
    ):

        start_row = matrix.loc[
            start_poi
        ]

        result[
            "start_to_all_reachable"
        ] = bool(
            start_row.notna().all()
        )

    # --------------------------------------------------------
    # Every POI can reach end?
    # --------------------------------------------------------

    if (
        end_poi in matrix.columns
    ):

        end_column = matrix[
            end_poi
        ]

        result[
            "all_to_end_reachable"
        ] = bool(
            end_column.notna().all()
        )

    # --------------------------------------------------------
    # Full direct feasibility
    # --------------------------------------------------------

    result[
        "strongly_feasible"
    ] = (
        unreachable == 0
    )

    # A simple fixed-order feasibility
    # check using the generated POI order.
    #
    # This is NOT the optimization result.
    # It only checks whether the original
    # benchmark ordering is traversable.

    ordered_pois = poi_ids

    full_order_feasible = True

    for i in range(
        len(ordered_pois) - 1
    ):

        source = ordered_pois[i]
        target = ordered_pois[i + 1]

        value = matrix.loc[
            source,
            target
        ]

        if pd.isna(value):

            full_order_feasible = False
            break

    result[
        "full_order_feasible"
    ] = full_order_feasible

    return result


# ============================================================
# RUN VALIDATION
# ============================================================

results = []

for _, case in cases.iterrows():

    print(
        f"Validating {case['case_id']}..."
    )

    results.append(
        validate_case(case)
    )


validation_df = pd.DataFrame(
    results
)


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_file = (
    OUTPUT_DIR
    / "benchmark_validation.csv"
)

validation_df.to_csv(
    output_file,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

print(
    "Total cases:",
    len(validation_df)
)

print(
    "Matrices present:",
    validation_df[
        "matrix_exists"
    ].sum()
)

print(
    "Valid matrix shapes:",
    validation_df[
        "matrix_shape_valid"
    ].sum()
)

print(
    "Zero diagonals:",
    validation_df[
        "diagonal_zero"
    ].sum()
)

print(
    "Fully reachable cases:",
    validation_df[
        "strongly_feasible"
    ].sum()
)

print(
    "Start reaches all POIs:",
    validation_df[
        "start_to_all_reachable"
    ].sum()
)

print(
    "All POIs reach end:",
    validation_df[
        "all_to_end_reachable"
    ].sum()
)

print(
    "Original-order feasible:",
    validation_df[
        "full_order_feasible"
    ].sum()
)

print()
print(
    validation_df[
        [
            "case_id",
            "poi_count",
            "unreachable_pairs",
            "start_to_all_reachable",
            "all_to_end_reachable",
            "full_order_feasible",
        ]
    ].to_string(index=False)
)

print()
print(
    "Saved:",
    output_file
)