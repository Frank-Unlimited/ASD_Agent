from openai import OpenAI
import os
from dotenv import load_dotenv

# Re-construct .env path relative to root
env_path = "services/GraphRag/GraphRAG/.env"
load_dotenv(env_path)

api_key = os.getenv("GRAPHRAG_EMBEDDING_API_KEY")
base_url = os.getenv("GRAPHRAG_EMBEDDING_API_BASE")
model = os.getenv("GRAPHRAG_EMBEDDING_MODEL")

print(f"Testing Embedding API:")
print(f"Base URL: {base_url}")
print(f"Model: {model}")
print(f"API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("Error: API Key not found in .env")
    exit(1)

client = OpenAI(
    api_key=api_key,
    base_url=base_url,
)

try:
    response = client.embeddings.create(
        input="Hello world",
        model=model
    )
    print("\nSuccess!")
    print(f"Embedding length: {len(response.data[0].embedding)}")
    print(f"First 5 values: {response.data[0].embedding[:5]}")
except Exception as e:
    print(f"\nError details: {e}")
