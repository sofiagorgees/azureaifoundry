from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://sgorgees-exploring-resource.services.ai.azure.com/api/projects/sgorgees-exploring")


agent = project.agents.get_agent("asst_fGV7F0M0Vic9UEzL2YlUGFVW")

thread = project.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

chat = True
print('Hello, I am the image conscious enthusiast model!\n If you want to end the chat type exit ,quit, q')
while chat:
    user_prompt = input("\n-You: ")
    if user_prompt.lower() in ["exit", "quit", "q"]:
        print("Ending chat session.")
        break
    message = project.agents.messages.create(
        thread_id = thread.id,
        role ="user",
        content = user_prompt
    )
    print(f"Created message, ID: {message['id']}")

    run = project.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id)

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    else:
        messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

        print("----------------CURRENT THREAD: \n")
        for message in messages:
            if message.text_messages:
                print(f"{message.role}: {message.text_messages[-1].text.value}")
