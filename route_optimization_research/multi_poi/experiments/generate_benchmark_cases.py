import json
import random
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = (
    "route_optimization_research/"
    "multi_poi/results/"
    "Hyderabad_Itinerary_POIs.csv"
)

MAPPING_FILE = (
    "route_optimization_research/"
    "multi_poi/results/"
    "Hyderabad_Itinerary_POI_Road_Mapping.csv"
)

OUTPUT_DIR = Path(
    "route_optimization_research/"
    "multi_poi/results/benchmark_cases"
)

SEED = 42

ITINERARY_SIZES = [10, 20, 30]


# Single-interest profiles
SINGLE_INTERESTS = [
    "Food",
    "Shopping",
    "Religion",
    "Nature & Outdoors",
    "Culture & Heritage",
    "Entertainment",
    "Recreation & Sports",
]


# Multi-interest profiles
MULTI_INTERESTS = [
    ["Food", "Shopping"],
    ["Culture & Heritage", "Religion"],
    ["Food", "Entertainment"],
    ["Nature & Outdoors", "Recreation & Sports"],
    ["Culture & Heritage", "Food"],
]


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("MULTI-POI BENCHMARK CASE GENERATOR")
print("=" * 70)

pois = pd.read_csv(INPUT_FILE)
mapping = pd.read_csv(MAPPING_FILE)

print("Raw/preprocessed POIs:", len(pois))
print("Mapped POIs:", len(mapping))


# Merge mapping information
mapping_columns = [
    "poi_id",
    "nearest_road_node",
    "distance_to_road_m",
    "mapping_quality",
]

mapping_small = mapping[
    [c for c in mapping_columns if c in mapping.columns]
].copy()

pois = pois.merge(
    mapping_small,
    on="poi_id",
    how="inner",
)

# Only itinerary candidates
if "is_itinerary_candidate" in pois.columns:
    pois = pois[
        pois["is_itinerary_candidate"] == True
    ].copy()

# Remove rows without road mapping
pois = pois.dropna(
    subset=["nearest_road_node"]
).copy()

pois["nearest_road_node"] = (
    pois["nearest_road_node"]
    .astype("int64")
)

pois = pois.reset_index(drop=True)

print(
    "Usable itinerary POIs:",
    len(pois)
)


# ============================================================
# REPRODUCIBLE RANDOM GENERATOR
# ============================================================

rng = random.Random(SEED)

cases = []


def geographic_spread_km(case_df):
    """
    Approximate geographic spread using the maximum
    pairwise haversine distance.
    """

    import math

    lat = case_df["latitude"].tolist()
    lon = case_df["longitude"].tolist()

    max_distance = 0.0

    for i in range(len(lat)):
        for j in range(i + 1, len(lat)):

            lat1 = math.radians(lat[i])
            lat2 = math.radians(lat[j])

            dlat = math.radians(
                lat[j] - lat[i]
            )

            dlon = math.radians(
                lon[j] - lon[i]
            )

            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(lat1)
                * math.cos(lat2)
                * math.sin(dlon / 2) ** 2
            )

            distance = (
                6371.0
                * 2
                * math.atan2(
                    math.sqrt(a),
                    math.sqrt(1 - a),
                )
            )

            max_distance = max(
                max_distance,
                distance,
            )

    return max_distance


def create_case(
    case_id,
    profile,
    poi_count,
):
    """
    Generate one reproducible benchmark case.
    """

    profile_set = set(profile)

    candidates = pois[
        pois["itinerary_category"].isin(
            profile_set
        )
    ].copy()

    if len(candidates) < poi_count:
        print(
            f"SKIPPING {case_id}: "
            f"only {len(candidates)} candidates "
            f"for {poi_count} POIs"
        )
        return None

    # Random but reproducible selection
    selected_indices = rng.sample(
        list(candidates.index),
        poi_count,
    )

    case_df = candidates.loc[
        selected_indices
    ].copy()

    case_df = case_df.reset_index(
        drop=True
    )

    # Fixed start and end:
    # first and last POIs in the generated case.
    start_poi = case_df.iloc[0]
    end_poi = case_df.iloc[-1]

    spread = geographic_spread_km(
        case_df
    )

    # Count distinct road nodes
    unique_nodes = (
        case_df["nearest_road_node"]
        .nunique()
    )

    shared_node_count = (
        len(case_df)
        - unique_nodes
    )

    record = {
        "case_id": case_id,
        "interest_profile": " + ".join(profile),
        "poi_count": poi_count,
        "poi_ids": json.dumps(
            case_df["poi_id"].tolist()
        ),
        "poi_names": json.dumps(
            case_df["name"].tolist()
        ),
        "poi_categories": json.dumps(
            case_df[
                "itinerary_category"
            ].tolist()
        ),
        "road_nodes": json.dumps(
            case_df[
                "nearest_road_node"
            ].astype(int).tolist()
        ),
        "start_poi_id": start_poi["poi_id"],
        "end_poi_id": end_poi["poi_id"],
        "start_road_node": int(
            start_poi["nearest_road_node"]
        ),
        "end_road_node": int(
            end_poi["nearest_road_node"]
        ),
        "geographic_spread_km": round(
            spread,
            4,
        ),
        "unique_road_nodes": unique_nodes,
        "shared_road_node_count": shared_node_count,
    }

    return record


# ============================================================
# GENERATE SINGLE-INTEREST CASES
# ============================================================

print()
print("Generating single-interest cases...")

case_number = 1

for interest in SINGLE_INTERESTS:

    for poi_count in ITINERARY_SIZES:

        case_id = (
            f"S{case_number:03d}"
        )

        record = create_case(
            case_id=case_id,
            profile=[interest],
            poi_count=poi_count,
        )

        if record is not None:
            cases.append(record)
            case_number += 1


# ============================================================
# GENERATE MULTI-INTEREST CASES
# ============================================================

print()
print("Generating multi-interest cases...")

multi_number = 1

for profile in MULTI_INTERESTS:

    for poi_count in ITINERARY_SIZES:

        case_id = (
            f"M{multi_number:03d}"
        )

        record = create_case(
            case_id=case_id,
            profile=profile,
            poi_count=poi_count,
        )

        if record is not None:
            cases.append(record)
            multi_number += 1


# ============================================================
# SAVE
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

cases_df = pd.DataFrame(cases)

output_file = (
    OUTPUT_DIR
    / "benchmark_cases.csv"
)

cases_df.to_csv(
    output_file,
    index=False,
)

print()
print("=" * 70)
print("BENCHMARK GENERATION COMPLETE")
print("=" * 70)

print(
    "Total benchmark cases:",
    len(cases_df),
)

print(
    "Output:",
    output_file,
)

print()
print(
    cases_df[
        [
            "case_id",
            "interest_profile",
            "poi_count",
            "geographic_spread_km",
            "unique_road_nodes",
            "shared_road_node_count",
        ]
    ].to_string(index=False)
)