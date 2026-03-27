import pandas as pd
import json

# Load dataset (adjust filename if needed)
df = pd.read_csv("train.csv")

# Combine toxicity-related columns into one score
df["toxicity"] = df[
    ["toxic", "severe_toxic", "insult", "threat", "obscene"]
].mean(axis=1)

# Keep only necessary columns
df = df[["comment_text", "toxicity"]]

# Drop empty values
df = df.dropna()

# Sample small subset (IMPORTANT for hackathon)
df = df.sample(300, random_state=42)

# Save as JSON
data = df.to_dict(orient="records")

# Create data folder if not exists
import os
os.makedirs("data", exist_ok=True)

with open("data/comments.json", "w") as f:
    json.dump(data, f, indent=2)

print("Saved data/comments.json with", len(data), "entries")