import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

candidates = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-flash-latest",
]

for name in candidates:
    try:
        print(f"Trying {name}...")
        resp = client.models.generate_content(
            model=name,
            contents="Reply with exactly: API working",
        )
        print("WORKS:", name)
        print("TEXT:", resp.text)
        break
    except (errors.ServerError, errors.ClientError) as e:
        print("  failed:", str(e)[:80])