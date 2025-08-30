import os
import subprocess
from google.genai import types

def run_python_file(working_directory, file_path, args=[]):
    abs_working = os.path.abspath(working_directory)
    abs_target = os.path.abspath(os.path.join(working_directory, file_path))

    if not abs_target.startswith(abs_working):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(abs_target): 
        return f'Error: File "{file_path}" not found.'
    
    ext = os.path.splitext(file_path)[1]
    if not ext == ".py":
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        result = subprocess.run(
            ['python', abs_target] + (args or []),
            capture_output=True, text=True, timeout=30, cwd=abs_working)

        output_parts = []

        if result.stdout:
            output_parts.append(f'STDOUT:\n{result.stdout}')
        if result.stderr:
            output_parts.append(f'STDERR:\n{result.stderr}')
        if result.returncode != 0:
            output_parts.append(f'Process exited with code {result.returncode}')  
        
        if output_parts:
            return "\n".join(output_parts)
        else:
            return "No output produced."
            
    except Exception as e:
        return f"Error: executing Python file: {e}"
    


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute a Python file with optional string arguments.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to run, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional arguments to pass to the script.",
            ),
        },
        required=["file_path"],
    ),
)