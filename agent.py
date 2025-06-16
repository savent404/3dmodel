from ai_client import ChatMessage, ChatMessagePrompt, ChatGPTClient as Client
from if_tool import ToolIface
from if_model import Model, ModelOperation
from typing import List, Dict
from models import ModelCube

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

    def input(self, user_input: str) -> List[Model]:
        # Create a chat message with the system prompt
        messages = user_input.strip()

        # Send the request to the AI client
        response = self.client.chat(messages, self.history)

        # Parse the response to extract model operations
        model_operations = self.handle_chat_response(response)

        return model_operations

    def handle_chat_response(self, response: str) -> List[Model]:
        # This method should parse the response from the AI client
        # and return a list of Model objects based on the operations specified.
        # For simplicity, we will assume the response is a JSON string containing model data.
        import json

        models = []

        try:
            data = json.loads(response)
            for item in data:
                # find tool by name
                tool_name = item.get('tool')
                tool = next((t for t in self.tools if t.name == tool_name), None)
                if tool and item.get('has_model_content'):
                    # Create a model instance from the tool parameters
                    args = item.get('tool_parameters', {})
                    model = tool.call(**args)
                    models.append(model)
                else:
                    print(f"Tool '{tool_name}' not found or no model content in item: {item}")
            return models
        except json.JSONDecodeError as e:
            print(f"Raw Response: {response}")
            print(f"Parsed models: {models}")
            print(f"Error parsing response: {e}")
            return []

if __name__ == "__main__":
    # Example usage
    cube_tool = ModelCube(name="CubeTool")
    agent = Agent(tools=[cube_tool])
    user_input = "Create a cube with width 2.0, height 3.0, and depth 4.0."
    models = agent.input(user_input)
    print("Generated Models:")
    for model in models:
        print(model.to_json())
        print(model)
