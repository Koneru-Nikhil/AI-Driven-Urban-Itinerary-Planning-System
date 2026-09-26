import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
from math import radians, cos


POI_FILE = (
    "route_optimization_research/"
    "multi_poi/results/"
    "Hyderabad_Itinerary_POIs.csv"
)

ROAD_NODES_FILE = (
    r"C:\Users\nikhi\Downloads\Hyderabad_Route_Research"
    r"\Hyderabad_Largest_Component_Nodes.csv"
)

OUTPUT_FILE = (
    "route_optimization_research/"
    "multi_poi/results/"
    "Hyderabad_Itinerary_POI_Road_Mapping.csv"
)


print("=" * 60)
print("POI → ROAD NETWORK NODE MAPPING")
print("=" * 60)


# ---------------------------------------------------------
# Load POIs
# ---------------------------------------------------------

pois = pd.read_csv(POI_FILE)

pois = pois[
    pois["is_itinerary_candidate"] == True
].copy()

pois.reset_index(drop=True, inplace=True)

print(f"Itinerary POIs : {len(pois)}")


# ---------------------------------------------------------
# Load road nodes
# ---------------------------------------------------------

print("Loading road nodes...")

nodes = pd.read_csv(ROAD_NODES_FILE)

print(f"Road nodes     : {len(nodes)}")


# ---------------------------------------------------------
# Build spatial coordinate system
# ---------------------------------------------------------

# Use an approximate local metre-based coordinate system.
# Hyderabad is small enough for this nearest-neighbour
# mapping step.

mean_lat = nodes["latitude"].mean()

lat_scale = 111320.0
lon_scale = 111320.0 * cos(radians(mean_lat))


road_x = nodes["longitude"].to_numpy() * lon_scale
road_y = nodes["latitude"].to_numpy() * lat_scale

road_coordinates = np.column_stack(
    (road_x, road_y)
)


# ---------------------------------------------------------
# Build KD-tree
# ---------------------------------------------------------

print("Building KD-tree...")

tree = cKDTree(road_coordinates)


# ---------------------------------------------------------
# Convert POI coordinates
# ---------------------------------------------------------

poi_x = pois["longitude"].to_numpy() * lon_scale
poi_y = pois["latitude"].to_numpy() * lat_scale

poi_coordinates = np.column_stack(
    (poi_x, poi_y)
)


# ---------------------------------------------------------
# Find nearest road node
# ---------------------------------------------------------

print("Finding nearest road node for each POI...")

distances, indices = tree.query(
    poi_coordinates,
    k=1
)


# ---------------------------------------------------------
# Create mapping
# ---------------------------------------------------------

mapped = pois[
    [
        "poi_id",
        "osm_id",
        "name",
        "category",
        "itinerary_category",
        "latitude",
        "longitude"
    ]
].copy()


mapped["nearest_road_node"] = (
    nodes.iloc[indices]["node_id"].to_numpy()
)

mapped["distance_to_road_m"] = (
    distances.round(3)
)


# ---------------------------------------------------------
# Quality checks
# ---------------------------------------------------------

print()
print("=" * 60)
print("MAPPING QUALITY")
print("=" * 60)

print(f"Mapped POIs              : {len(mapped)}")
print(
    "Missing road-node mapping : "
    f"{mapped['nearest_road_node'].isna().sum()}"
)

print(
    "Average distance to node : "
    f"{mapped['distance_to_road_m'].mean():.2f} m"
)

print(
    "Median distance to node  : "
    f"{mapped['distance_to_road_m'].median():.2f} m"
)

print(
    "Maximum distance to node : "
    f"{mapped['distance_to_road_m'].max():.2f} m"
)

print()
print("Distance distribution:")

print(
    mapped["distance_to_road_m"]
    .describe()
    .to_string()
)


# ---------------------------------------------------------
# Save
# ---------------------------------------------------------

mapped.to_csv(
    OUTPUT_FILE,
    index=False
)

print()
print("=" * 60)
print("SAVED")
print("=" * 60)

print(OUTPUT_FILE)