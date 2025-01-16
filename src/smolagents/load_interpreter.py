import ast
import os
import smolagents
import importlib

def deserialize_tool_dict(data: str) -> dict:
    data = ast.literal_eval(data)
    tool_dict = {}
    for key, path in data.items():
        module_path, class_name = path.rsplit(".", 1)
        mod = importlib.import_module(module_path)

        cls = getattr(mod, class_name)
        tool_dict[key] = cls()
    return tool_dict

def main():
    # Retrieve the necessary environment variables
    imports = os.getenv("AUTHORIZED_IMPORTS")
    tools = deserialize_tool_dict(os.getenv("TOOLS"))
    code_action = os.getenv('CODE_ACTION')
    additional_variables = ast.literal_eval(os.getenv('ADDITIONAL_VARIABLES'))

    try:
        interpreter = smolagents.local_python_executor.LocalPythonInterpreter(imports, tools)

        out = interpreter(code_action, additional_variables)
        print(out) # output gets parsed by the docker executor

    except Exception as e:
        print(f"Error processing object: {e}")
if __name__ == "__main__":
    main()