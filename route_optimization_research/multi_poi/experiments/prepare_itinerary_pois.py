import os
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)

RESEARCH_DIR = os.path.join(
    BASE_DIR,
    "route_optimization_research"
)

INPUT_FILE = os.path.join(
    RESEARCH_DIR,
    "Hyderabad_POIs.csv"
)

OUTPUT_DIR = os.path.join(
    RESEARCH_DIR,
    "multi_poi",
    "results"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "Hyderabad_Itinerary_POIs.csv"
)


# ============================================================
# CATEGORY MAPPING
# ============================================================

CATEGORY_MAP = {

    # ---------------- FOOD ----------------
    "restaurant": "Food",
    "fast_food": "Food",
    "cafe": "Food",
    "bakery": "Food",
    "food_court": "Food",
    "confectionery": "Food",
    "butcher": "Food",
    "ice_cream": "Food",
    "tea": "Food",
    "coffee": "Food",
    "food": "Food",
    "beverages": "Food",
    "pastry": "Food",
    "seafood": "Food",
    "dairy": "Food",
    "grocery": "Food",
    "greengrocer": "Food",
    "health_food": "Food",
    "juice_bar": "Food",
    "deli": "Food",
    "sweet": "Food",
    "tiffincenter": "Food",

    # ---------------- CULTURE & HERITAGE ----------------
    "museum": "Culture & Heritage",
    "archaeological_site": "Culture & Heritage",
    "monument": "Culture & Heritage",
    "memorial": "Culture & Heritage",
    "artwork": "Culture & Heritage",
    "gallery": "Culture & Heritage",
    "art": "Culture & Heritage",
    "arts_centre": "Culture & Heritage",
    "exhibition_centre": "Culture & Heritage",
    "castle": "Culture & Heritage",
    "building;castle": "Culture & Heritage",
    "heritage_building": "Culture & Heritage",
    "city_gate": "Culture & Heritage",
    "tomb": "Culture & Heritage",
    "grave_yard": "Culture & Heritage",
    "library": "Culture & Heritage",
    "planetarium": "Culture & Heritage",

    # ---------------- RELIGION ----------------
    "place_of_worship": "Religion",
    "church": "Religion",
    "Temple": "Religion",
    "hindu": "Religion",
    "religion": "Religion",
    "wayside_shrine": "Religion",

    # ---------------- NATURE & OUTDOORS ----------------
    "park": "Nature & Outdoors",
    "garden": "Nature & Outdoors",
    "nature_reserve": "Nature & Outdoors",
    "water": "Nature & Outdoors",
    "water_park": "Nature & Outdoors",
    "wetland": "Nature & Outdoors",
    "wood": "Nature & Outdoors",
    "grassland": "Nature & Outdoors",
    "scrub": "Nature & Outdoors",
    "tree": "Nature & Outdoors",
    "peak": "Nature & Outdoors",
    "hill": "Nature & Outdoors",
    "cliff": "Nature & Outdoors",
    "islet": "Nature & Outdoors",
    "fountain": "Nature & Outdoors",
    "viewpoint": "Nature & Outdoors",
    "picnic_site": "Nature & Outdoors",
    "recreation_ground": "Nature & Outdoors",
    "dog_park": "Nature & Outdoors",

    # ---------------- SHOPPING ----------------
    "mall": "Shopping",
    "clothes": "Shopping",
    "supermarket": "Shopping",
    "jewelry": "Shopping",
    "electronics": "Shopping",
    "department_store": "Shopping",
    "shoes": "Shopping",
    "books": "Shopping",
    "stationery": "Shopping",
    "convenience": "Shopping",
    "gift": "Shopping",
    "fashion": "Shopping",
    "fashion_accessories": "Shopping",
    "boutique": "Shopping",
    "bag": "Shopping",
    "watches": "Shopping",
    "cosmetics": "Shopping",
    "florist": "Shopping",
    "toys": "Shopping",
    "variety_store": "Shopping",
    "furniture": "Shopping",
    "hardware": "Shopping",
    "houseware": "Shopping",
    "appliance": "Shopping",
    "paint": "Shopping",
    "fabric": "Shopping",
    "tiles": "Shopping",
    "leather": "Shopping",
    "pottery": "Shopping",
    "retail shops": "Shopping",
    "kirana_store": "Shopping",

    # ---------------- ENTERTAINMENT ----------------
    "cinema": "Entertainment",
    "theatre": "Entertainment",
    "events_venue": "Entertainment",
    "theme_park": "Entertainment",
    "amusement_arcade": "Entertainment",
    "aquarium": "Entertainment",
    "zoo": "Entertainment",
    "games": "Entertainment",
    "party": "Entertainment",
    "music": "Entertainment",
    "bandstand": "Entertainment",

    # ---------------- RECREATION & SPORTS ----------------
    "fitness_centre": "Recreation & Sports",
    "sports_centre": "Recreation & Sports",
    "sports": "Recreation & Sports",
    "sports_hall": "Recreation & Sports",
    "stadium": "Recreation & Sports",
    "pitch": "Recreation & Sports",
    "practice_pitch": "Recreation & Sports",
    "playground": "Recreation & Sports",
    "golf_course": "Recreation & Sports",
    "swimming_pool": "Recreation & Sports",
    "fitness_station": "Recreation & Sports",
    "horse_riding": "Recreation & Sports",
    "outdoor": "Recreation & Sports",

    # ---------------- ACCOMMODATION ----------------
    "hotel": "Accommodation",
    "guest_house": "Accommodation",
    "hostel": "Accommodation",
    "resort": "Accommodation",
    "motel": "Accommodation",
    "love_hotel": "Accommodation",
    "camp_site": "Accommodation",
    "caravan_site": "Accommodation",
    "beach_resort": "Accommodation",

    # ---------------- EDUCATION ----------------
    "school": "Education",
    "college": "Education",
    "university": "Education",
    "kindergarten": "Education",
    "prep_school": "Education",
    "language_school": "Education",
    "research_institute": "Education",
    "music_school": "Education",
    "education": "Education",

    # ---------------- HEALTHCARE ----------------
    "hospital": "Healthcare",
    "health_post": "Healthcare",
    "clinic": "Healthcare",
    "pharmacy": "Healthcare",
    "doctors": "Healthcare",
    "dentist": "Healthcare",
    "medical_supply": "Healthcare",
    "optician": "Healthcare",
    "medical": "Healthcare",
    "dispensary": "Healthcare",

    # ---------------- SERVICES ----------------
    "bank": "Services",
    "atm": "Services",
    "post_office": "Services",
    "post_box": "Services",
    "post_depot": "Services",
    "police": "Services",
    "fire_station": "Services",
    "courthouse": "Services",
    "townhall": "Services",
    "public_building": "Services",
    "community_centre": "Services",
    "social_facility": "Services",
    "information": "Services",
    "toilets": "Services",
    "parking": "Services",
    "bus_station": "Transport",
    "bus_stop": "Transport",
    "taxi": "Transport",
    "ferry_terminal": "Transport",
    "public_transport": "Transport",

    # ---------------- PERSONAL SERVICES ----------------
    "beauty": "Personal Services",
    "hairdresser": "Personal Services",
    "saloon": "Personal Services",
    "tailor": "Personal Services",
    "laundry": "Personal Services",
    "dry_cleaning": "Personal Services",
    "massage": "Personal Services",

}


# ============================================================
# CANDIDATE CATEGORIES
# ============================================================

ITINERARY_CATEGORIES = {
    "Food",
    "Culture & Heritage",
    "Religion",
    "Nature & Outdoors",
    "Shopping",
    "Entertainment",
    "Recreation & Sports",
    "Accommodation",
}


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("HYDERABAD ITINERARY POI PREPROCESSING")
    print("=" * 70)

    print("\nLoading raw POI dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Raw POIs: {len(df):,}")
    print(f"Raw categories: {df['category'].nunique():,}")

    # --------------------------------------------------------
    # Map raw OSM category → itinerary category
    # --------------------------------------------------------

    df["itinerary_category"] = (
        df["category"]
        .map(CATEGORY_MAP)
        .fillna("Unclassified")
    )

    # --------------------------------------------------------
    # Candidate flag
    # --------------------------------------------------------

    df["is_itinerary_candidate"] = (
        df["itinerary_category"]
        .isin(ITINERARY_CATEGORIES)
    )

    # --------------------------------------------------------
    # Save derived dataset
    # --------------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("PREPROCESSING SUMMARY")
    print("=" * 70)

    print(f"Total POIs: {len(df):,}")

    print(
        f"Itinerary candidates: "
        f"{df['is_itinerary_candidate'].sum():,}"
    )

    print(
        f"Unclassified POIs: "
        f"{(df['itinerary_category'] == 'Unclassified').sum():,}"
    )

    print("\nItinerary category distribution:")

    print(
        df["itinerary_category"]
        .value_counts()
        .to_string()
    )

    print("\nCandidate category distribution:")

    print(
        df.loc[
            df["is_itinerary_candidate"],
            "itinerary_category"
        ]
        .value_counts()
        .to_string()
    )

    print("\nOutput:")
    print(OUTPUT_FILE)

    print("\nPreprocessing completed successfully.")


if __name__ == "__main__":
    main()