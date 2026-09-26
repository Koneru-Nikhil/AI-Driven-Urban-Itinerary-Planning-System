import heapq
import math
import pandas as pd


def load_road_graph(edges_file):
    """
    Load the directed Hyderabad road network.

    Returns:
        graph[source] = [(target, distance_km), ...]
    """

    edges = pd.read_csv(edges_file)

    graph = {}

    for row in edges.itertuples(index=False):

        source = int(row.source)
        target = int(row.target)
        distance = float(row.distance_km)

        if source not in graph:
            graph[source] = []

        graph[source].append(
            (target, distance)
        )

    return graph


def dijkstra_distances(graph, source):
    """
    Calculate shortest-path distances from one
    source node to every reachable node.
    """

    distances = {
        source: 0.0
    }

    heap = [
        (0.0, source)
    ]

    while heap:

        current_distance, current_node = heapq.heappop(heap)

        if current_distance != distances.get(
            current_node,
            math.inf
        ):
            continue

        for neighbor, edge_distance in graph.get(
            current_node,
            []
        ):

            new_distance = (
                current_distance
                + edge_distance
            )

            if new_distance < distances.get(
                neighbor,
                math.inf
            ):

                distances[neighbor] = new_distance

                heapq.heappush(
                    heap,
                    (new_distance, neighbor)
                )

    return distances


def shortest_path_distance(
    graph,
    source,
    target
):
    """
    Calculate shortest road-network distance
    between two nodes.
    """

    if source == target:
        return 0.0

    distances = {
        source: 0.0
    }

    heap = [
        (0.0, source)
    ]

    while heap:

        current_distance, current_node = (
            heapq.heappop(heap)
        )

        if current_node == target:
            return current_distance

        if current_distance != distances.get(
            current_node,
            math.inf
        ):
            continue

        for neighbor, edge_distance in graph.get(
            current_node,
            []
        ):

            new_distance = (
                current_distance
                + edge_distance
            )

            if new_distance < distances.get(
                neighbor,
                math.inf
            ):

                distances[neighbor] = new_distance

                heapq.heappush(
                    heap,
                    (new_distance, neighbor)
                )

    return math.inf