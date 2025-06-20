import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

load_dotenv()

project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.getenv("AZURE_FOUNDRY_ENDPOINT"))

agentIdList = ["asst_1DYZAop1Obe8KQSVucC7JcpW", "asst_HIq5x9Gelzk6PlfX30LpIMxy", "asst_yksk9SIQhvbf4dCLnoKHPNM8", "asst_w79HcJ15MGIat8yvZNcW4kqs", "asst_DXpD2zd3Uc3t6gRxu9IdBl8Y"]

print("Which agent would you like to chat with?")
agents = ["Image Conscious Enthusiast","Practical DIYer","Car-Involved Tinker", "Diligent Delegator", "Disinterested Value Seeker"]

for i in range(len(agentIdList)):
    print(f"{i + 1}. {agents[i]}")

agent_choice = input("Enter the number of the agent you want to chat with: ")

print("Which model would you like to use?\n\t1. gpt-4o\n\t2. gpt-4.1")
model_choice = input("Enter the number of the model you want to use: ")
if model_choice == "1":
    model = "gpt-4o"
elif model_choice == "2":
    model = "gpt-4.1"

agent = project.agents.get_agent(agentIdList[int(agent_choice) - 1])
project.agents.update_agent(
    agent.id,
    model=model
)

thread = project.agents.threads.create()
print(f"Created thread, ID: {thread.id}")
print('Hello, I am the ' + agents[int(agent_choice) - 1] + ' model!\n If you want to end the chat type exit ,quit, q')

with open(thread.id, "w") as output_file:
    while True:
        user_prompt = input("\n-You: ")
        if user_prompt.lower() in ["exit", "quit", "q"]:
            print("Ending chat session.")
            break
        output_file.write(user_prompt)
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
            #if messages and messages[-1].text_messages:
            #     output_file.write(f"{messages[-1].role}: {messages[-1].text_messages[-1].text.value}\n")
            print("----------------CURRENT THREAD: \n")
            for message in messages:
                if message.text_messages:
                    print(f"{message.role}: {message.text_messages[-1].text.value}")
        
