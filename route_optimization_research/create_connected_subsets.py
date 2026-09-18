import pandas as pd
import networkx as nx
import os
from collections import deque

# ============================================================
# CONFIGURATION
# ============================================================

NODES_FILE = "Hyderabad_Largest_Component_Nodes.csv"
EDGES_FILE = "Hyderabad_Largest_Component_Edges.csv"

TARGET_SIZES = [
    10000,
    25000,
    50000,
    100000,
    250000,
    500000
]

OUTPUT_DIR = "connected_subsets"

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("CREATING CORRECTLY CONNECTED GRAPH SUBSETS")
print("=" * 60)

print("\nLoading nodes...")
nodes_df = pd.read_csv(NODES_FILE)

print("Loading edges...")
edges_df = pd.read_csv(EDGES_FILE)

print(f"Available nodes: {len(nodes_df):,}")
print(f"Available edges: {len(edges_df):,}")

# ============================================================
# BUILD UNDIRECTED GRAPH FOR CONNECTIVITY
# ============================================================

print("\nBuilding connectivity graph...")

G = nx.Graph()

# Add nodes
for node_id in nodes_df["node_id"]:
    G.add_node(node_id)

# Add edges
for row in edges_df.itertuples(index=False):

    G.add_edge(
        row.source,
        row.target
    )

print(
    f"Graph nodes: {G.number_of_nodes():,}"
)

print(
    f"Graph edges: {G.number_of_edges():,}"
)

# ============================================================
# OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

# ============================================================
# CONNECTED SUBGRAPH GROWTH
# ============================================================

# Start from a deterministic node
start_node = nodes_df.iloc[0]["node_id"]

print("\nStarting node:", start_node)

selected = set()
queue = deque()

selected.add(start_node)
queue.append(start_node)

# ============================================================
# GROW CONNECTED SET
# ============================================================

print("\nGrowing connected network...")

target_index = 0

while queue and target_index < len(TARGET_SIZES):

    current = queue.popleft()

    # Add neighboring nodes
    for neighbour in G.neighbors(current):

        if neighbour not in selected:

            selected.add(neighbour)
            queue.append(neighbour)

            # Check whether we reached next target
            if len(selected) >= TARGET_SIZES[target_index]:

                target = TARGET_SIZES[target_index]

                print("\n" + "-" * 60)
                print(
                    f"Creating connected {target:,}-node graph..."
                )

                # Take exactly target nodes
                target_nodes = list(selected)[:target]

                target_set = set(target_nodes)

                # ------------------------------------------------
                # IMPORTANT:
                # Keep ONLY edges between selected nodes.
                # Because nodes were added through connectivity,
                # the resulting graph remains connected.
                # ------------------------------------------------

                subset_nodes = nodes_df[
                    nodes_df["node_id"].isin(target_set)
                ].copy()

                subset_edges = edges_df[
                    edges_df["source"].isin(target_set)
                    &
                    edges_df["target"].isin(target_set)
                ].copy()

                print(
                    f"Nodes: {len(subset_nodes):,}"
                )

                print(
                    f"Edges: {len(subset_edges):,}"
                )

                # ------------------------------------------------
                # VERIFY CONNECTIVITY
                # ------------------------------------------------

                test_graph = nx.Graph()

                test_graph.add_nodes_from(
                    subset_nodes["node_id"]
                )

                test_graph.add_edges_from(
                    subset_edges[
                        ["source", "target"]
                    ].itertuples(
                        index=False,
                        name=None
                    )
                )

                components = nx.number_connected_components(
                    test_graph
                )

                largest = max(
                    len(c)
                    for c in nx.connected_components(test_graph)
                )

                print(
                    f"Connected components: {components}"
                )

                print(
                    f"Largest component: {largest:,}"
                )

                if components == 1:
                    print("STATUS: CONNECTED ✓")
                else:
                    print(
                        "WARNING: NOT FULLY CONNECTED"
                    )

                # ------------------------------------------------
                # SAVE
                # ------------------------------------------------

                node_file = os.path.join(
                    OUTPUT_DIR,
                    f"Hyderabad_{target//1000}K_Nodes.csv"
                )

                edge_file = os.path.join(
                    OUTPUT_DIR,
                    f"Hyderabad_{target//1000}K_Edges.csv"
                )

                subset_nodes.to_csv(
                    node_file,
                    index=False
                )

                subset_edges.to_csv(
                    edge_file,
                    index=False
                )

                print("\nSaved:")
                print(node_file)
                print(edge_file)

                target_index += 1

                if target_index >= len(TARGET_SIZES):
                    break

# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 60)
print("CONNECTED SUBSET CREATION COMPLETED")
print("=" * 60)

print(
    f"Total selected nodes: {len(selected):,}"
)