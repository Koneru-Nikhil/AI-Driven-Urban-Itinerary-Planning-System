import math
import random
import time


def tabu_search(
    distance_matrix,
    poi_ids,
    start_poi,
    end_poi,
    seed=42,
    max_iterations=500,
    tabu_tenure=15,
):
    start_time = time.perf_counter()
    rng = random.Random(seed)

    poi_ids = [str(poi) for poi in poi_ids]
    start_poi = str(start_poi)
    end_poi = str(end_poi)

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------
    if start_poi not in poi_ids:
        return _result(False, [], math.inf, start_time, 0)

    if end_poi not in poi_ids:
        return _result(False, [], math.inf, start_time, 0)

    if start_poi == end_poi and len(poi_ids) > 1:
        return _result(False, [], math.inf, start_time, 0)

    internal = [
        poi
        for poi in poi_ids
        if poi != start_poi and poi != end_poi
    ]

    # ---------------------------------------------------------
    # Construct a feasible initial solution
    # ---------------------------------------------------------
    initial_route = _construct_feasible_route(
        distance_matrix,
        start_poi,
        end_poi,
        internal,
    )

    if initial_route is None:
        return _result(
            False,
            [],
            math.inf,
            start_time,
            0,
        )

    current_route = initial_route

    current_distance = _route_distance(
        current_route,
        distance_matrix,
    )

    if not math.isfinite(current_distance):
        return _result(
            False,
            current_route,
            math.inf,
            start_time,
            0,
        )

    best_route = list(current_route)
    best_distance = current_distance

    evaluations = len(current_route) - 1

    # ---------------------------------------------------------
    # No meaningful optimization for <= 1 internal POI
    # ---------------------------------------------------------
    if len(internal) <= 1:
        return _result(
            True,
            best_route,
            best_distance,
            start_time,
            evaluations,
        )

    # ---------------------------------------------------------
    # Tabu list
    # ---------------------------------------------------------
    tabu_list = {}

    for iteration in range(max_iterations):

        best_candidate = None

        # -----------------------------------------------------
        # Generate swap neighborhood
        #
        # Start and end positions remain fixed.
        # -----------------------------------------------------
        for i in range(1, len(current_route) - 1):

            for j in range(i + 1, len(current_route) - 1):

                candidate_route = list(current_route)

                poi_a = candidate_route[i]
                poi_b = candidate_route[j]

                candidate_route[i], candidate_route[j] = (
                    candidate_route[j],
                    candidate_route[i],
                )

                candidate_distance = _route_distance(
                    candidate_route,
                    distance_matrix,
                )

                evaluations += len(candidate_route) - 1

                if not math.isfinite(candidate_distance):
                    continue

                # Represent the move by the two swapped POIs.
                move = tuple(sorted((poi_a, poi_b)))

                tabu_until = tabu_list.get(move, -1)

                is_tabu = iteration < tabu_until

                # Aspiration criterion:
                # allow tabu move if it improves global best.
                aspiration = (
                    candidate_distance
                    < best_distance - 1e-12
                )

                if is_tabu and not aspiration:
                    continue

                candidate = (
                    candidate_distance,
                    candidate_route,
                    move,
                )

                if best_candidate is None:
                    best_candidate = candidate

                elif candidate_distance < best_candidate[0] - 1e-12:
                    best_candidate = candidate

                elif math.isclose(
                    candidate_distance,
                    best_candidate[0],
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ):
                    if move < best_candidate[2]:
                        best_candidate = candidate

        # No admissible neighbor.
        if best_candidate is None:
            break

        (
            candidate_distance,
            candidate_route,
            move,
        ) = best_candidate

        current_route = candidate_route
        current_distance = candidate_distance

        # -----------------------------------------------------
        # Update tabu list
        # -----------------------------------------------------
        tabu_list[move] = iteration + tabu_tenure

        # Remove expired tabu moves.
        expired = [
            key
            for key, expiry in tabu_list.items()
            if expiry <= iteration
        ]

        for key in expired:
            del tabu_list[key]

        # -----------------------------------------------------
        # Update global best
        # -----------------------------------------------------
        if current_distance < best_distance - 1e-12:

            best_distance = current_distance
            best_route = list(current_route)

    return _result(
        True,
        best_route,
        best_distance,
        start_time,
        evaluations,
    )


def _construct_feasible_route(
    distance_matrix,
    start_poi,
    end_poi,
    internal,
):
    """
    Construct:

        start -> every internal POI -> end

    while respecting directed reachability.

    At each step, choose an unvisited POI that:

    1. Can be reached from the current POI.
    2. Can itself reach the final destination.
    """

    remaining = set(internal)

    route = [start_poi]

    current = start_poi

    while remaining:

        candidates = []

        for poi in remaining:

            try:
                forward_distance = float(
                    distance_matrix.loc[current, poi]
                )

                to_end_distance = float(
                    distance_matrix.loc[poi, end_poi]
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

            if not math.isfinite(forward_distance):
                continue

            if not math.isfinite(to_end_distance):
                continue

            candidates.append(
                (
                    forward_distance + to_end_distance,
                    forward_distance,
                    poi,
                )
            )

        if not candidates:
            return None

        # Deterministic selection.
        candidates.sort(
            key=lambda x: (
                x[0],
                x[1],
                x[2],
            )
        )

        _, _, selected = candidates[0]

        route.append(selected)

        remaining.remove(selected)

        current = selected

    # ---------------------------------------------------------
    # Final leg
    # ---------------------------------------------------------
    try:
        final_distance = float(
            distance_matrix.loc[current, end_poi]
        )

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        return None

    if not math.isfinite(final_distance):
        return None

    route.append(end_poi)

    # Final validation.
    if not _route_is_feasible(
        route,
        distance_matrix,
    ):
        return None

    return route


def _route_is_feasible(
    route,
    distance_matrix,
):
    for i in range(len(route) - 1):

        source = route[i]
        target = route[i + 1]

        try:
            distance = float(
                distance_matrix.loc[source, target]
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return False

        if not math.isfinite(distance):
            return False

    return True


def _route_distance(
    route,
    distance_matrix,
):
    total = 0.0

    for i in range(len(route) - 1):

        source = route[i]
        target = route[i + 1]

        try:
            distance = float(
                distance_matrix.loc[source, target]
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return math.inf

        if not math.isfinite(distance):
            return math.inf

        total += distance

    return total


def _result(
    feasible,
    route,
    distance,
    start_time,
    evaluations,
):
    elapsed = (
        time.perf_counter() - start_time
    ) * 1000

    return {
        "algorithm": "Tabu Search",
        "route": route,
        "distance_km": distance,
        "execution_time_ms": elapsed,
        "nodes_evaluated": evaluations,
        "feasible": feasible,
    }