import math
import random
import time


def simulated_annealing(
    distance_matrix,
    poi_ids,
    start_poi,
    end_poi,
    seed=42,
    initial_temperature=1000.0,
    cooling_rate=0.995,
    min_temperature=1e-3,
    iterations_per_temperature=20,
):
    """
    Simulated Annealing for an OPEN itinerary.

    Fixed:
        start_poi
        end_poi

    Variable:
        Internal POI ordering

    Objective:
        Minimize total directed road-network distance.

    A fixed random seed is used for reproducibility.
    """

    start_time = time.perf_counter()

    rng = random.Random(seed)

    poi_ids = list(poi_ids)

    # --------------------------------------------------------
    # Validation
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

    # Start from the benchmark order.
    current_route = (
        [start_poi]
        + internal
        + [end_poi]
    )

    current_distance = _route_distance(
        current_route,
        distance_matrix,
    )

    if not math.isfinite(
        current_distance
    ):
        return _result(
            False,
            current_route,
            math.inf,
            start_time,
            0,
        )

    # Best solution found.
    best_route = list(
        current_route
    )

    best_distance = (
        current_distance
    )

    evaluations = 0

    temperature = (
        initial_temperature
    )

    # --------------------------------------------------------
    # Simulated Annealing
    # --------------------------------------------------------

    while temperature > min_temperature:

        for _ in range(
            iterations_per_temperature
        ):

            # Need at least two internal POIs
            # for a swap/move.
            if len(current_route) <= 3:
                break

            # Select two internal positions.
            i, j = sorted(
                rng.sample(
                    range(
                        1,
                        len(current_route) - 1
                    ),
                    2,
                )
            )

            # Use a mixture of neighborhood moves.
            move_type = rng.choice(
                [
                    "swap",
                    "reverse",
                    "relocate",
                ]
            )

            candidate_route = (
                list(current_route)
            )

            if move_type == "swap":

                (
                    candidate_route[i],
                    candidate_route[j],
                ) = (
                    candidate_route[j],
                    candidate_route[i],
                )

            elif move_type == "reverse":

                candidate_route[
                    i:j + 1
                ] = reversed(
                    candidate_route[
                        i:j + 1
                    ]
                )

            else:
                # Relocate the POI at position i
                # to position j.

                item = candidate_route.pop(
                    i
                )

                candidate_route.insert(
                    j,
                    item,
                )

            candidate_distance = (
                _route_distance(
                    candidate_route,
                    distance_matrix,
                )
            )

            evaluations += (
                len(candidate_route) - 1
            )

            # Ignore infeasible candidate routes.
            if not math.isfinite(
                candidate_distance
            ):
                continue

            delta = (
                candidate_distance
                - current_distance
            )

            # Always accept improvements.
            #
            # Sometimes accept worse solutions
            # according to the Boltzmann probability.
            if (
                delta <= 0
                or rng.random()
                < math.exp(
                    -delta
                    / temperature
                )
            ):

                current_route = (
                    candidate_route
                )

                current_distance = (
                    candidate_distance
                )

                if current_distance < (
                    best_distance
                    - 1e-12
                ):

                    best_route = list(
                        current_route
                    )

                    best_distance = (
                        current_distance
                    )

        temperature *= (
            cooling_rate
        )

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return _result(
        True,
        best_route,
        best_distance,
        start_time,
        evaluations,
    )


def _route_distance(
    route,
    distance_matrix,
):
    """
    Calculate total directed route distance.
    """

    total = 0.0

    for i in range(
        len(route) - 1
    ):

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
        "algorithm": "Simulated Annealing",
        "route": route,
        "distance_km": distance,
        "execution_time_ms": elapsed,
        "nodes_evaluated": evaluations,
        "feasible": feasible,
    }