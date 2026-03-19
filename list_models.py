
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Listing models...")
try:
    models = client.models.list()
    print("Flash models found:")
    for m in models:
        if "flash" in m.name.lower():
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
