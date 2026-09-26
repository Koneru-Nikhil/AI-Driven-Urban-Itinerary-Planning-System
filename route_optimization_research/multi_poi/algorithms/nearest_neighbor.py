import math
import time


def nearest_neighbor(
    distance_matrix,
    poi_ids,
    start_poi,
    end_poi,
):
    """
    Nearest Neighbor heuristic for an OPEN itinerary.

    Objective:
        Start -> visit every POI exactly once -> End

    The start and end POIs are fixed.

    At each step, select the nearest unvisited POI
    that can eventually continue toward the end.

    Returns:
        algorithm
        route
        distance_km
        execution_time_ms
        nodes_evaluated
        feasible
    """

    start_time = time.perf_counter()

    poi_ids = list(poi_ids)

    if start_poi not in poi_ids:
        return {
            "algorithm": "Nearest Neighbor",
            "route": [],
            "distance_km": math.inf,
            "execution_time_ms": 0.0,
            "nodes_evaluated": 0,
            "feasible": False,
        }

    if end_poi not in poi_ids:
        return {
            "algorithm": "Nearest Neighbor",
            "route": [],
            "distance_km": math.inf,
            "execution_time_ms": 0.0,
            "nodes_evaluated": 0,
            "feasible": False,
        }

    if start_poi == end_poi and len(poi_ids) > 1:
        return {
            "algorithm": "Nearest Neighbor",
            "route": [],
            "distance_km": math.inf,
            "execution_time_ms": 0.0,
            "nodes_evaluated": 0,
            "feasible": False,
        }

    # --------------------------------------------------------
    # Start route
    # --------------------------------------------------------

    route = [start_poi]

    unvisited = set(poi_ids)

    unvisited.discard(start_poi)
    unvisited.discard(end_poi)

    current = start_poi

    total_distance = 0.0
    nodes_evaluated = 0

    # --------------------------------------------------------
    # Select nearest unvisited POIs
    # --------------------------------------------------------

    while unvisited:

        candidates = []

        for candidate in unvisited:

            distance = distance_matrix.loc[
                current,
                candidate
            ]

            nodes_evaluated += 1

            if (
                not math.isfinite(
                    float(distance)
                )
            ):
                continue

            # Candidate must also be able to
            # eventually reach the fixed end.
            to_end = distance_matrix.loc[
                candidate,
                end_poi
            ]

            if not math.isfinite(
                float(to_end)
            ):
                continue

            candidates.append(
                (
                    float(distance),
                    candidate,
                )
            )

        if not candidates:

            elapsed = (
                time.perf_counter()
                - start_time
            ) * 1000

            return {
                "algorithm": "Nearest Neighbor",
                "route": route,
                "distance_km": math.inf,
                "execution_time_ms": elapsed,
                "nodes_evaluated": nodes_evaluated,
                "feasible": False,
            }

        # Nearest feasible candidate
        candidates.sort(
            key=lambda x: (
                x[0],
                str(x[1]),
            )
        )

        step_distance, next_poi = (
            candidates[0]
        )

        route.append(next_poi)

        total_distance += step_distance

        current = next_poi

        unvisited.remove(
            next_poi
        )

    # --------------------------------------------------------
    # Final leg to fixed end
    # --------------------------------------------------------

    final_distance = distance_matrix.loc[
        current,
        end_poi
    ]

    if not math.isfinite(
        float(final_distance)
    ):

        elapsed = (
            time.perf_counter()
            - start_time
        ) * 1000

        return {
            "algorithm": "Nearest Neighbor",
            "route": route,
            "distance_km": math.inf,
            "execution_time_ms": elapsed,
            "nodes_evaluated": nodes_evaluated,
            "feasible": False,
        }

    route.append(end_poi)

    total_distance += float(
        final_distance
    )

    elapsed = (
        time.perf_counter()
        - start_time
    ) * 1000

    return {
        "algorithm": "Nearest Neighbor",
        "route": route,
        "distance_km": total_distance,
        "execution_time_ms": elapsed,
        "nodes_evaluated": nodes_evaluated,
        "feasible": True,
    }