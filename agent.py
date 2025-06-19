from ai_client import ChatMessage, ChatMessagePrompt, get_ai_client
from if_tool import ToolIface
from if_model import Model, ModelOperation
from typing import List, Dict
from models import ModelCube, ModelCylinder, ModelHalfCylinder, ModelNACA4, get_coordinate_system_description
from operations import ModelRigidTransform
from backend_trimesh import BackendTrimesh as Backend
import re, os, json
import hashlib

def gen_tool():
    return [
        ModelCube(),
        ModelCylinder(),
        ModelHalfCylinder(),
        ModelNACA4(),
        ModelRigidTransform(),
    ]

class Agent:
    def __init__(self, tools: List[ToolIface]):
        self.tools = tools
        self.client = get_ai_client()
        self.history = []        # Build system prompt
        self.system_prompt = "You are an aircraft design expert who can use various tools to create and manipulate models. You can use the following tools to create models or perform operations:\n"
        for tool in self.tools:
            item = f'- {tool.name}: {tool.to_json()}\n'
            self.system_prompt += item
        
        # Add standardized coordinate system information
        coord_system_desc = get_coordinate_system_description()
        self.system_prompt += f"\n{coord_system_desc}\n"
        self.system_prompt += "You can also perform operations on models, such as combining them or transforming them. "
        self.system_prompt += "When creating models, always follow the standardized orientation constraints defined in each tool's description. "
        self.system_prompt += "Pay close attention to model orientations to ensure consistency across all created models."
        self.client.system_prompt = f'{self.system_prompt}\n{ChatMessagePrompt().get()}'

        self.models = []
        self.operations = []

    def input(self, user_input: str):
        # Create a chat message with the system prompt
        messages = user_input.strip()

        # Create cache filename based on user input hash
        cache_key = hashlib.md5(user_input.encode('utf-8')).hexdigest()
        cache_file = f'.cache_{cache_key}'

        if os.path.exists(cache_file):
            print(f"cache mathced: {cache_file}")
            with open(cache_file, 'r') as f:
                response = f.read()
        else:
            print(f"cache not found, sending request to AI client...")
            # Send the request to the AI client
            response = self.client.chat(messages, self.history)

            # cache response to cache file
            with open(cache_file, 'w') as f:
                f.write(response)
        # Parse the response to extract model operations
        return self.handle_chat_response(response)
    
    def parse_json(self, response: str):
        import json
        response = response.strip()

        # remove // comments
        response = re.sub(r'//.*?\n', '', response)
        # If the response contains ``` json....```, we need to extract the JSON part

        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response}")
            return None
        return data

    def handle_chat_response(self, response: str):
        # This method should parse the response from the AI client
        # and return a list of Model objects based on the operations specified.
        # For simplicity, we will assume the response is a JSON string containing model data.

        # If the response contains ``` json....```, we need to extract the JSON part
        json_regex = re.compile(r'```json\s*([\s\S]*?)```', re.IGNORECASE)

        # case 1: non json block
        if not json_regex.search(response):
            # If no JSON block is found, we assume the response is already in JSON format
            response = response.strip()
            data = self.parse_json(response)
        elif json_regex.search(response):
            count = len(json_regex.findall(response))

            if count == 1:
                print("Found a single JSON block in the response.")
                response = json_regex.search(response).group(1).strip()
                data = self.parse_json(response)
                data = [data] if isinstance(data, dict) else data
            else:
                print(f"Found {count} JSON blocks in the response, extracting the first one.")
                data = []
                for match in json_regex.finditer(response):
                    json_block = match.group(1).strip()
                    try:
                        d = self.parse_json(json_block)
                        #if json begin with array, we assume it's a list of models
                        if isinstance(d, list):
                            # Append each item in the list to the response
                            for item in d:
                                data.append(item)
                        else:
                            # Otherwise, append the single item
                            data.append(d)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON block: {e}")
                        print(f"Raw block: {json_block}")
        try:
            print(f"Parsed response: {data}")
            for item in data:
                # filter: Object is None, no attributes named `tool`
                if item is None or item.keys() == [] or 'tool' not in item:
                    print(f"Skipping item: {item}")
                    continue
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
    user_input = """
使用6个airfoil模拟机翼，airfoil沿着y轴方向堆叠。接近x轴的为机翼根部，远离x轴的为机翼尖部。各个airfoil需要调整自身参数以适应这种堆叠方式。
模型整体呈流线型，，即参数的变化呈现出一种平滑渐变的效果；此之间的后端不能大于间隙的二分之一，确保每个airfoil的前端与下一个airfoil的后端之间有合理的间隔。
"""
    models, ops = agent.input(user_input)
    print(f"Generated Models: {[model for model in models]}")
    print(f"Generated Operations: {[op for op in ops]}")
    backend = Backend("trimesh")
    transformed_models = backend.transform(models, ops)
    print(f"Transformed Models: {[model.to_json() for model in transformed_models]}")
    backend.render(transformed_models)
