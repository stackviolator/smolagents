# ExecutorDockerfile
FROM python:3.12-slim

WORKDIR /app

COPY src/smolagents/load_interpreter.py ./

COPY . /app/smolagents

RUN pip install dill ./smolagents

CMD ["python", "load_interpreter.py"]