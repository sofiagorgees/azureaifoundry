import os
from dotenv import load_dotenv
load_dotenv()

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, AssistantMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Create project client with default azure credentials and endpoint from environment variable
# project = AIProjectClient(
#     credential=DefaultAzureCredential(),
#     endpoint=os.getenv("AZURE_FOUNDRY_ENDPOINT"),
#     )    

model_name = "DeepSeek-R1-0528"
client = ChatCompletionsClient(
    endpoint= os.getenv("COMPLETIONS_ENDPOINT"),
    credential= AzureKeyCredential(os.getenv("AZURE_FOUNDRY_API_KEY")), 
    api_version="2024-05-01-preview"
)
chat_history = [{"role": "system", "content": "You are a helpful assistant."}]

print('Hello, I am the model!\n If you want to end the chat type exit, quit, q')

while True:
    user_input = input("User: ")
    if user_input.lower() == "exit":
        break

    # Add user message to chat history
    chat_history.append({"role": "user", "content": user_input})

    # Call Azure OpenAI
    response = client.complete(
        model=model_name,
        messages=chat_history,
        temperature=0.7,
        max_tokens=1000
    )

    # Get assistant's reply
    assistant_message = response.choices[0].message
    print(f"Assistant: {assistant_message.content}\n")

    # Add assistant reply to chat history
    chat_history.append({"role": assistant_message.role, "content": assistant_message.content})

response = client.complete(
    messages=[
        SystemMessage(content="You are a helpful assistant."),
        UserMessage(content="I am going to Paris, what should I see?"),
    ],
    max_tokens=2048,
    model=model_name
)

print(response.choices[0].message.content)

# #Chose and agent and model to chat with
# print("Which agent would you like to chat with?")
# agents = ["Image Conscious Enthusiast","Practical DIYer","Car-Involved Tinker", "Diligent Delegator", "Disinterested Value Seeker"]
# for i in range(len(agents)):
#     print(f"{i + 1}. {agents[i]}")

# #chose a model
# agent_choice = input("Enter the number of the agent you want to chat with: ")
# print("Which model would you like to use?\n\t1. gpt-4o\n\t2. gpt-4.1")
# model_choice = input("Enter the number of the model you want to use: ")
# if model_choice == "1":
#     model = "gpt-4o"
# elif model_choice == "2":
#     model = "gpt-4.1"

# # Create a new agent with the selected model and name
# agent = project.agents.create_agent(
#     model=model,
#     name = agents[int(agent_choice) - 1],
#     instructions = "REPLACE WITH INSTRUCTIONS"
# )

# #get files from sharepoint


# #connect them to agent

# #Create new thread
# thread = project.agents.threads.create()
# print(f"Created thread, ID: {thread.id}")

# print('Hello, I am the ' + agents[int(agent_choice) - 1] + ' model!\n If you want to end the chat type exit, quit, q')

# # Loop to chat with the agent

# # Create a file to store the conversation
# with open(thread.id, "w") as output_file:
#     output_file.write(f"Chat started with agent: {agents[int(agent_choice) - 1]}\n")
# while True:
#     user_prompt = input("\n-You: ")
#     if user_prompt.lower() in ["exit", "quit", "q"]:
#         print("Ending chat session.")
#         break
#     message = project.agents.messages.create(
#         thread_id = thread.id,
#         role ="user",
#         content = user_prompt
#     )
#     print(f"Created message, ID: {message['id']}")

#     run = project.agents.runs.create_and_process(
#         thread_id=thread.id,
#         agent_id=agent.id)

#     if run.status == "failed":
#         print(f"Run failed: {run.last_error}")
#     else:
#         messages = project.agents.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

#         print("----------------CURRENT THREAD: \n")
#         for message in messages:
#             if message.text_messages:
#                 print(f"{message.role}: {message.text_messages[-1].text.value}")

# # Save the thread to the file

# # Save thread file to sharepoint

# # Delete the agent after the chat session
# project.agents.delete_agent(agent.id)
# print(f"Deleted agent, ID: {agent.id}")
# # Delete vector store
