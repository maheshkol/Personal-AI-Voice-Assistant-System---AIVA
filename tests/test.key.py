import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Find and load .env explicitly
env_path = Path(__file__).parent.parent / ".env"
print(f"Looking for .env at: {env_path}")
print(f".env exists: {env_path.exists()}")

load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {bool(api_key)}")

if not api_key:
    print("\n❌ ERROR: API key not found!")
    print("Check that your .env file contains:")
    print("GEMINI_API_KEY=your_actual_key_here")
    exit(1)

print(f"API Key loaded: {api_key[:10]}...")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello as AIVA voice assistant in one sentence."
)

print("\n✅ SUCCESS!")
print("Response:", response.text)