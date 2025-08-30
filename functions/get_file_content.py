import os
from config import MAX_CHARS
from google.genai import types

def get_file_content(working_directory, file_path):
    abs_working = os.path.abspath(working_directory)
    abs_target = os.path.abspath(os.path.join(working_directory, file_path))


    if not abs_target.startswith(abs_working):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'


    if not os.path.isfile(abs_target):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(abs_target, 'r') as file:
            file_content_string = file.read(MAX_CHARS)

            if file.read(1) != "":
                file_content_string += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            
            return file_content_string


    except Exception as e:
        return f'Error: {e}'
    
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Retrieves the content of a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to read, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)