import math
import time


def two_opt(
    distance_matrix,
    poi_ids,
    start_poi,
    end_poi,
):
    """
    2-opt local search for an OPEN itinerary.

    Start and end POIs remain fixed.

    Objective:
        Start -> visit every POI exactly once -> End

    The algorithm repeatedly reverses an internal route
    segment when the reversal produces a shorter feasible route.
    """

    start_time = time.perf_counter()

    poi_ids = list(poi_ids)

    if start_poi not in poi_ids:
        return _result(
            False, [], math.inf, start_time, 0
        )

    if end_poi not in poi_ids:
        return _result(
            False, [], math.inf, start_time, 0
        )

    if start_poi == end_poi and len(poi_ids) > 1:
        return _result(
            False, [], math.inf, start_time, 0
        )

    # --------------------------------------------------------
    # Initial route
    # --------------------------------------------------------
    #
    # For a standalone 2-opt benchmark we start with the
    # benchmark POI order.
    #
    # This keeps 2-opt independent from another heuristic.
    # --------------------------------------------------------

    route = list(poi_ids)

    # Ensure fixed start and end.
    route.remove(start_poi)
    route.remove(end_poi)

    route = (
        [start_poi]
        + route
        + [end_poi]
    )

    # --------------------------------------------------------
    # Calculate initial route distance
    # --------------------------------------------------------

    total_distance = 0.0

    for i in range(len(route) - 1):

        distance = distance_matrix.loc[
            route[i],
            route[i + 1],
        ]

        if not math.isfinite(
            float(distance)
        ):
            return _result(
                False,
                route,
                math.inf,
                start_time,
                0,
            )

        total_distance += float(distance)

    evaluations = 0

    # --------------------------------------------------------
    # 2-opt improvement
    # --------------------------------------------------------

    improved = True

    while improved:

        improved = False

        best_route = None
        best_distance = total_distance

        # Do not touch position 0 or the final position.
        #
        # i and j define the internal segment:
        #
        # ... -> route[i-1]
        #        route[i] ... route[j]
        #        route[j+1] -> ...
        #
        # Reversing route[i:j+1] keeps start/end fixed.

        for i in range(
            1,
            len(route) - 2,
        ):

            for j in range(
                i + 1,
                len(route) - 1,
            ):

                new_route = (
                    route[:i]
                    + list(
                        reversed(
                            route[i:j + 1]
                        )
                    )
                    + route[j + 1:]
                )

                new_distance = 0.0
                feasible = True

                for k in range(
                    len(new_route) - 1
                ):

                    distance = (
                        distance_matrix.loc[
                            new_route[k],
                            new_route[k + 1],
                        ]
                    )

                    evaluations += 1

                    if not math.isfinite(
                        float(distance)
                    ):
                        feasible = False
                        break

                    new_distance += float(
                        distance
                    )

                if not feasible:
                    continue

                # Strict improvement.
                if new_distance < (
                    best_distance - 1e-12
                ):

                    best_distance = (
                        new_distance
                    )

                    best_route = (
                        new_route
                    )

        if best_route is not None:

            route = best_route

            total_distance = (
                best_distance
            )

            improved = True

    return _result(
        True,
        route,
        total_distance,
        start_time,
        evaluations,
    )


def _result(
    feasible,
    route,
    distance,
    start_time,
    evaluations,
):

    elapsed = (
        time.perf_counter()
        - start_time
    ) * 1000

    return {
        "algorithm": "2-opt",
        "route": route,
        "distance_km": distance,
        "execution_time_ms": elapsed,
        "nodes_evaluated": evaluations,
        "feasible": feasible,
    }