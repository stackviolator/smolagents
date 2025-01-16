from smolagents import (
    CodeAgent,
    HfApiModel,
    GradioUI,
    DuckDuckGoSearchTool
)

web_tool = DuckDuckGoSearchTool()

agent = CodeAgent(
    tools=[web_tool], model=HfApiModel(), max_steps=4, verbosity_level=1, executor="docker"
)

GradioUI(agent, file_upload_folder='./data').launch()

agent.run("What is the weather in Istanbul")