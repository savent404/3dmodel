from ai_client import ChatMessage, ChatMessagePrompt, ChatGPTClient as Client
from if_tool import ToolIface
from if_model import Model, ModelOperation
from typing import List, Dict
from models import ModelCube, ModelCylinder
from operations import ModelRigidTransform
from backend_matplot import BackendMatplot as Backend
import re

def gen_tool():
    return [
        ModelCube(),
        ModelCylinder(),
        ModelRigidTransform()
    ]

class Agent:
    def __init__(self, tools: List[ToolIface]):
        self.tools = tools
        self.client = Client()
        self.history = []

        # Build system prompt
        self.system_prompt = "You are an AI agent that can create 3D models using the following tools:\n"
        for tool in self.tools:
            item = f'- {tool.name}: {tool.to_json()}\n'
            self.system_prompt += item
        self.system_prompt += "You can also perform operations on models, such as combining them or transforming them."
        self.client.system_prompt = f'{self.system_prompt}\n{ChatMessagePrompt().get()}'

        self.models = []
        self.operations = []

    def input(self, user_input: str):
        # Create a chat message with the system prompt
        messages = user_input.strip()

        # Send the request to the AI client
        response = self.client.chat(messages, self.history)

        # Parse the response to extract model operations
        return self.handle_chat_response(response)

    def handle_chat_response(self, response: str):
        # This method should parse the response from the AI client
        # and return a list of Model objects based on the operations specified.
        # For simplicity, we will assume the response is a JSON string containing model data.
        import json

        # If the response contains ``` json....```, we need to extract the JSON part
        json_regex = re.compile(r'```json\s*([\s\S]*?)```', re.IGNORECASE)
        if json_regex.search(response):
            response = json_regex.search(response).group(1).strip()
        else:
            # If no JSON block is found, we assume the response is already in JSON format
            response = response.strip()

        try:
            data = json.loads(response)

            print(f"Parsed response: {data}")
            for item in data:
                # find tool by name
                tool_name = item.get('tool')
                tool = next((t for t in self.tools if t.name == tool_name), None)
                if tool and item.get('has_content'):
                    is_model = item.get('tool_type', '') == 'model'
                    is_operation = item.get('tool_type', '') == 'operation'
                    args = item.get('tool_parameters', {})

                    if is_model:
                        # Create a model instance from the item
                        model = tool.call(**args)
                        self.models.append(model)
                    elif is_operation:
                        # Create a model operation instance from the item
                        operation = tool.call(self.models, **args)
                        self.operations.append(operation)
                else:
                    print(f"Tool '{tool_name}' not found or no model content in item: {item}")
            return self.models, self.operations
        except json.JSONDecodeError as e:
            print(f"Raw Response: {response}")
            print(f"Parsed models: {self.models}")
            print(f"Parsed operations: {self.operations}")
            print(f"Error parsing response: {e}")
            return [], []

if __name__ == "__main__":
    agent = Agent(tools=gen_tool())
    user_input = "创建一个(1,1,1)大小的正方体，并在其旁边创建一个(x轴半径为1,y轴半径为2,高度为1)大小的圆柱体"
    models, ops = agent.input(user_input)
    print(f"Generated Models: {[model for model in models]}")
    print(f"Generated Operations: {[op for op in ops]}")
    backend = Backend("matplot")
    transformed_models = backend.transform(models, ops)
    print(f"Transformed Models: {[model.to_json() for model in transformed_models]}")
    backend.render(transformed_models)
