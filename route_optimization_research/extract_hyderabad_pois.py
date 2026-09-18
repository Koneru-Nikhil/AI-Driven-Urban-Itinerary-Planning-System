import osmium
import pandas as pd

# ============================================================
# HYDERABAD BOUNDING BOX
# ============================================================

MIN_LON = 78.20
MAX_LON = 78.70
MIN_LAT = 17.20
MAX_LAT = 17.60


# ============================================================
# POI EXTRACTION HANDLER
# ============================================================

class POIHandler(osmium.SimpleHandler):

    def __init__(self):
        super().__init__()
        self.pois = []

    # --------------------------------------------------------
    # Add POI to our dataset
    # --------------------------------------------------------

    def add_poi(self, obj, lon, lat):

        name = obj.tags.get("name")

        # Ignore unnamed objects
        if not name:
            return

        # Identify POI category
        category = (
            obj.tags.get("tourism")
            or obj.tags.get("amenity")
            or obj.tags.get("leisure")
            or obj.tags.get("historic")
            or obj.tags.get("shop")
            or obj.tags.get("natural")
            or obj.tags.get("place")
            or "other"
        )

        self.pois.append({
            "osm_id": obj.id,
            "name": name,
            "category": category,
            "latitude": lat,
            "longitude": lon
        })

    # --------------------------------------------------------
    # Process OSM Nodes
    # --------------------------------------------------------

    def node(self, n):

        if not n.location.valid():
            return

        lon = n.location.lon
        lat = n.location.lat

        # Hyderabad bounding box
        if (
            MIN_LON <= lon <= MAX_LON
            and MIN_LAT <= lat <= MAX_LAT
        ):
            self.add_poi(n, lon, lat)

    # --------------------------------------------------------
    # Process OSM Ways
    # --------------------------------------------------------

    def way(self, w):

        try:

            if not w.nodes:
                return

            lons = []
            lats = []

            for node in w.nodes:

                if node.location.valid():

                    lons.append(node.lon)
                    lats.append(node.lat)

            if not lons:
                return

            # Approximate center of the way
            lon = sum(lons) / len(lons)
            lat = sum(lats) / len(lats)

            # Hyderabad bounding box
            if (
                MIN_LON <= lon <= MAX_LON
                and MIN_LAT <= lat <= MAX_LAT
            ):
                self.add_poi(w, lon, lat)

        except Exception:
            pass


# ============================================================
# MAIN PROGRAM
# ============================================================

print()
print("==============================================")
print("   HYDERABAD POI EXTRACTION")
print("==============================================")
print()

PBF_FILE = "southern-zone-260916.osm.pbf"

print("Input file:")
print(PBF_FILE)
print()

print("Hyderabad bounding box:")
print(
    MIN_LAT,
    "to",
    MAX_LAT,
    "latitude"
)

print(
    MIN_LON,
    "to",
    MAX_LON,
    "longitude"
)

print()
print("Reading OSM data...")
print("This may take several minutes.")
print()


# Create handler
handler = POIHandler()


# Read OSM PBF
handler.apply_file(
    PBF_FILE,
    locations=True
)


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(handler.pois)


# Check whether POIs were found
if df.empty:

    print()
    print("ERROR: No POIs were found.")
    print("Please check the Hyderabad bounding box.")
    print()

    exit()


# ============================================================
# REMOVE DUPLICATES
# ============================================================

df = df.drop_duplicates(
    subset=[
        "name",
        "latitude",
        "longitude"
    ]
)


# ============================================================
# SORT DATA
# ============================================================

df = df.sort_values(
    by=[
        "category",
        "name"
    ]
)


# ============================================================
# CREATE POI IDs
# ============================================================

df.insert(
    0,
    "poi_id",
    [
        "HYD{:06d}".format(i + 1)
        for i in range(len(df))
    ]
)


# ============================================================
# SAVE CSV
# ============================================================

OUTPUT_FILE = "Hyderabad_POIs.csv"

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("==============================================")
print("             EXTRACTION COMPLETE")
print("==============================================")
print()

print(
    "Total Hyderabad POIs:",
    len(df)
)

print()
print("POI categories:")
print("----------------------------------------------")

print(
    df["category"]
    .value_counts()
    .head(30)
)


print()
print("First 30 POIs:")
print("----------------------------------------------")

print(
    df.head(30).to_string(
        index=False
    )
)


print()
print("==============================================")
print("Dataset saved as:")
print(OUTPUT_FILE)
print("==============================================")
print()