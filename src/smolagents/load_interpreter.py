import ast
import os
import dill
import base64

def main():
    # Retrieve the necessary environment variables
    encoded_interpreter = os.getenv('ENCODED_INTERPRETER')
    code_action = os.getenv('CODE_ACTION')
    additional_variables = ast.literal_eval(os.getenv('ADDITIONAL_VARIABLES')) # convert the string back to a dict

    if encoded_interpreter:
        try:
            dill_object = base64.b64decode(encoded_interpreter)
            interpreter = dill.loads(dill_object)

            out = interpreter(code_action, additional_variables)
            print(out) # output gets parsed by the docker executor

        except dill.UnpicklingError as e:
            print(f"Error unpickling object: {e}")
        except Exception as e:
            print(f"Error processing object: {e}")
    else:
        print("No dill object found in environment variable ENCODED_INTERPRETER")

if __name__ == "__main__":
    main()
