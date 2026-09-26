import pandas as pd
import re
from difflib import SequenceMatcher
from math import radians
from scipy.spatial import cKDTree


INPUT_FILE = "route_optimization_research/multi_poi/results/Hyderabad_Itinerary_POIs.csv"
OUTPUT_FILE = "route_optimization_research/multi_poi/results/poi_duplicate_analysis.csv"

DISTANCE_THRESHOLD_M = 100


def normalize_name(name):
    if pd.isna(name):
        return ""

    name = str(name).lower()
    name = re.sub(r"[^a-z0-9\s]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()

    return name


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def meters_to_latlon_radius(distance_m):
    """
    Approximate conversion of meters to degrees.
    Used only for KD-tree candidate generation.
    """
    lat_radius = distance_m / 111320
    lon_radius = distance_m / 105000

    return lat_radius, lon_radius


df = pd.read_csv(INPUT_FILE)

candidates = df[
    df["is_itinerary_candidate"] == True
].copy()

candidates = candidates.reset_index(drop=True)

candidates["normalized_name"] = candidates["name"].apply(
    normalize_name
)


print("=" * 60)
print("POI DUPLICATE ANALYSIS")
print("=" * 60)

print(f"Total itinerary candidates : {len(candidates)}")
print(f"Distance threshold         : {DISTANCE_THRESHOLD_M} meters")
print()


# ---------------------------------------------------------
# Build spatial index
# ---------------------------------------------------------

# Convert latitude/longitude approximately to meters.
# This makes the KD-tree distance approximately meaningful.
lat_mean = candidates["latitude"].mean()

lat_scale = 111320
lon_scale = 111320 * __import__("math").cos(
    radians(lat_mean)
)

x = candidates["longitude"].values * lon_scale
y = candidates["latitude"].values * lat_scale

coordinates = list(zip(x, y))

tree = cKDTree(coordinates)


# ---------------------------------------------------------
# Find nearby candidate pairs
# ---------------------------------------------------------

pairs = tree.query_pairs(
    r=DISTANCE_THRESHOLD_M
)

print(f"Nearby pairs found         : {len(pairs)}")
print()


results = []


for i, j in pairs:

    a = candidates.iloc[i]
    b = candidates.iloc[j]

    dx = x[i] - x[j]
    dy = y[i] - y[j]

    distance_m = (dx ** 2 + dy ** 2) ** 0.5

    name_similarity = similarity(
        a["normalized_name"],
        b["normalized_name"]
    )

    same_category = (
        a["itinerary_category"]
        == b["itinerary_category"]
    )

    if name_similarity >= 0.80 and same_category:
        decision = "Potential Duplicate"

    elif name_similarity >= 0.90:
        decision = "Potential Duplicate"

    else:
        decision = "Likely Distinct"

    results.append({
        "poi_a": a["poi_id"],
        "poi_b": b["poi_id"],
        "name_a": a["name"],
        "name_b": b["name"],
        "category_a": a["category"],
        "category_b": b["category"],
        "itinerary_category_a": a["itinerary_category"],
        "itinerary_category_b": b["itinerary_category"],
        "latitude_a": a["latitude"],
        "longitude_a": a["longitude"],
        "latitude_b": b["latitude"],
        "longitude_b": b["longitude"],
        "distance_m": round(distance_m, 3),
        "name_similarity": round(name_similarity, 3),
        "same_itinerary_category": same_category,
        "decision": decision
    })


result_df = pd.DataFrame(results)


# ---------------------------------------------------------
# Save results
# ---------------------------------------------------------

if len(result_df) > 0:

    result_df = result_df.sort_values(
        [
            "decision",
            "distance_m",
            "name_similarity"
        ],
        ascending=[
            True,
            True,
            False
        ]
    )

result_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

print("=" * 60)
print("RESULTS")
print("=" * 60)

print(f"Nearby POI pairs analyzed : {len(result_df)}")

if len(result_df) > 0:

    print("\nDecision summary:")
    print(
        result_df["decision"]
        .value_counts()
        .to_string()
    )

    print("\nPotential duplicates:")

    potential = result_df[
        result_df["decision"]
        == "Potential Duplicate"
    ]

    if len(potential) > 0:

        print(
            potential[
                [
                    "poi_a",
                    "poi_b",
                    "name_a",
                    "name_b",
                    "distance_m",
                    "name_similarity",
                    "same_itinerary_category"
                ]
            ].to_string(index=False)
        )

    else:
        print("None found.")

print()
print("Saved:")
print(OUTPUT_FILE)