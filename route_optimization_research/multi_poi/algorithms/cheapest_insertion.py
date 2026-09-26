import math
import time


def cheapest_insertion(
    distance_matrix,
    poi_ids,
    start_poi,
    end_poi,
):
    """
    Cheapest Insertion heuristic for an OPEN itinerary.

    Fixed:
        start_poi
        end_poi

    Objective:
        Start -> visit every POI exactly once -> End

    At each iteration, insert the unvisited POI into the
    feasible position that produces the smallest increase
    in total route distance.
    """

    start_time = time.perf_counter()

    poi_ids = list(poi_ids)

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if start_poi not in poi_ids:
        return _result(
            False,
            [],
            math.inf,
            start_time,
            0,
        )

    if end_poi not in poi_ids:
        return _result(
            False,
            [],
            math.inf,
            start_time,
            0,
        )

    if start_poi == end_poi and len(poi_ids) > 1:
        return _result(
            False,
            [],
            math.inf,
            start_time,
            0,
        )

    # --------------------------------------------------------
    # Initial route
    # --------------------------------------------------------

    route = [
        start_poi,
        end_poi,
    ]

    unvisited = set(poi_ids)

    unvisited.discard(start_poi)
    unvisited.discard(end_poi)

    total_distance = distance_matrix.loc[
        start_poi,
        end_poi,
    ]

    if not math.isfinite(
        float(total_distance)
    ):
        return _result(
            False,
            route,
            math.inf,
            start_time,
            0,
        )

    total_distance = float(
        total_distance
    )

    evaluations = 0

    # --------------------------------------------------------
    # Cheapest insertion
    # --------------------------------------------------------

    while unvisited:

        best_candidate = None
        best_position = None
        best_increase = math.inf

        for candidate in unvisited:

            # Candidate must be reachable from its
            # eventual predecessor and able to reach
            # its eventual successor.

            for position in range(
                1,
                len(route),
            ):

                predecessor = route[
                    position - 1
                ]

                successor = route[
                    position
                ]

                prev_to_candidate = (
                    distance_matrix.loc[
                        predecessor,
                        candidate,
                    ]
                )

                candidate_to_next = (
                    distance_matrix.loc[
                        candidate,
                        successor,
                    ]
                )

                prev_to_next = (
                    distance_matrix.loc[
                        predecessor,
                        successor,
                    ]
                )

                evaluations += 1

                if (
                    not math.isfinite(
                        float(
                            prev_to_candidate
                        )
                    )
                    or not math.isfinite(
                        float(
                            candidate_to_next
                        )
                    )
                    or not math.isfinite(
                        float(
                            prev_to_next
                        )
                    )
                ):
                    continue

                increase = (
                    float(prev_to_candidate)
                    + float(candidate_to_next)
                    - float(prev_to_next)
                )

                if (
                    increase < best_increase
                    or (
                        math.isclose(
                            increase,
                            best_increase,
                            rel_tol=1e-12,
                            abs_tol=1e-12,
                        )
                        and (
                            best_candidate is None
                            or str(candidate)
                            < str(best_candidate)
                        )
                    )
                ):

                    best_candidate = candidate
                    best_position = position
                    best_increase = increase

        # No feasible insertion exists.
        if best_candidate is None:

            return _result(
                False,
                route,
                math.inf,
                start_time,
                evaluations,
            )

        # Insert selected POI.
        route.insert(
            best_position,
            best_candidate,
        )

        total_distance += (
            best_increase
        )

        unvisited.remove(
            best_candidate
        )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

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
        "algorithm": "Cheapest Insertion",
        "route": route,
        "distance_km": distance,
        "execution_time_ms": elapsed,
        "nodes_evaluated": evaluations,
        "feasible": feasible,
    }