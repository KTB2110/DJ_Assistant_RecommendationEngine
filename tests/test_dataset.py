from datasets import load_dataset

print("Loading Spotify dataset from Hugging Face...")

dataset = load_dataset("maharshipandya/spotify-tracks-dataset")

print(f"✓ Loaded dataset")
print(f"  Number of tracks: {len(dataset['train'])}")

# Look at one example
example = dataset['train'][0]
print(f"\nExample track:")
for key, value in example.items():
    print(f"  {key}: {value}")