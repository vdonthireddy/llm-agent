  
import os  
import base64
from openai import AzureOpenAI  
from azure.identity import DefaultAzureCredential, get_bearer_token_provider  
import json

endpoint = os.getenv("ENDPOINT_URL")
deployment = os.getenv("DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

# Initialize Azure OpenAI client with key-based authentication
client = AzureOpenAI(
    azure_endpoint = endpoint,
    api_key = subscription_key,
    api_version = "2024-08-01-preview",
)  
    
# Include speech result if speech is enabled  
messages = [
    {
        "role": "system",
        "content": "You are an assistant to a marketing specialist."
    },
     {
        "role": "user",
        "content": "give me marketing best practices."
    }
] 

completion = client.chat.completions.create(  
    model=deployment,  
    messages=messages,
    max_tokens=800,  
    temperature=0.7,  
    top_p=0.95,  
    frequency_penalty=0,  
    presence_penalty=0,
    stop=None,  
    stream=False  
)  
  
data = json.loads(completion.to_json())  
print(data["choices"][0]["message"]["content"])
