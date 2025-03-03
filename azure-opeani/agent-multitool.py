import os
import json
from openai import AzureOpenAI
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import math
import inspect

# Initialize the Azure OpenAI client
endpoint = os.getenv("ENDPOINT_URL")
deployment_name = os.getenv("DEPLOYMENT_NAME")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
client = AzureOpenAI(
    azure_endpoint = endpoint,
    api_key = subscription_key,
    api_version = "2024-08-01-preview",
)  

# Simplified weather data
WEATHER_DATA = {
    "tokyo": {"temperature": "10", "unit": "celsius"},
    "san francisco": {"temperature": "72", "unit": "fahrenheit"},
    "paris": {"temperature": "22", "unit": "celsius"}
}

# Simplified timezone data
TIMEZONE_DATA = {
    "tokyo": "Asia/Tokyo",
    "san francisco": "America/Los_Angeles",
    "paris": "Europe/Paris"
}

def check_args(function, args):
    print('check_args called')
    print('inspect.signature(function)', inspect.signature(function))
    sig = inspect.signature(function)
    print("sig", sig)
    params = sig.parameters
    print("params", params)

    # Check if there are extra arguments
    for name in args:
        if name not in params:
            return False
    # Check if the required arguments are provided
    for name, param in params.items():
        if param.default is param.empty and name not in args:
            return False

    return True

def get_current_weather(location, unit=None):
    """Get the current weather for a given location"""
    print(f"get_current_weather called with location: {location}, unit: {unit}")  
    
    location_lower = location.lower()
    for key in WEATHER_DATA:
        if key in location_lower:
            print(f"Weather data found for {key}")  
            weather = WEATHER_DATA[key]
            return json.dumps({
                "location": location,
                "temperature": weather["temperature"],
                "unit": unit if unit else weather["unit"]
            })
    
    print(f"No weather data found for {location_lower}")  
    return json.dumps({"location": location, "temperature": "unknown"})

def get_current_time(location):
    """Get the current time for a given location"""
    print(f"get_current_time called with location: {location}")  
    location_lower = location.lower()
    
    for key, timezone in TIMEZONE_DATA.items():
        if key in location_lower:
            print(f"Timezone found for {key}")  
            current_time = datetime.now(ZoneInfo(timezone)).strftime("%I:%M %p")
            return json.dumps({
                "location": location,
                "current_time": current_time
            })
    
    print(f"No timezone data found for {location_lower}")  
    return json.dumps({"location": location, "current_time": "unknown"})

def calculator(num1, num2, operator):
    """A simple calculator used to perform basic arithmetic operations"""
    print(f"calculator called with num1: {num1}, num2: {num2}, operator: {operator}")  
    output = ""
    if operator == "+":
        output = str(num1 + num2)
    elif operator == "-":
        output = str(num1 - num2)
    elif operator == "*":
        output = str(num1 * num2)
    elif operator == "/":
        output = str(num1 / num2)
    elif operator == "**":
        output = str(num1**num2)
    elif operator == "sqrt":
        output = str(math.sqrt(num1))
    else:
        output = "Invalid operator"
    return output

available_functions = {
    "get_current_weather": get_current_weather,
    "get_current_time": get_current_time,
    "calculator": calculator,
}

def run_conversation(messages):
    # Define the functions for the model
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name, e.g. San Francisco",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current time in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name, e.g. San Francisco",
                        },
                    },
                    "required": ["location"],
                },
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "A simple calculator used to perform basic arithmetic operations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {"type": "number"},
                        "num2": {"type": "number"},
                        "operator": {
                            "type": "string",
                            "enum": ["+", "-", "*", "/", "**", "sqrt"],
                        },
                    },
                    "required": ["num1", "num2", "operator"],
                },
            },
        },
    ]

    # First API call: Ask the model to use the functions
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    # Process the model's response
    response_message = response.choices[0].message
    messages.append(response_message)

    print("Model's response:")  
    print(response_message)  

    # Handle function calls
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"Function call: {function_name}")  
            print(f"Function arguments: {function_args}")  

            if check_args(available_functions[function_name], function_args) is False:
                return "Invalid number of arguments for function: " + function_name
            
            if function_name == "get_current_weather":
                function_response = get_current_weather(
                    location=function_args.get("location"),
                    unit=function_args.get("unit")
                )
            elif function_name == "get_current_time":
                function_response = get_current_time(
                    location=function_args.get("location")
                )
            elif function_name == "calculator":
                function_response = calculator(
                    num1=function_args.get("num1"),
                    num2=function_args.get("num2"),
                    operator=function_args.get("operator")
                )
            else:
                function_response = json.dumps({"error": "Unknown function"})
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            })
    else:
        print("No tool calls were made by the model.")  

    # Second API call: Get the final response from the model
    final_response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
    )

    return final_response.choices[0].message.content

# Initial user message
messages = [{"role": "user", "content": "What's the weather and current time in San Francisco, Tokyo, and Paris? What's the difference between 7 and 4, 2 multiplied by 3, sqrt of 144 and finally add all of them?"}]

print(run_conversation(messages=messages))

# messages = [{"role": "user", "content": "What's the weather in San Francisco, Tokyo, and Tokyo? What is the difference between those two temparatures. please use calculator function to calculate the difference."}]
# messages = [{"role": "user", "content": "What's the difference between 7 and 4, 2 multiplied by 3, sqrt of 144 and finally add all of them?"}]
# messages = [{"role": "user", "content": "What's the difference in weather in F between San Francisco, and Tokyo? Use calculator tool"}]
# messages = [{"role": "user", "content": "what's the time in Tokyo?"}]
# Run the conversation and print the result