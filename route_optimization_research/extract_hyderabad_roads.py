import osmium
import pandas as pd
import math

# ============================================================
# CONFIGURATION
# ============================================================

PBF_FILE = "southern-zone-260916.osm.pbf"

# Hyderabad study area
MIN_LON = 78.20
MAX_LON = 78.70
MIN_LAT = 17.20
MAX_LAT = 17.60

# Road types used for the initial routing network
ROAD_TYPES = {
    "motorway",
    "motorway_link",
    "trunk",
    "trunk_link",
    "primary",
    "primary_link",
    "secondary",
    "secondary_link",
    "tertiary",
    "tertiary_link",
    "unclassified",
    "residential",
    "living_street",
    "service",
    "road"
}


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine(lon1, lat1, lon2, lat2):

    R = 6371.0  # Earth radius in km

    lon1 = math.radians(lon1)
    lat1 = math.radians(lat1)
    lon2 = math.radians(lon2)
    lat2 = math.radians(lat2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ============================================================
# OSM ROAD HANDLER
# ============================================================

class RoadHandler(osmium.SimpleHandler):

    def __init__(self):

        super().__init__()

        self.nodes = {}
        self.edges = []

        self.road_way_count = 0
        self.segment_count = 0

    def way(self, w):

        highway = w.tags.get("highway")

        if highway not in ROAD_TYPES:
            return

        self.road_way_count += 1

        previous = None

        for node in w.nodes:

            try:
                lon = node.lon
                lat = node.lat
            except Exception:
                previous = None
                continue

            if lon is None or lat is None:
                previous = None
                continue

            # Check Hyderabad study-area boundary
            inside = (
                MIN_LON <= lon <= MAX_LON
                and MIN_LAT <= lat <= MAX_LAT
            )

            if not inside:
                previous = None
                continue

            node_id = node.ref

            # Store node
            self.nodes[node_id] = {
                "node_id": node_id,
                "latitude": lat,
                "longitude": lon
            }

            # Create edge with previous node
            if previous is not None:

                prev_id, prev_lon, prev_lat = previous

                distance = haversine(
                    prev_lon,
                    prev_lat,
                    lon,
                    lat
                )

                oneway = w.tags.get("oneway", "no")

                # Normal two-way road
                if oneway not in {"yes", "1", "true", "-1"}:

                    self.edges.append({
                        "source": prev_id,
                        "target": node_id,
                        "distance_km": distance,
                        "highway": highway,
                        "oneway": "no"
                    })

                    self.edges.append({
                        "source": node_id,
                        "target": prev_id,
                        "distance_km": distance,
                        "highway": highway,
                        "oneway": "no"
                    })

                # Forward one-way
                elif oneway in {"yes", "1", "true"}:

                    self.edges.append({
                        "source": prev_id,
                        "target": node_id,
                        "distance_km": distance,
                        "highway": highway,
                        "oneway": "yes"
                    })

                # Reverse one-way
                elif oneway == "-1":

                    self.edges.append({
                        "source": node_id,
                        "target": prev_id,
                        "distance_km": distance,
                        "highway": highway,
                        "oneway": "yes"
                    })

                self.segment_count += 1

            previous = (node_id, lon, lat)


# ============================================================
# MAIN
# ============================================================

print("=" * 60)
print("HYDERABAD ROAD NETWORK EXTRACTION")
print("=" * 60)

print("\nReading:", PBF_FILE)
print("Study area:")
print("Longitude:", MIN_LON, "to", MAX_LON)
print("Latitude :", MIN_LAT, "to", MAX_LAT)

handler = RoadHandler()

handler.apply_file(
    PBF_FILE,
    locations=True
)

print("\nExtraction completed.")

print("\nRoad statistics")
print("-" * 40)

print("Road ways:", handler.road_way_count)
print("Road segments:", handler.segment_count)
print("Unique road nodes:", len(handler.nodes))
print("Directed edges:", len(handler.edges))


# ============================================================
# SAVE NODES
# ============================================================

nodes_df = pd.DataFrame(
    list(handler.nodes.values())
)

nodes_df.to_csv(
    "Hyderabad_Road_Nodes.csv",
    index=False
)


# ============================================================
# SAVE EDGES
# ============================================================

edges_df = pd.DataFrame(
    handler.edges
)

edges_df.to_csv(
    "Hyderabad_Road_Edges.csv",
    index=False
)


# ============================================================
# ROAD TYPE STATISTICS
# ============================================================

print("\nRoad type distribution")
print("-" * 40)

road_type_counts = (
    edges_df["highway"]
    .value_counts()
)

print(road_type_counts)


print("\nFiles created:")
print("1. Hyderabad_Road_Nodes.csv")
print("2. Hyderabad_Road_Edges.csv")

print("\nDONE.")