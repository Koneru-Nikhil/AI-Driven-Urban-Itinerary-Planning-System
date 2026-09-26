import math
import time


def three_opt(
    distance_matrix,
    poi_ids,
    start_poi,
    end_poi,
):
    """
    3-opt local search for an OPEN itinerary.

    Start and end POIs remain fixed.

    The algorithm selects three edges and evaluates the
    feasible reconnection patterns produced by reversing
    internal route segments.

    Because the road network is directed, every candidate
    route is evaluated using the actual directed distance
    matrix rather than assuming symmetric distances.
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

    internal = [
        poi
        for poi in poi_ids
        if poi != start_poi
        and poi != end_poi
    ]

    route = (
        [start_poi]
        + internal
        + [end_poi]
    )

    total_distance = _route_distance(
        route,
        distance_matrix,
    )

    if not math.isfinite(total_distance):
        return _result(
            False,
            route,
            math.inf,
            start_time,
            0,
        )

    evaluations = 0

    # --------------------------------------------------------
    # 3-opt local search
    # --------------------------------------------------------

    improved = True

    while improved:

        improved = False

        best_route = None
        best_distance = total_distance

        n = len(route)

        # Need at least three edges to perform 3-opt.
        if n < 5:
            break

        # ----------------------------------------------------
        # Choose three cut positions.
        #
        # The route is divided into:
        #
        # A | B | C | D
        #
        # where A and D include the fixed endpoints.
        # ----------------------------------------------------

        for i in range(1, n - 3):

            for j in range(i + 1, n - 2):

                for k in range(j + 1, n - 1):

                    a = route[:i]
                    b = route[i:j]
                    c = route[j:k]
                    d = route[k:]

                    # ------------------------------------------------
                    # Seven standard non-original reconnections.
                    #
                    # Since the graph is directed, every candidate
                    # is explicitly evaluated for feasibility.
                    # ------------------------------------------------

                    candidates = [
                        a + b[::-1] + c + d,
                        a + b + c[::-1] + d,
                        a + b[::-1] + c[::-1] + d,
                        a + c + b + d,
                        a + c[::-1] + b + d,
                        a + c + b[::-1] + d,
                        a + c[::-1] + b[::-1] + d,
                    ]

                    for candidate_route in candidates:

                        # Keep fixed endpoints.
                        if (
                            candidate_route[0]
                            != start_poi
                            or candidate_route[-1]
                            != end_poi
                        ):
                            continue

                        candidate_distance = (
                            _route_distance(
                                candidate_route,
                                distance_matrix,
                            )
                        )

                        evaluations += (
                            len(candidate_route) - 1
                        )

                        if not math.isfinite(
                            candidate_distance
                        ):
                            continue

                        if candidate_distance < (
                            best_distance - 1e-12
                        ):

                            best_distance = (
                                candidate_distance
                            )

                            best_route = (
                                candidate_route
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


def _route_distance(
    route,
    distance_matrix,
):
    """
    Calculate total directed road-network distance.
    """

    total = 0.0

    for i in range(len(route) - 1):

        distance = distance_matrix.loc[
            route[i],
            route[i + 1],
        ]

        if not math.isfinite(
            float(distance)
        ):
            return math.inf

        total += float(distance)

    return total


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
        "algorithm": "3-opt",
        "route": route,
        "distance_km": distance,
        "execution_time_ms": elapsed,
        "nodes_evaluated": evaluations,
        "feasible": feasible,
    }