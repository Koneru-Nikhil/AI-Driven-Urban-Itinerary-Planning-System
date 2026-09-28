import math
import random
import time


def route_distance(route, distance_matrix):
    """Calculate total directed route distance."""

    total = 0.0

    for i in range(len(route) - 1):

        source = route[i]
        target = route[i + 1]

        distance = distance_matrix.get(
            (source, target),
            math.inf
        )

        if not math.isfinite(distance):
            return math.inf

        total += distance

    return total


def construct_ant_route(
    poi_ids,
    start_poi,
    end_poi,
    distance_matrix,
    pheromone,
    alpha,
    beta,
    rng
):
    """
    Construct one feasible ant route.

    Start and end POIs are fixed.
    Every internal POI is visited exactly once.
    """

    unvisited = set(poi_ids)

    unvisited.discard(start_poi)
    unvisited.discard(end_poi)

    route = [start_poi]
    current = start_poi

    while unvisited:

        candidates = []

        for candidate in unvisited:

            distance = distance_matrix.get(
                (current, candidate),
                math.inf
            )

            # Candidate must be reachable now.
            if not math.isfinite(distance):
                continue

            # Candidate must also be able to reach
            # the fixed destination eventually.
            end_distance = distance_matrix.get(
                (candidate, end_poi),
                math.inf
            )

            if not math.isfinite(end_distance):
                continue

            candidates.append(
                (candidate, distance)
            )

        if not candidates:
            return None

        probabilities = []
        total_probability = 0.0

        for candidate, distance in candidates:

            tau = pheromone.get(
                (current, candidate),
                1.0
            )

            # Inverse distance heuristic.
            eta = 1.0 / max(distance, 1e-12)

            value = (
                (tau ** alpha)
                * (eta ** beta)
            )

            probabilities.append(
                (candidate, value)
            )

            total_probability += value

        if total_probability <= 0:
            return None

        # Roulette-wheel selection.
        threshold = (
            rng.random()
            * total_probability
        )

        cumulative = 0.0
        selected = None

        for candidate, probability in probabilities:

            cumulative += probability

            if cumulative >= threshold:

                selected = candidate
                break

        if selected is None:
            selected = probabilities[-1][0]

        route.append(selected)
        unvisited.remove(selected)
        current = selected

    # Final leg to fixed end.
    final_distance = distance_matrix.get(
        (current, end_poi),
        math.inf
    )

    if not math.isfinite(final_distance):
        return None

    route.append(end_poi)

    return route


def ant_colony_optimization(
    distance_matrix,
    poi_ids,
    start_poi,
    end_poi,
    ants=30,
    iterations=100,
    alpha=1.0,
    beta=3.0,
    evaporation_rate=0.5,
    pheromone_deposit=1.0,
    seed=42
):
    """
    Ant Colony Optimization for an open directed itinerary.

    Problem:

        Start -> visit every POI exactly once -> End

    Objective:

        Minimize total directed road-network distance.

    Start and end POIs remain fixed.
    """

    start_time = time.perf_counter()

    rng = random.Random(seed)

    poi_ids = list(poi_ids)

    # Force requested start/end positions.
    if start_poi in poi_ids:
        poi_ids.remove(start_poi)

    if end_poi in poi_ids:
        poi_ids.remove(end_poi)

    poi_ids = (
        [start_poi]
        + poi_ids
        + [end_poi]
    )

    # Duplicate POI validation.
    if len(set(poi_ids)) != len(poi_ids):

        return {
            "algorithm": "Ant Colony Optimization",
            "route": [],
            "distance_km": math.inf,
            "execution_time_ms":
                (time.perf_counter() - start_time) * 1000,
            "nodes_evaluated": 0,
            "feasible": False
        }

    internal_pois = poi_ids[1:-1]

    # Trivial case.
    if not internal_pois:

        direct_distance = distance_matrix.get(
            (start_poi, end_poi),
            math.inf
        )

        if not math.isfinite(direct_distance):

            return {
                "algorithm": "Ant Colony Optimization",
                "route": [],
                "distance_km": math.inf,
                "execution_time_ms":
                    (time.perf_counter() - start_time) * 1000,
                "nodes_evaluated": 0,
                "feasible": False
            }

        return {
            "algorithm": "Ant Colony Optimization",
            "route": [
                start_poi,
                end_poi
            ],
            "distance_km": direct_distance,
            "execution_time_ms":
                (time.perf_counter() - start_time) * 1000,
            "nodes_evaluated": 1,
            "feasible": True
        }

    # --------------------------------------------------
    # Pheromone initialization
    # --------------------------------------------------

    pheromone = {}

    for source in poi_ids:

        for target in poi_ids:

            if source == target:
                continue

            distance = distance_matrix.get(
                (source, target),
                math.inf
            )

            if math.isfinite(distance):

                pheromone[
                    (source, target)
                ] = 1.0

    best_route = None
    best_distance = math.inf

    candidate_evaluations = 0

    # --------------------------------------------------
    # Main ACO loop
    # --------------------------------------------------

    for iteration in range(iterations):

        ant_routes = []

        # ----------------------------------------------
        # Construct routes
        # ----------------------------------------------

        for _ in range(ants):

            route = construct_ant_route(
                poi_ids=poi_ids,
                start_poi=start_poi,
                end_poi=end_poi,
                distance_matrix=distance_matrix,
                pheromone=pheromone,
                alpha=alpha,
                beta=beta,
                rng=rng
            )

            candidate_evaluations += 1

            if route is None:
                continue

            distance = route_distance(
                route,
                distance_matrix
            )

            candidate_evaluations += 1

            if not math.isfinite(distance):
                continue

            ant_routes.append(
                (route, distance)
            )

            if distance < best_distance:

                best_distance = distance
                best_route = route[:]

        # ----------------------------------------------
        # Pheromone evaporation
        # ----------------------------------------------

        for edge in list(pheromone.keys()):

            pheromone[edge] *= (
                1.0 - evaporation_rate
            )

            # Avoid numerical underflow.
            pheromone[edge] = max(
                pheromone[edge],
                1e-12
            )

        # ----------------------------------------------
        # Pheromone deposition
        # ----------------------------------------------

        for route, distance in ant_routes:

            if distance <= 0:
                continue

            deposit = (
                pheromone_deposit
                / distance
            )

            for i in range(len(route) - 1):

                edge = (
                    route[i],
                    route[i + 1]
                )

                if edge in pheromone:

                    pheromone[edge] += deposit

        # ----------------------------------------------
        # Extra reinforcement for global best
        # ----------------------------------------------

        if best_route is not None:

            best_deposit = (
                pheromone_deposit
                / best_distance
            )

            for i in range(
                len(best_route) - 1
            ):

                edge = (
                    best_route[i],
                    best_route[i + 1]
                )

                if edge in pheromone:

                    pheromone[edge] += (
                        best_deposit
                    )

    execution_time_ms = (
        time.perf_counter() - start_time
    ) * 1000

    if best_route is None:

        return {
            "algorithm": "Ant Colony Optimization",
            "route": [],
            "distance_km": math.inf,
            "execution_time_ms":
                execution_time_ms,
            "nodes_evaluated":
                candidate_evaluations,
            "feasible": False
        }

    return {
        "algorithm": "Ant Colony Optimization",
        "route": best_route,
        "distance_km": best_distance,
        "execution_time_ms":
            execution_time_ms,
        "nodes_evaluated":
            candidate_evaluations,
        "feasible": True
    }