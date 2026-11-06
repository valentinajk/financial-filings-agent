import os, time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.5-flash-lite"

def ask(prompt, retries=5):
    for attempt in range(retries):
        try:
            return client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0),
            ).text
        except errors.ServerError:
            print("Server busy, retrying in 15s...")
            time.sleep(15)
    raise RuntimeError("Model stayed busy, try again later")