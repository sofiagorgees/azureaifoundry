import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

endpoint = "https://oldworldai.cognitiveservices.azure.com/"
model_name = "gpt-4"
deployment = "gpt-4"

subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key
)

conversation=[{"role": "system", "content": "You will model the disinterested value seeker from the OWI segmentation study. Answer questions and provide insightful responses as a disinterested value seeker would reply."}]
print('Hello, I am the segmentation model agent using gpt 4!\n If you want to end the chat at anytime type exit, quit, or q')

while True:
    user_input = input("You: ")      
    if user_input.lower() in ["exit", "quit", "q"]:
        print("Ending chat session.")    
        break
    conversation.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="gpt-4", # model = "deployment_name".
        messages=conversation
    )

    conversation.append({"role": "assistant", "content": response.choices[0].message.content})
    print("\n" + response.choices[0].message.content + "\n")