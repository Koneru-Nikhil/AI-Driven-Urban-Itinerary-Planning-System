import math
import random
import time


def genetic_algorithm(
    distance_matrix,
    poi_ids,
    start_poi,
    end_poi,
    seed=42,
    population_size=50,
    generations=100,
    mutation_rate=0.10,
    elite_size=2,
    tournament_size=3,
):
    """
    Genetic Algorithm for an open directed TSP-style itinerary.

    Fixed:
        - start POI
        - end POI

    Optimized:
        - ordering of all internal POIs

    Objective:
        Minimize total directed road-network distance.
    """

    start_time = time.perf_counter()

    rng = random.Random(seed)

    poi_ids = [str(poi) for poi in poi_ids]
    start_poi = str(start_poi)
    end_poi = str(end_poi)

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------

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

    internal = [
        poi for poi in poi_ids
        if poi != start_poi and poi != end_poi
    ]

    # ---------------------------------------------------------
    # Initial route
    # ---------------------------------------------------------

    initial_route = [
        start_poi
    ] + internal + [
        end_poi
    ]

    initial_distance = _route_distance(
        initial_route,
        distance_matrix
    )

    if not math.isfinite(initial_distance):
        return _result(
            False,
            initial_route,
            math.inf,
            start_time,
            0
        )

    # ---------------------------------------------------------
    # Small problem
    # ---------------------------------------------------------

    if len(internal) <= 1:
        return _result(
            True,
            initial_route,
            initial_distance,
            start_time,
            1
        )

    # ---------------------------------------------------------
    # Population initialization
    # ---------------------------------------------------------

    population = []

    population.append(list(internal))

    while len(population) < population_size:

        chromosome = list(internal)

        rng.shuffle(chromosome)

        population.append(chromosome)

    evaluations = 0

    # ---------------------------------------------------------
    # Track best
    # ---------------------------------------------------------

    best_chromosome = None
    best_distance = math.inf

    # ---------------------------------------------------------
    # Evolution
    # ---------------------------------------------------------

    for _ in range(generations):

        scored_population = []

        for chromosome in population:

            route = (
                [start_poi]
                + chromosome
                + [end_poi]
            )

            distance = _route_distance(
                route,
                distance_matrix
            )

            evaluations += len(route) - 1

            if math.isfinite(distance):

                scored_population.append(
                    (distance, chromosome)
                )

                if distance < best_distance:

                    best_distance = distance

                    best_chromosome = list(
                        chromosome
                    )

        # -----------------------------------------------------
        # No feasible solutions
        # -----------------------------------------------------

        if not scored_population:

            return _result(
                False,
                [],
                math.inf,
                start_time,
                evaluations
            )

        # -----------------------------------------------------
        # Sort population
        # -----------------------------------------------------

        scored_population.sort(
            key=lambda x: x[0]
        )

        # -----------------------------------------------------
        # Elitism
        # -----------------------------------------------------

        new_population = []

        for _, chromosome in scored_population[
            :elite_size
        ]:

            new_population.append(
                list(chromosome)
            )

        # -----------------------------------------------------
        # Generate children
        # -----------------------------------------------------

        while len(new_population) < population_size:

            parent1 = _tournament_selection(
                scored_population,
                tournament_size,
                rng
            )

            parent2 = _tournament_selection(
                scored_population,
                tournament_size,
                rng
            )

            child = _ordered_crossover(
                parent1,
                parent2,
                rng
            )

            # Mutation
            if rng.random() < mutation_rate:

                _swap_mutation(
                    child,
                    rng
                )

            new_population.append(child)

        population = new_population

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    if best_chromosome is None:

        return _result(
            False,
            [],
            math.inf,
            start_time,
            evaluations
        )

    best_route = (
        [start_poi]
        + best_chromosome
        + [end_poi]
    )

    return _result(
        True,
        best_route,
        best_distance,
        start_time,
        evaluations
    )


# =============================================================
# Route distance
# =============================================================

def _route_distance(route, distance_matrix):

    total = 0.0

    for i in range(len(route) - 1):

        source = route[i]
        target = route[i + 1]

        try:
            distance = float(
                distance_matrix.loc[
                    source,
                    target
                ]
            )
        except (KeyError, TypeError, ValueError):
            return math.inf

        if not math.isfinite(distance):
            return math.inf

        total += distance

    return total


# =============================================================
# Tournament selection
# =============================================================

def _tournament_selection(
    scored_population,
    tournament_size,
    rng
):

    tournament_size = min(
        tournament_size,
        len(scored_population)
    )

    participants = rng.sample(
        scored_population,
        tournament_size
    )

    winner = min(
        participants,
        key=lambda x: x[0]
    )

    return list(winner[1])


# =============================================================
# Ordered Crossover (OX)
# =============================================================

def _ordered_crossover(
    parent1,
    parent2,
    rng
):

    length = len(parent1)

    if length <= 1:
        return list(parent1)

    left, right = sorted(
        rng.sample(
            range(length),
            2
        )
    )

    child = [None] * length

    # Copy segment from parent 1
    child[left:right + 1] = parent1[
        left:right + 1
    ]

    # Fill remaining positions using parent 2
    remaining = [
        gene
        for gene in parent2
        if gene not in child
    ]

    remaining_index = 0

    for i in range(length):

        if child[i] is None:

            child[i] = remaining[
                remaining_index
            ]

            remaining_index += 1

    return child


# =============================================================
# Swap mutation
# =============================================================

def _swap_mutation(
    chromosome,
    rng
):

    if len(chromosome) < 2:
        return

    i, j = rng.sample(
        range(len(chromosome)),
        2
    )

    chromosome[i], chromosome[j] = (
        chromosome[j],
        chromosome[i]
    )


# =============================================================
# Result helper
# =============================================================

def _result(
    feasible,
    route,
    distance,
    start_time,
    evaluations
):

    elapsed = (
        time.perf_counter()
        - start_time
    ) * 1000

    return {
        "algorithm": "Genetic Algorithm",
        "route": route,
        "distance_km": distance,
        "execution_time_ms": elapsed,
        "nodes_evaluated": evaluations,
        "feasible": feasible,
    }