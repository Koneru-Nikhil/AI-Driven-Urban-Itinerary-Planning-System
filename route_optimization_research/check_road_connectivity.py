import pandas as pd
import networkx as nx

print("=" * 60)
print("HYDERABAD ROAD NETWORK CONNECTIVITY ANALYSIS")
print("=" * 60)

# Load data
print("\nLoading road data...")

nodes_df = pd.read_csv("Hyderabad_Road_Nodes.csv")
edges_df = pd.read_csv("Hyderabad_Road_Edges.csv")

print("Nodes loaded:", len(nodes_df))
print("Edges loaded:", len(edges_df))

# Create directed graph
print("\nBuilding graph...")

G = nx.DiGraph()

# Add nodes
for node_id in nodes_df["node_id"]:
    G.add_node(node_id)

# Add edges
for row in edges_df.itertuples(index=False):
    G.add_edge(
        row.source,
        row.target,
        distance_km=row.distance_km,
        highway=row.highway
    )

print("Graph created.")
print("Graph nodes:", G.number_of_nodes())
print("Graph edges:", G.number_of_edges())

# ------------------------------------------------------------
# WEAKLY CONNECTED COMPONENTS
# ------------------------------------------------------------

print("\nCalculating connected components...")

components = list(nx.weakly_connected_components(G))

components.sort(key=len, reverse=True)

print("\nTotal connected components:", len(components))

print("\nLargest components:")
print("-" * 50)

for i, component in enumerate(components[:10], start=1):
    print(f"Component {i}: {len(component):,} nodes")

# ------------------------------------------------------------
# LARGEST COMPONENT
# ------------------------------------------------------------

largest_component = components[0]

largest_graph = G.subgraph(largest_component).copy()

print("\n" + "=" * 60)
print("LARGEST CONNECTED ROAD NETWORK")
print("=" * 60)

print("Nodes :", f"{largest_graph.number_of_nodes():,}")
print("Edges :", f"{largest_graph.number_of_edges():,}")

# ------------------------------------------------------------
# SAVE LARGEST COMPONENT
# ------------------------------------------------------------

largest_node_ids = set(largest_component)

largest_nodes_df = nodes_df[
    nodes_df["node_id"].isin(largest_node_ids)
].copy()

largest_edges_df = edges_df[
    edges_df["source"].isin(largest_node_ids)
    & edges_df["target"].isin(largest_node_ids)
].copy()

largest_nodes_df.to_csv(
    "Hyderabad_Largest_Component_Nodes.csv",
    index=False
)

largest_edges_df.to_csv(
    "Hyderabad_Largest_Component_Edges.csv",
    index=False
)

print("\nFiles created:")
print("1. Hyderabad_Largest_Component_Nodes.csv")
print("2. Hyderabad_Largest_Component_Edges.csv")

print("\nDONE.")