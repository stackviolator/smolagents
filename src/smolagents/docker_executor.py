import ast
import docker
import dill
import base64
from typing import Any, Callable, Dict, List, Optional, Tuple

from .tool_validation import validate_tool_attributes
from .tools import Tool
from .utils import BASE_BUILTIN_MODULES, instance_to_source

def kill_self():
    import sys; sys.exit(0)

class DockerExecutor:
    def __init__(self, local_python_interpreter):
        self.image_name = "temp-python-executor"
        self.container_name = "smolagents-executor"

        self.local_python_interpreter = local_python_interpreter
        self.client = self.get_client()
        if self.client is False:
            print("[-] Docker daemon is not running. Start the daemon with \"sudo systemctl start docker\".")
            kill_self()

        self.encoded_obj = base64.b64encode(dill.dumps(local_python_interpreter)).decode('utf-8')
        self.image = self.build_image(self.image_name)

    """
    Only supports docker, not podman. Especially not on Mac. podman on Mac only uses ssh sockets, not unix sockets. Very annoying.
    """
    def get_client(self):
        try:
            client = docker.from_env()
            client.ping()
            return client
        except docker.errors.DockerException as e:
            print(f"Docker error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return False

    def build_image(self, image_name, force=False):
        try:
            existing_images = self.client.images.list(name=image_name)
            if existing_images and not force:
                print(f"Image \"{image_name}\" already exists. Skipping build...")
                return  # Skip building if the image exists and force is False
        except Exception as e:
            print(f"Error checking for existing image: {e}")

        try:
            if force:
                print(f"Removing existing image \"{image_name}\"...")
                self.client.images.remove(image=image_name, force=True)

            print(f"Building docker image \"{image_name}\" for local sandboxing...")
            image, build_logs = self.client.images.build(
                path=".",
                tag=image_name,
                rm=True,
                dockerfile="executor.Dockerfile"
            )
            print("Image built successfully!")
        except Exception as e:
            print(f"Failed to build image: {e}")

    def stop_container(self, container_name):
        container = self.client.containers.get(container_name)
        container.stop()
        container.remove()

    def execute_command(self, encoded_interpreter, code_action, additional_variables) -> Tuple[Any, str, bool]:
        try:
            container = self.client.containers.run(
                image=self.image_name,
                name=self.container_name,
                ports={"5000/tcp": 5000},
                environment={"ENCODED_INTERPRETER": encoded_interpreter, "CODE_ACTION": code_action, "ADDITIONAL_VARIABLES":additional_variables}
            )

            output = container.decode(('utf-8'))
            output = self.parse_tuple(output)
        finally:
            try:
                self.stop_container(container_name=self.container_name)
            except Exception as e:
                print(f"Error during container cleanup: {e}")
            return output

    def parse_tuple(self, input_str: str) -> Tuple[Any, str, bool]:
        try:
            input_str = input_str.rstrip()
            parsed_tuple = ast.literal_eval(input_str)

            if isinstance(parsed_tuple, tuple) and len(parsed_tuple) == 3:
                return parsed_tuple
            else:
                raise ValueError("The parsed data is not a valid tuple with 3 elements.")

        except Exception as e:
            print(f"Error parsing the input string: {e}")
            return None

    def __call__(
        self, code_action: str, additional_variables: Dict
    ) -> Tuple[Any, str, bool]:
        
        return self.execute_command(self.encoded_obj, code_action=code_action, additional_variables=additional_variables)