import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key = api_key)

if len(sys.argv) < 2:
    print("error: prompt required")
    sys.exit(1)

prompt = sys.argv[1]

is_verbose = False
if "--verbose" in sys.argv:
    is_verbose = True

messages = [
    types.Content(role="user", parts=[types.Part(text=prompt)]),
]

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents = messages, 
)

prompt_tokens = response.usage_metadata.prompt_token_count
response_tokens = response.usage_metadata.candidates_token_count

print(response.text)

if is_verbose:
    print(f"User prompt:, {prompt}")
    print(f"Prompt tokens:, {prompt_tokens}")
    print(f"Response tokens:, {response_tokens}")