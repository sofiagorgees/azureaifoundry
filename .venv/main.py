
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import ListSortOrder, FilePurpose

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://sgorgees-exploring-resource.services.ai.azure.com/api/projects/sgorgees-exploring"
)

#agent id for data helper agent
agent = project.agents.get_agent("asst_jWLxM8twZtAHEtXW99SpdXZC")

#creates new thread
thread = project.agents.threads.create()


message = project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="How many spaces are in a tab?"
)

run = project.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=agent.id)

if run.status == "failed":
    print(f"Run failed: {run.last_error}")
else:
    messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

    for message in messages:
        if message.text_messages:
            print(f"{message.role}: {message.text_messages[-1].text.value}")