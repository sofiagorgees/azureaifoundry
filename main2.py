import os
from dotenv import load_dotenv
load_dotenv()

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

# from azure.ai.inference import ChatCompletionsClient
# from azure.ai.inference.models import SystemMessage, UserMessage
# from azure.core.credentials import AzureKeyCredential

# Create project client with default azure credentials and endpoint from environment variable
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.getenv("AZURE_FOUNDRY_ENDPOINT"),
    )    

# agentIdList = ["asst_1DYZAop1Obe8KQSVucC7JcpW", "asst_HIq5x9Gelzk6PlfX30LpIMxy", "asst_yksk9SIQhvbf4dCLnoKHPNM8", "asst_w79HcJ15MGIat8yvZNcW4kqs", "asst_DXpD2zd3Uc3t6gRxu9IdBl8Y"]

#Chose and agent and model to chat with
print("Which agent would you like to chat with?")
agents = ["Image Conscious Enthusiast","Practical DIYer","Car-Involved Tinker", "Diligent Delegator", "Disinterested Value Seeker"]
for i in range(len(agents)):
    print(f"{i + 1}. {agents[i]}")

agent_choice = input("Enter the number of the agent you want to chat with: ")
print("Which model would you like to use?\n\t1. gpt-4o\n\t2. gpt-4.1")
model_choice = input("Enter the number of the model you want to use: ")
if model_choice == "1":
    model = "gpt-4o"
elif model_choice == "2":
    model = "gpt-4.1"

# Create a new agent with the selected model and name
agent = project.agents.create_agent(
    model=model,
    name = agents[int(agent_choice) - 1],
    instructions = "REPLACE WITH INSTRUCTIONS"
)
#Create new thread
thread = project.agents.threads.create()
print(f"Created thread, ID: {thread.id}")

print('Hello, I am the ' + agents[int(agent_choice) - 1] + ' model!\n If you want to end the chat type exit ,quit, q')

# Loop to chat with the agent
while True:
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

project.agents.delete_agent(agent.id)
print(f"Deleted agent, ID: {agent.id}")

    

