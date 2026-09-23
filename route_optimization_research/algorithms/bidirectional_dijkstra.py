import heapq
import time


def bidirectional_dijkstra(
    graph,
    reverse_graph,
    source,
    target
):
    """
    Bidirectional Dijkstra for a directed weighted graph.

    Parameters
    ----------
    graph : dict
        Forward adjacency list.
        graph[u] = [(v, weight), ...]

    reverse_graph : dict
        Reverse adjacency list.
        reverse_graph[v] = [(u, weight), ...]

    source : int
        Starting node.

    target : int
        Destination node.

    Returns
    -------
    dict
        Same result structure as Dijkstra and A*.
    """

    start_time = time.perf_counter()

    # ------------------------------------------------------------
    # SOURCE == TARGET
    # ------------------------------------------------------------

    if source == target:
        elapsed = (time.perf_counter() - start_time) * 1000

        return {
            "algorithm": "Bidirectional Dijkstra",
            "distance_km": 0.0,
            "path": [source],
            "execution_time_ms": elapsed,
            "nodes_explored": 1,
            "found": True
        }

    # ------------------------------------------------------------
    # DISTANCE / PREDECESSOR DATA
    # ------------------------------------------------------------

    # Forward search:
    # source -> target
    forward_dist = {source: 0.0}
    forward_prev = {}

    # Backward search:
    # target -> source through reverse graph
    backward_dist = {target: 0.0}

    # For reconstruction:
    #
    # If p -> v is an original graph edge and the backward search
    # discovers p from v using reverse_graph, then:
    #
    # backward_next[p] = v
    #
    # This allows:
    #
    # meeting_node -> ... -> target
    backward_next = {}

    # ------------------------------------------------------------
    # PRIORITY QUEUES
    # ------------------------------------------------------------

    forward_queue = [
        (0.0, source)
    ]

    backward_queue = [
        (0.0, target)
    ]

    # ------------------------------------------------------------
    # SEARCH STATE
    # ------------------------------------------------------------

    forward_settled = set()
    backward_settled = set()

    best_distance = float("inf")
    meeting_node = None

    nodes_explored = 0

    # ------------------------------------------------------------
    # MAIN BIDIRECTIONAL SEARCH
    # ------------------------------------------------------------

    while forward_queue or backward_queue:

        # --------------------------------------------------------
        # CURRENT MINIMUM DISTANCES
        # --------------------------------------------------------

        forward_min = (
            forward_queue[0][0]
            if forward_queue
            else float("inf")
        )

        backward_min = (
            backward_queue[0][0]
            if backward_queue
            else float("inf")
        )

        # --------------------------------------------------------
        # CORRECT TERMINATION CONDITION
        #
        # Once:
        #
        # min_forward + min_backward >= best_distance
        #
        # no unexplored combination can produce a shorter path.
        # --------------------------------------------------------

        if (
            meeting_node is not None
            and forward_min + backward_min >= best_distance
        ):
            break

        # --------------------------------------------------------
        # EXPAND THE SEARCH WITH THE SMALLER FRONTIER KEY
        # --------------------------------------------------------

        if forward_min <= backward_min:

            current_distance, current = heapq.heappop(
                forward_queue
            )

            # Ignore stale priority-queue entries
            if current_distance != forward_dist.get(
                current,
                float("inf")
            ):
                continue

            if current in forward_settled:
                continue

            forward_settled.add(current)
            nodes_explored += 1

            # ----------------------------------------------------
            # IF THIS NODE WAS ALREADY REACHED FROM BACKWARD SIDE
            # ----------------------------------------------------

            if current in backward_dist:

                total_distance = (
                    current_distance
                    + backward_dist[current]
                )

                if total_distance < best_distance:
                    best_distance = total_distance
                    meeting_node = current

            # ----------------------------------------------------
            # RELAX FORWARD EDGES
            # ----------------------------------------------------

            for neighbor, weight in graph.get(
                current,
                []
            ):

                new_distance = (
                    current_distance + weight
                )

                if new_distance < forward_dist.get(
                    neighbor,
                    float("inf")
                ):

                    forward_dist[neighbor] = new_distance
                    forward_prev[neighbor] = current

                    heapq.heappush(
                        forward_queue,
                        (
                            new_distance,
                            neighbor
                        )
                    )

                    # Check whether backward search already
                    # reached this node.
                    if neighbor in backward_dist:

                        total_distance = (
                            new_distance
                            + backward_dist[neighbor]
                        )

                        if total_distance < best_distance:
                            best_distance = total_distance
                            meeting_node = neighbor

        else:

            current_distance, current = heapq.heappop(
                backward_queue
            )

            # Ignore stale priority-queue entries
            if current_distance != backward_dist.get(
                current,
                float("inf")
            ):
                continue

            if current in backward_settled:
                continue

            backward_settled.add(current)
            nodes_explored += 1

            # ----------------------------------------------------
            # IF THIS NODE WAS ALREADY REACHED FROM FORWARD SIDE
            # ----------------------------------------------------

            if current in forward_dist:

                total_distance = (
                    forward_dist[current]
                    + current_distance
                )

                if total_distance < best_distance:
                    best_distance = total_distance
                    meeting_node = current

            # ----------------------------------------------------
            # RELAX REVERSE EDGES
            #
            # reverse_graph[current] contains:
            #
            # predecessor -> current
            #
            # Therefore, if predecessor is discovered, its next
            # node on the original route is "current".
            # ----------------------------------------------------

            for predecessor, weight in reverse_graph.get(
                current,
                []
            ):

                new_distance = (
                    current_distance + weight
                )

                if new_distance < backward_dist.get(
                    predecessor,
                    float("inf")
                ):

                    backward_dist[predecessor] = new_distance

                    backward_next[predecessor] = current

                    heapq.heappush(
                        backward_queue,
                        (
                            new_distance,
                            predecessor
                        )
                    )

                    # Check whether forward search already
                    # reached this predecessor.
                    if predecessor in forward_dist:

                        total_distance = (
                            forward_dist[predecessor]
                            + new_distance
                        )

                        if total_distance < best_distance:
                            best_distance = total_distance
                            meeting_node = predecessor

    # ------------------------------------------------------------
    # NO PATH FOUND
    # ------------------------------------------------------------

    if meeting_node is None:

        elapsed = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "algorithm": "Bidirectional Dijkstra",
            "distance_km": None,
            "path": [],
            "execution_time_ms": elapsed,
            "nodes_explored": nodes_explored,
            "found": False
        }

    # ------------------------------------------------------------
    # RECONSTRUCT SOURCE -> MEETING NODE
    # ------------------------------------------------------------

    forward_path = []

    current = meeting_node

    while current != source:

        forward_path.append(current)

        if current not in forward_prev:
            # Safety check
            elapsed = (
                time.perf_counter() - start_time
            ) * 1000

            return {
                "algorithm": "Bidirectional Dijkstra",
                "distance_km": None,
                "path": [],
                "execution_time_ms": elapsed,
                "nodes_explored": nodes_explored,
                "found": False
            }

        current = forward_prev[current]

    forward_path.append(source)

    forward_path.reverse()

    # ------------------------------------------------------------
    # RECONSTRUCT MEETING NODE -> TARGET
    # ------------------------------------------------------------

    backward_path = []

    current = meeting_node

    while current != target:

        if current not in backward_next:
            # Safety check
            elapsed = (
                time.perf_counter() - start_time
            ) * 1000

            return {
                "algorithm": "Bidirectional Dijkstra",
                "distance_km": None,
                "path": [],
                "execution_time_ms": elapsed,
                "nodes_explored": nodes_explored,
                "found": False
            }

        current = backward_next[current]

        backward_path.append(current)

    # ------------------------------------------------------------
    # COMPLETE PATH
    # ------------------------------------------------------------

    path = forward_path + backward_path

    elapsed = (
        time.perf_counter() - start_time
    ) * 1000

    return {
        "algorithm": "Bidirectional Dijkstra",
        "distance_km": best_distance,
        "path": path,
        "execution_time_ms": elapsed,
        "nodes_explored": nodes_explored,
        "found": True
    }