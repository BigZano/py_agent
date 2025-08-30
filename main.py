import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from config import system_prompt
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python import schema_run_python_file
from functions.write_file import schema_write_file
from functions.call_function import call_function

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key = api_key)

if len(sys.argv) < 2:
    print("error: prompt required")
    sys.exit(1)

prompt = sys.argv[1]

verbose = "--verbose" in sys.argv

messages = [
    types.Content(role="user", parts=[types.Part(text=prompt)]),
]

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents = messages,
    config=types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt) 
)

prompt_tokens = response.usage_metadata.prompt_token_count
response_tokens = response.usage_metadata.candidates_token_count


# python
if response.function_calls:
    for fc in response.function_calls:
        if fc.name == "run_python_file" and "args" not in (fc.args or {}):
            fc.args = dict(fc.args or {})
            fc.args["args"] = []

        function_call_result = call_function(fc, verbose=verbose)

        fr = function_call_result.parts[0].function_response.response
        if fr is None:
            raise RuntimeError("Missing function_response.response from tool call")
        if verbose:
            print(f"-> {fr}")
else:
    print(response.text)

if verbose:
    print(f"User prompt: {prompt}")
    print(f"Prompt tokens: {prompt_tokens}")
    print(f"Response tokens: {response_tokens}")