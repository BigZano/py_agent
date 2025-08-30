import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types


from config import system_prompt, MAX_ITERS 
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

def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents = messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt)
    )

    messages.append(response.candidates[0].content)

    
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


    if response.function_calls:
        function_responses = []
        for fc in response.function_calls:
            if fc.name == "run_python_file" and "args" not in (fc.args or {}):
                fc.args = dict(fc.args or {})
                fc.args["args"] = []

            function_call_result = call_function(fc, verbose=verbose)

            function_responses.append(function_call_result.parts[0])

            fr = function_call_result.parts[0].function_response.response
            if fr is None:
                raise RuntimeError("Missing function_response.response from tool call")
            if verbose:
                print(f"-> {fr}")

        
        messages.append(types.Content(role="user", parts=function_responses))
        return None 
    else:
        return response.text



def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    client = genai.Client(api_key = api_key)

    if len(sys.argv) < 2:
        print("error: prompt required")
        sys.exit(1)

    user_prompt = sys.argv[1]

    verbose = "--verbose" in sys.argv

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    iters = 0
    while True:
        iters += 1
        if iters > MAX_ITERS:
            print(f"Maximum iterations ({MAX_ITERS}) reached without a final response.")
            sys.exit(1)

        try:
            final_response = generate_content(client, messages, verbose)
            if final_response:
                print("Final response:")
                print(final_response)
                break 
        except Exception as e:
            print(f"Error during agent execution: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()