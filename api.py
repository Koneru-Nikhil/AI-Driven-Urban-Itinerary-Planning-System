from flask import Flask, request, jsonify
from flask_cors import CORS

import pandas as pd
import re

from model.utils.proxy_call import GeminiCall
from model.itinera_en import ItiNera


app = Flask(__name__)
CORS(app)


# ============================================================
# Helper: normalize POI names
# ============================================================

def normalize_name(name):
    """
    Normalize a POI name so that names such as:

        Shanyin Road, Hongkou District

    can match:

        Shanyin Road
    """

    if name is None:
        return ""

    name = str(name).strip().lower()

    # Remove district / area information after comma
    name = name.split(",")[0].strip()

    # Remove extra spaces
    name = re.sub(r"\s+", " ", name)

    return name


# ============================================================
# Find POI in dataset
# ============================================================

def find_poi(df, poi_name):

    target = normalize_name(poi_name)

    if not target:
        return None

    # --------------------------------------------
    # Exact normalized match
    # --------------------------------------------

    normalized_names = df["name"].apply(normalize_name)

    matches = df[
        normalized_names == target
    ]

    if not matches.empty:
        return matches.iloc[0]

    # --------------------------------------------
    # Partial match
    # --------------------------------------------

    matches = df[
        normalized_names.str.contains(
            re.escape(target),
            regex=True,
            na=False
        )
    ]

    if not matches.empty:
        return matches.iloc[0]

    # --------------------------------------------
    # Reverse partial match
    # --------------------------------------------

    for index, name in normalized_names.items():

        if target in name or name in target:
            return df.loc[index]

    return None


# ============================================================
# Generate itinerary
# ============================================================

@app.route("/api/generate", methods=["POST"])
def generate_itinerary():

    try:

        # ----------------------------------------------------
        # Read request
        # ----------------------------------------------------

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is empty."
            }), 400


        city = data.get(
            "city",
            "shanghai"
        )

        query = data.get(
            "query",
            "I would like an itinerary filled with history and art."
        )


        print("\n===================================")
        print("ITINERA REQUEST")
        print("===================================")

        print("City:", city)
        print("User Query:", query)


        # ----------------------------------------------------
        # Run ITINERA
        # ----------------------------------------------------

        day_planner = ItiNera(
            user_reqs=[query],
            proxy_call=GeminiCall(),
            city=city,
            type="en"
        )


        itinerary, lookup = day_planner.solve()


        print("\nGenerated ITINERARY:")
        print(itinerary)


        # ----------------------------------------------------
        # Load POI dataset
        # ----------------------------------------------------

        csv_path = f"model/data/{city}_en.csv"

        df = pd.read_csv(csv_path)


        # Make sure required columns exist

        required_columns = [
            "id",
            "name",
            "lat",
            "lon"
        ]

        for column in required_columns:

            if column not in df.columns:

                raise ValueError(
                    f"Dataset is missing required column: {column}"
                )


        df["name"] = df["name"].astype(str)


        # ----------------------------------------------------
        # Get itinerary text
        # ----------------------------------------------------

        itinerary_text = itinerary.get(
            "itinerary",
            ""
        )


        print("\nItinerary text:")
        print(itinerary_text)


        # ----------------------------------------------------
        # Extract POI names
        # ----------------------------------------------------

        # ITINERA normally uses ->
        poi_names = [
            name.strip()
            for name in itinerary_text.split("->")
            if name.strip()
        ]


        print("\nExtracted POIs:")

        for name in poi_names:
            print(" -", name)


        # ----------------------------------------------------
        # Get descriptions
        # ----------------------------------------------------

        itinerary_pois = itinerary.get(
            "pois",
            {}
        )


        # ----------------------------------------------------
        # Build selected POIs
        # ----------------------------------------------------

        selected_pois = []


        for position, poi_name in enumerate(
            poi_names,
            start=1
        ):

            print(
                f"\nMatching POI {position}: {poi_name}"
            )


            row = find_poi(
                df,
                poi_name
            )


            if row is None:

                print(
                    f"WARNING: POI not found: {poi_name}"
                )

                continue


            print(
                f"Matched with dataset POI: {row['name']}"
            )


            # ------------------------------------------------
            # Description
            # ------------------------------------------------

            description = ""


            # ITINERA's POI dictionary generally
            # uses dataset index as the key.

            row_index = row.name


            if isinstance(
                itinerary_pois,
                dict
            ):

                description = itinerary_pois.get(
                    str(row_index),
                    ""
                )


            # ------------------------------------------------
            # If no description was found,
            # use a simple fallback.
            # ------------------------------------------------

            if not description:

                description = (
                    f"Recommended location: "
                    f"{row['name']}."
                )


            # ------------------------------------------------
            # Add POI
            # ------------------------------------------------

            selected_pois.append({

                "order": position,

                "id": str(
                    row["id"]
                ),

                "name": str(
                    row["name"]
                ),

                "lat": float(
                    row["lat"]
                ),

                "lon": float(
                    row["lon"]
                ),

                "description": str(
                    description
                )
            })


        # ----------------------------------------------------
        # Final response
        # ----------------------------------------------------

        result = {

            "success": True,

            "itinerary": itinerary_text,

            "overall_reason": itinerary.get(
                "Overall Reason",
                ""
            ),

            "pois": selected_pois
        }


        print("\n===================================")
        print("FINAL API RESPONSE")
        print("===================================")

        print(
            f"POIs returned: {len(selected_pois)}"
        )


        for poi in selected_pois:

            print(
                f"{poi['order']}. "
                f"{poi['name']} "
                f"({poi['lat']}, {poi['lon']})"
            )


        print("===================================\n")


        return jsonify(result)


    except Exception as e:

        print("\n===================================")
        print("ITINERA API ERROR")
        print("===================================")

        print(str(e))

        print("===================================\n")


        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# Health check
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status":
            "ITINERA API is running"

    })


# ============================================================
# Start server
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True
    )