import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

load_dotenv()
# Upload a file to OneDrive for Business using Office365-REST-Python-Client
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

# 1. Point at your OneDrive for Business site (it’s just a special SP site):
site_url = 'https://oldworld-my.sharepoint.com/personal/sgorgees_oldworldind_com'

ctx = ClientContext(site_url).with_credentials(
    UserCredential("sgorgees@oldworldind.com", "Turtle10!")
)
# 3. Target a folder (e.g. Documents)
folder = ctx.web.get_folder_by_server_relative_url("/personal/you_contoso_onmicrosoft_com/Documents")
folder = ctx.web.get_folder_by_server_relative_url("/personal/you_contoso_onmicrosoft_com/Documents")

# 4. Upload your text file
with open("hello.txt", "rb") as f:
    file_content = f.read()
uploaded = folder.upload_file("hello.txt", file_content).execute_query()

print("✔ Uploaded at:", uploaded.serverRelativeUrl)

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
print('Hello, I am the ' + agents[int(agent_choice) - 1] + ' agent using '+ model +' model!\n If you want to end the chat type exit, quit, q')
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
    with open(thread.id, "w", encoding = "utf-8") as output_file:
        output_file.write('MessageRole.AGENT:Hello, I am the ' + agents[int(agent_choice) - 1] + ' agent using '+ model +' model!\n')
        for message in messages:
            if message.text_messages:
                print(f"{message.role}: {message.text_messages[-1].text.value}")
                output_file.write(f"{message.role}: {message.text_messages[-1].text.value}\n") 
        output_file.write(f"end of thread {thread.id}\n")       
