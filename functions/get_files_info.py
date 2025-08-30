# python
import os
from google.genai import types

def get_files_info(working_directory, directory="."):
    abs_working = os.path.abspath(working_directory)
    abs_target = os.path.abspath(os.path.join(working_directory, directory))

    if not abs_target.startswith(abs_working):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(abs_target):
        return f'Error: "{directory}" is not a directory'

    try:
        entries = os.listdir(abs_target)
        lines = []
        for name in entries:
            full = os.path.join(abs_target, name)
            is_dir = os.path.isdir(full)
            size = os.path.getsize(full)
            lines.append(f'- {name}: file_size={size} bytes, is_dir={is_dir}')
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"
    

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="List files and directories for a given path.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory to list, relative to the working directory.",
            ),
        },
        required=["directory"],
    ),
)


