import heapq
import math
import time


def haversine_km(lat1, lon1, lat2, lon2):
    """
    Calculate straight-line distance between two geographic coordinates.
    Returns distance in kilometers.
    """

    R = 6371.0

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = lat2 - lat1
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def dijkstra(graph, source, target):
    """
    Dijkstra's shortest-path algorithm.

    Parameters
    ----------
    graph : dict
        graph[node] = [(neighbor, distance_km), ...]

    source : int
        Starting node.

    target : int
        Destination node.

    Returns
    -------
    result : dict
        Contains distance, path, execution time,
        and number of explored nodes.
    """

    start_time = time.perf_counter()

    distances = {source: 0.0}
    previous = {}

    priority_queue = [(0.0, source)]

    explored = 0

    while priority_queue:

        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance != distances.get(current_node):
            continue

        explored += 1

        if current_node == target:
            break

        for neighbor, weight in graph.get(current_node, []):

            new_distance = current_distance + weight

            if new_distance < distances.get(neighbor, float("inf")):

                distances[neighbor] = new_distance
                previous[neighbor] = current_node

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbor)
                )

    elapsed = time.perf_counter() - start_time

    if target not in distances:

        return {
            "algorithm": "Dijkstra",
            "distance_km": None,
            "path": [],
            "execution_time_ms": elapsed * 1000,
            "nodes_explored": explored,
            "found": False,
        }

    path = reconstruct_path(previous, source, target)

    return {
        "algorithm": "Dijkstra",
        "distance_km": distances[target],
        "path": path,
        "execution_time_ms": elapsed * 1000,
        "nodes_explored": explored,
        "found": True,
    }


def astar(graph, coordinates, source, target):
    """
    A* shortest-path algorithm.

    The heuristic is geographic straight-line distance
    between the current node and the destination.
    """

    start_time = time.perf_counter()

    g_score = {
        source: 0.0
    }

    previous = {}

    source_lat, source_lon = coordinates[source]
    target_lat, target_lon = coordinates[target]

    initial_h = haversine_km(
        source_lat,
        source_lon,
        target_lat,
        target_lon
    )

    priority_queue = [
        (initial_h, 0.0, source)
    ]

    explored = 0

    while priority_queue:

        f_score, current_g, current_node = heapq.heappop(
            priority_queue
        )

        if current_g != g_score.get(current_node):
            continue

        explored += 1

        if current_node == target:
            break

        for neighbor, weight in graph.get(current_node, []):

            tentative_g = current_g + weight

            if tentative_g < g_score.get(
                neighbor,
                float("inf")
            ):

                g_score[neighbor] = tentative_g
                previous[neighbor] = current_node

                neighbor_lat, neighbor_lon = coordinates[
                    neighbor
                ]

                heuristic = haversine_km(
                    neighbor_lat,
                    neighbor_lon,
                    target_lat,
                    target_lon
                )

                f_score = tentative_g + heuristic

                heapq.heappush(
                    priority_queue,
                    (
                        f_score,
                        tentative_g,
                        neighbor
                    )
                )

    elapsed = time.perf_counter() - start_time

    if target not in g_score:

        return {
            "algorithm": "A*",
            "distance_km": None,
            "path": [],
            "execution_time_ms": elapsed * 1000,
            "nodes_explored": explored,
            "found": False,
        }

    path = reconstruct_path(
        previous,
        source,
        target
    )

    return {
        "algorithm": "A*",
        "distance_km": g_score[target],
        "path": path,
        "execution_time_ms": elapsed * 1000,
        "nodes_explored": explored,
        "found": True,
    }


def reconstruct_path(previous, source, target):
    """
    Reconstruct path from predecessor information.
    """

    path = [target]

    current = target

    while current != source:

        if current not in previous:
            return []

        current = previous[current]
        path.append(current)

    path.reverse()

    return path