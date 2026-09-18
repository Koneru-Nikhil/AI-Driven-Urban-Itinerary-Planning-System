import pandas as pd
import numpy as np
from model.utils.proxy_call import GeminiCall


# Paths
csv_path = "model/data/shanghai_en.csv"
output_path = "model/data/shanghai_en.npy"


# Load dataset
data = pd.read_csv(csv_path)

print("Dataset columns:", data.columns.tolist())
print("Number of POIs:", len(data))


# Create text for embedding
# The dataset already contains the POI information in the "context" column.
context = (
    data["name"].astype(str)
    + " "
    + data["context"].astype(str)
)


# Create Gemini client
proxy = GeminiCall()

print("Generating Gemini embeddings...")


# Generate embeddings
response = proxy.embedding(
    input_data=context.tolist()
)


# Convert response to NumPy array
embeddings = np.array([
    record["embedding"]
    for record in response["data"]
])


print("Embedding shape:", embeddings.shape)


# Save embeddings
np.save(output_path, embeddings)

print("Successfully saved:")
print(output_path)