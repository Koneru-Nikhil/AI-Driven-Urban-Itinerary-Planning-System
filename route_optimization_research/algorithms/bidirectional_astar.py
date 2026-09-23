import heapq
import math
import time

from route_optimization_research.algorithms.shortest_path import (
    haversine_km
)


def reconstruct_bidirectional_path(
    source,
    target,
    meeting_node,
    forward_prev,
    backward_next
):
    """
    Reconstruct:

        source -> meeting_node -> target
    """

    # ---------------------------------------------------------
    # Forward part
    # ---------------------------------------------------------

    forward_path = []
    current = meeting_node

    while current is not None:

        forward_path.append(current)

        if current == source:
            break

        current = forward_prev.get(current)

    if not forward_path:
        return []

    if forward_path[-1] != source:
        return []

    forward_path.reverse()

    # ---------------------------------------------------------
    # Backward part
    # ---------------------------------------------------------

    backward_path = []
    current = meeting_node

    while current != target:

        current = backward_next.get(current)

        if current is None:
            return []

        backward_path.append(current)

    return forward_path + backward_path


def clean_astar_heap(
    heap,
    distance_map,
    settled
):
    """
    Remove stale A* heap entries.

    A* heap entry:

        (f_score, g_score, node)
    """

    while heap:

        f_score, g_score, node = heap[0]

        if node in settled:
            heapq.heappop(heap)
            continue

        current_best = distance_map.get(
            node,
            math.inf
        )

        if g_score > current_best:
            heapq.heappop(heap)
            continue

        break


def clean_g_heap(
    heap,
    distance_map,
    settled
):
    """
    Remove stale entries from the auxiliary
    g-value heap.

    g-value heap entry:

        (g_score, node)
    """

    while heap:

        g_score, node = heap[0]

        if node in settled:
            heapq.heappop(heap)
            continue

        current_best = distance_map.get(
            node,
            math.inf
        )

        if g_score > current_best:
            heapq.heappop(heap)
            continue

        break


def bidirectional_astar(
    graph,
    reverse_graph,
    coordinates,
    source,
    target
):
    """
    Exact Bidirectional A* shortest-path algorithm.

    Forward search:
        source -> target

    Backward search:
        target -> source using reverse graph.

    A* heuristic:
        Haversine geographic distance.

    Important correctness feature:
        A* priority queues are ordered by f = g + h,
        but termination is based on the true minimum
        unsettled g-values maintained in separate heaps.

    Returns:
        algorithm
        distance_km
        path
        execution_time_ms
        nodes_explored
        found
    """

    start_time = time.perf_counter()

    # =========================================================
    # SOURCE == TARGET
    # =========================================================

    if source == target:

        elapsed = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "algorithm": "Bidirectional A*",
            "distance_km": 0.0,
            "path": [source],
            "execution_time_ms": elapsed,
            "nodes_explored": 1,
            "found": True
        }

    # =========================================================
    # COORDINATES
    # =========================================================

    source_lat = coordinates[source][0]
    source_lon = coordinates[source][1]

    target_lat = coordinates[target][0]
    target_lon = coordinates[target][1]

    # =========================================================
    # DISTANCE MAPS
    # =========================================================

    forward_dist = {
        source: 0.0
    }

    backward_dist = {
        target: 0.0
    }

    # =========================================================
    # PARENT MAPS
    # =========================================================

    forward_prev = {
        source: None
    }

    backward_next = {
        target: None
    }

    # =========================================================
    # INITIAL HEURISTICS
    # =========================================================

    forward_h = haversine_km(
        source_lat,
        source_lon,
        target_lat,
        target_lon
    )

    backward_h = haversine_km(
        target_lat,
        target_lon,
        source_lat,
        source_lon
    )

    # =========================================================
    # A* PRIORITY QUEUES
    #
    # (f_score, g_score, node)
    # =========================================================

    forward_heap = [
        (
            forward_h,
            0.0,
            source
        )
    ]

    backward_heap = [
        (
            backward_h,
            0.0,
            target
        )
    ]

    # =========================================================
    # AUXILIARY g-VALUE HEAPS
    #
    # These are NOT used to choose which node A* expands.
    #
    # They are used only to calculate a correct lower bound
    # for termination.
    #
    # (g_score, node)
    # =========================================================

    forward_g_heap = [
        (
            0.0,
            source
        )
    ]

    backward_g_heap = [
        (
            0.0,
            target
        )
    ]

    # =========================================================
    # SETTLED NODES
    # =========================================================

    forward_settled = set()
    backward_settled = set()

    # =========================================================
    # BEST COMPLETE ROUTE
    # =========================================================

    best_distance = math.inf
    meeting_node = None

    nodes_explored = 0

    # =========================================================
    # MAIN SEARCH LOOP
    # =========================================================

    while forward_heap and backward_heap:

        # -----------------------------------------------------
        # Clean A* heaps
        # -----------------------------------------------------

        clean_astar_heap(
            forward_heap,
            forward_dist,
            forward_settled
        )

        clean_astar_heap(
            backward_heap,
            backward_dist,
            backward_settled
        )

        if not forward_heap or not backward_heap:
            break

        # =====================================================
        # FORWARD A*
        # =====================================================

        f_score, g_score, current = heapq.heappop(
            forward_heap
        )

        if current in forward_settled:
            continue

        if g_score > forward_dist.get(
            current,
            math.inf
        ):
            continue

        forward_settled.add(current)
        nodes_explored += 1

        # -----------------------------------------------------
        # Check intersection
        # -----------------------------------------------------

        if current in backward_dist:

            candidate_distance = (
                forward_dist[current]
                + backward_dist[current]
            )

            if candidate_distance < best_distance:

                best_distance = candidate_distance
                meeting_node = current

        # -----------------------------------------------------
        # Relax forward edges
        # -----------------------------------------------------

        for neighbor, weight in graph.get(
            current,
            []
        ):

            new_distance = (
                forward_dist[current]
                + weight
            )

            if new_distance < forward_dist.get(
                neighbor,
                math.inf
            ):

                forward_dist[neighbor] = new_distance
                forward_prev[neighbor] = current

                neighbor_lat = coordinates[neighbor][0]
                neighbor_lon = coordinates[neighbor][1]

                heuristic = haversine_km(
                    neighbor_lat,
                    neighbor_lon,
                    target_lat,
                    target_lon
                )

                # A* priority queue
                heapq.heappush(
                    forward_heap,
                    (
                        new_distance + heuristic,
                        new_distance,
                        neighbor
                    )
                )

                # True g-value queue
                heapq.heappush(
                    forward_g_heap,
                    (
                        new_distance,
                        neighbor
                    )
                )

        # =====================================================
        # BACKWARD A*
        # =====================================================

        clean_astar_heap(
            backward_heap,
            backward_dist,
            backward_settled
        )

        if not backward_heap:
            break

        f_score, g_score, current = heapq.heappop(
            backward_heap
        )

        if current in backward_settled:
            continue

        if g_score > backward_dist.get(
            current,
            math.inf
        ):
            continue

        backward_settled.add(current)
        nodes_explored += 1

        # -----------------------------------------------------
        # Check intersection
        # -----------------------------------------------------

        if current in forward_dist:

            candidate_distance = (
                forward_dist[current]
                + backward_dist[current]
            )

            if candidate_distance < best_distance:

                best_distance = candidate_distance
                meeting_node = current

        # -----------------------------------------------------
        # Relax reverse edges
        # -----------------------------------------------------

        for neighbor, weight in reverse_graph.get(
            current,
            []
        ):

            new_distance = (
                backward_dist[current]
                + weight
            )

            if new_distance < backward_dist.get(
                neighbor,
                math.inf
            ):

                backward_dist[neighbor] = new_distance
                backward_next[neighbor] = current

                neighbor_lat = coordinates[neighbor][0]
                neighbor_lon = coordinates[neighbor][1]

                heuristic = haversine_km(
                    neighbor_lat,
                    neighbor_lon,
                    source_lat,
                    source_lon
                )

                # A* priority queue
                heapq.heappush(
                    backward_heap,
                    (
                        new_distance + heuristic,
                        new_distance,
                        neighbor
                    )
                )

                # True g-value queue
                heapq.heappush(
                    backward_g_heap,
                    (
                        new_distance,
                        neighbor
                    )
                )

        # =====================================================
        # CORRECT TERMINATION CHECK
        # =====================================================

        if meeting_node is not None:

            # -------------------------------------------------
            # Clean true g-value heaps
            # -------------------------------------------------

            clean_g_heap(
                forward_g_heap,
                forward_dist,
                forward_settled
            )

            clean_g_heap(
                backward_g_heap,
                backward_dist,
                backward_settled
            )

            if (
                not forward_g_heap
                or not backward_g_heap
            ):
                break

            # -------------------------------------------------
            # IMPORTANT:
            #
            # These are TRUE minimum unsettled g-values.
            #
            # We do NOT use:
            #
            #     forward_heap[0][1]
            #
            # because forward_heap is ordered by f = g + h.
            # -------------------------------------------------

            min_forward_g = forward_g_heap[0][0]
            min_backward_g = backward_g_heap[0][0]

            lower_bound = (
                min_forward_g
                + min_backward_g
            )

            # -------------------------------------------------
            # If no unexplored combination can improve the
            # current complete route, the route is optimal.
            # -------------------------------------------------

            if lower_bound >= best_distance:
                break

    # =========================================================
    # NO ROUTE
    # =========================================================

    if meeting_node is None:

        elapsed = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "algorithm": "Bidirectional A*",
            "distance_km": math.inf,
            "path": [],
            "execution_time_ms": elapsed,
            "nodes_explored": nodes_explored,
            "found": False
        }

    # =========================================================
    # RECONSTRUCT PATH
    # =========================================================

    path = reconstruct_bidirectional_path(
        source,
        target,
        meeting_node,
        forward_prev,
        backward_next
    )

    if not path:

        elapsed = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "algorithm": "Bidirectional A*",
            "distance_km": math.inf,
            "path": [],
            "execution_time_ms": elapsed,
            "nodes_explored": nodes_explored,
            "found": False
        }

    # =========================================================
    # EXACT PATH DISTANCE
    # =========================================================

    actual_distance = 0.0

    for u, v in zip(
        path,
        path[1:]
    ):

        edge_found = False

        for neighbor, weight in graph.get(
            u,
            []
        ):

            if neighbor == v:

                actual_distance += weight
                edge_found = True
                break

        if not edge_found:

            elapsed = (
                time.perf_counter() - start_time
            ) * 1000

            return {
                "algorithm": "Bidirectional A*",
                "distance_km": math.inf,
                "path": [],
                "execution_time_ms": elapsed,
                "nodes_explored": nodes_explored,
                "found": False
            }

    # =========================================================
    # FINAL RESULT
    # =========================================================

    elapsed = (
        time.perf_counter() - start_time
    ) * 1000

    return {
        "algorithm": "Bidirectional A*",
        "distance_km": actual_distance,
        "path": path,
        "execution_time_ms": elapsed,
        "nodes_explored": nodes_explored,
        "found": True
    }