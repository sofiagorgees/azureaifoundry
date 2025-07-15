import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder, FilePurpose, FileSearchTool

load_dotenv()
# Upload a file to OneDrive for Business using Office365-REST-Python-Client
#from office365.sharepoint.client_context import ClientContext
#from office365.runtime.auth.user_credential import 

# 1. Point at your OneDrive for Business site (it’s just a special SP site):
# site_url = os.getenv("SITE_URL")
# ctx = ClientContext(site_url).with_device_flow()
# # 3. Target a folder (e.g. Documents)
# folder = ctx.web.get_folder_by_server_relative_url(os.getenv("FOLDER_CTX_URL"))

# Create project client
project = AIProjectClient( 
    credential=DefaultAzureCredential(),
    endpoint=os.getenv("AZURE_FOUNDRY_ENDPOINT"))

# List of agent IDs from azure foundry portal
agentIdList = ["asst_1DYZAop1Obe8KQSVucC7JcpW", "asst_HIq5x9Gelzk6PlfX30LpIMxy", "asst_yksk9SIQhvbf4dCLnoKHPNM8", "asst_w79HcJ15MGIat8yvZNcW4kqs", "asst_DXpD2zd3Uc3t6gRxu9IdBl8Y"]
agents = ["Image Conscious Enthusiast","Practical DIYer", "Car-Involved Tinker", "Diligent Delegator", "Disinterested Value Seeker"]

# Get agent choice from user
print("Which agent would you like to chat with?")
for i in range(len(agentIdList)):
    print(f"{i + 1}. {agents[i]}")
agent_choice = input("Enter the number (1-5) of the agent you want to chat with: ")

# Get gpt model choice from user
print("Which model would you like to use?\n\t1. gpt-4o\n\t2. gpt-4.1")
model_choice = input("Enter the number of the model you want to use (enter 1 or 2): ")
if model_choice == "1":
    model_name = "gpt-4o"
elif model_choice == "2":
    model_name = "gpt-4.1"
agent = project.agents.get_agent(agentIdList[int(agent_choice) - 1])

# File add and search
file_path ="PUT FILE PATH HERE"

# Upload the file
file = project.agents.files.upload_and_poll(file_path=file_path, purpose=FilePurpose.AGENTS)
print(f"Uploaded file, file ID: {file.id}")

# Create a vector store for the file
vector_store = project.vector_stores.create_and_poll(file_ids=[file.id], name="my_vectorstore")
print(f"Created vector store, vector store ID: {vector_store.id}")

# Create a file search tool using the vector store
file_search_tool = FileSearchTool(vector_store_ids= [vector_store.id])

# Updates agent with chosen model and file search tool
project.agents.update_agent(
    agent.id,
    model=model_name,
    tools=[file_search_tool],
    tool_resources= file_search_tool.resources
)

# Create new thread
thread = project.agents.threads.create()

print(f"Created thread, ID: {thread.id}")
print('Hello, I am the ' + agents[int(agent_choice) - 1] + ' agent using '+ model_name +' model!\n If you want to end the chat at anytime type exit, quit, or q')

# Loop for conversation
while True:
    # Get and store user prompt
    user_prompt = input("\n-You: ")
    if user_prompt.lower() in ["exit", "quit", "q"]:
        print("Ending chat session.")    
        break

    # New message
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
    # Write updated thread to text file
    with open((thread.id + ".txt"), "w", encoding = "utf-8") as output_file:
        output_file.write('MessageRole.AGENT:Hello, I am the ' + agents[int(agent_choice) - 1] + ' agent using '+ model_name +' model!\n')
        for message in messages:
            if message.text_messages:
                # Print message to console
                print(f"{message.role}: {message.text_messages[-1].text.value}")
                # Write to file
                output_file.write(f"{message.role}: {message.text_messages[-1].text.value}\n") 
        output_file.write(f"end of thread {thread.id}\n")


# with open((thread.id + ".txt"), "rb") as f:
#     file_content = f.read()
# uploaded = folder.upload_file((thread.id + ".txt"), file_content).execute_query()       
# print("✔ Uploaded at:", uploaded.serverRelativeUrl)