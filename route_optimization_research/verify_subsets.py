import pandas as pd
import networkx as nx
import os

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = "graph_subsets"

SIZES = [
    "10K",
    "25K",
    "50K",
    "100K",
    "250K",
    "500K"
]

print("=" * 60)
print("VERIFYING HYDERABAD GRAPH SUBSETS")
print("=" * 60)

results = []

# ============================================================
# CHECK EACH SUBSET
# ============================================================

for size in SIZES:

    print("\n" + "-" * 60)
    print(f"Checking {size} graph...")

    node_file = os.path.join(
        DATA_DIR,
        f"Hyderabad_{size}_Nodes.csv"
    )

    edge_file = os.path.join(
        DATA_DIR,
        f"Hyderabad_{size}_Edges.csv"
    )

    nodes_df = pd.read_csv(node_file)
    edges_df = pd.read_csv(edge_file)

    print(f"Nodes loaded : {len(nodes_df):,}")
    print(f"Edges loaded : {len(edges_df):,}")

    # Create undirected graph for connectivity check
    G = nx.Graph()

    G.add_nodes_from(nodes_df["node_id"])

    G.add_edges_from(
        edges_df[["source", "target"]].itertuples(
            index=False,
            name=None
        )
    )

    components = list(nx.connected_components(G))

    components.sort(key=len, reverse=True)

    largest_component = len(components[0])

    connected = (
        len(components) == 1
    )

    print(f"Connected components: {len(components):,}")
    print(
        f"Largest component : {largest_component:,} nodes"
    )

    if connected:
        print("STATUS: CONNECTED ✓")
    else:
        print("STATUS: NOT FULLY CONNECTED")

    results.append({
        "Graph": size,
        "Nodes": len(nodes_df),
        "Edges": len(edges_df),
        "Components": len(components),
        "Largest_Component": largest_component,
        "Connected": connected
    })


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("CONNECTIVITY SUMMARY")
print("=" * 60)

results_df = pd.DataFrame(results)

print(results_df.to_string(index=False))

results_df.to_csv(
    "graph_connectivity_results.csv",
    index=False
)

print("\nSaved:")
print("graph_connectivity_results.csv")

print("\nVerification completed.")