import requests
import json

print("🚀 Testing TRUE streaming endpoint with STORM callbacks...")
print("=" * 60)

# Send request with streaming enabled
response = requests.post(
    "http://localhost:8000/query/stream",
    json={"topic": "Python Programming"},
    stream=True  # This enables streaming!
)

print("✅ Request sent. Streaming progress in real-time:")
print("=" * 60)

# Print chunks as they arrive (decoded)
for chunk in response:
    try:
        # Decode bytes to string
        decoded = chunk.decode('utf-8')
        print(decoded, end="", flush=True)
    except:
        # Fallback for any unexpected encoding issues
        print(chunk, end="", flush=True)

print("\n" + "=" * 60)
print("✅ Streaming complete!")