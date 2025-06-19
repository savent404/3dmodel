from ai_client import ChatMessage, ChatMessagePrompt, get_ai_client
from if_tool import ToolIface
from if_model import Model, ModelOperation
from typing import List, Dict, Optional
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
        self.conversation_history = []  # Store full conversation history
        self.history = []  # Current history for AI client        
        # Build system prompt
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
        self.backend = None
        self.persistent_models = {}  # Store all created models by name for multi-turn access

    def set_backend(self, backend: Backend):
        """Set the backend for rendering models."""
        self.backend = backend

    def create_conversation_cache_key(self) -> str:
        """Create a cache key based on the entire conversation history."""
        conversation_text = ""
        for entry in self.conversation_history:
            conversation_text += f"{entry['role']}: {entry['content']}\n"
        return hashlib.md5(conversation_text.encode('utf-8')).hexdigest()

    def add_to_conversation(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': len(self.conversation_history)
        })

    def build_chat_history(self) -> List[ChatMessage]:
        """Convert conversation history to ChatMessage objects for AI client."""
        chat_history = []
        # Skip the last entry since it's the current user input that we're about to process
        for entry in self.conversation_history[:-1]:  
            chat_msg = ChatMessage(
                role=entry['role'],
                content=entry['content'],
                has_model_content=entry['role'] == 'assistant'
            )
            chat_history.append(chat_msg)
        return chat_history

    def input(self, user_input: str, use_conversation_cache: bool = False):
        # Add user input to conversation history
        self.add_to_conversation("user", user_input)
        
        # Create cache filename based on conversation history or just current input
        if use_conversation_cache:
            cache_key = self.create_conversation_cache_key()
            cache_file = f'.cache_conversation_{cache_key}'
        else:
            cache_key = hashlib.md5(user_input.encode('utf-8')).hexdigest()
            cache_file = f'.cache_{cache_key}'

        # Create a chat message with the system prompt
        messages = user_input.strip()

        if os.path.exists(cache_file):
            print(f"cache matched: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                response = f.read()
        else:
            print(f"cache not found, sending request to AI client...")
            # Convert conversation history to ChatMessage objects for AI client
            chat_history = self.build_chat_history()
            # Send the request to the AI client with conversation history
            response = self.client.chat(messages, chat_history)

            # cache response to cache file
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(response)
        
        # Add AI response to conversation history
        self.add_to_conversation("assistant", response)

        # dump current response
        with open('.cache.current_response', 'w', encoding='utf-8') as f:
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
                        # Store in persistent models for multi-turn access
                        self.persistent_models[model.name] = model
                    elif is_operation:
                        # For operations, we need to provide all available models
                        all_available_models = list(self.persistent_models.values()) + self.models
                        operation = tool.call(all_available_models, **args)
                        self.operations.append(operation)
                        
                        # Apply operation effects to persistent models if needed
                        target_model_name = args.get('model', '')
                        if target_model_name in self.persistent_models:
                            # Update the persistent model with transformation results
                            target_model = self.persistent_models[target_model_name]
                            if operation.type == "transform_rigid":
                                # FIXME: Leave it to backend rendering
                                pass
                            # Add the updated model to current models for rendering
                            if target_model not in self.models:
                                self.models.append(target_model)
                else:
                    print(f"Tool '{tool_name}' not found or no model content in item: {item}")
            return self.models, self.operations
        except json.JSONDecodeError as e:
            print(f"Raw Response: {response}")
            print(f"Parsed models: {self.models}")
            print(f"Parsed operations: {self.operations}")
            print(f"Error parsing response: {e}")
            return [], []

    def reset_models(self):
        """Reset current models and operations for a new conversation turn, but keep persistent models."""
        self.models = []
        self.operations = []

    def clear_all_models(self):
        """Clear all models including persistent ones."""
        self.models = []
        self.operations = []
        self.persistent_models = {}

    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.conversation_history:
            return "No conversation history."
        
        summary = f"Conversation Summary ({len(self.conversation_history)} messages):\n"
        for i, entry in enumerate(self.conversation_history):
            role = entry['role']
            content = entry['content'][:100] + "..." if len(entry['content']) > 100 else entry['content']
            summary += f"{i+1}. {role.title()}: {content}\n"
        
        summary += f"\nPersistent Models: {list(self.persistent_models.keys())}\n"
        return summary

def run_cli():
    """Run the CLI frontend for multi-turn conversation with the AI model."""
    print("=== 3D Model Generation CLI ===")
    print("与AI模型进行多轮对话以修正和完善3D模型")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'history' 查看对话历史")
    print("输入 'clear' 清除当前模型并开始新的对话")
    print("=" * 40)
    
    # Initialize agent and backend
    agent = Agent(tools=gen_tool())
    backend = Backend("trimesh")
    agent.set_backend(backend)
    
    conversation_turn = 0
    
    while True:
        try:
            # Get user input
            user_input = input(f"\n[第{conversation_turn + 1}轮] 请输入您的需求: ").strip()
            
            if not user_input:
                continue
                
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("感谢使用！再见！")
                break
            elif user_input.lower() in ['history', '历史']:
                print("\n" + agent.get_conversation_summary())
                continue
            elif user_input.lower() in ['clear', '清除']:
                # Close current display and reset
                backend.close_display()
                agent.clear_all_models()
                agent.conversation_history = []
                agent.history = []
                conversation_turn = 0
                print("已清除当前模型和对话历史，开始新的对话。")
                continue
            
            # Close previous rendering before processing new request
            if conversation_turn > 0:
                print("关闭当前渲染...")
                backend.close_display()
            
            # Reset models for new turn (but keep persistent models)
            agent.reset_models()
            
            print(f"\n处理中...")
            print(f"发送给AI的历史对话长度: {len(agent.conversation_history)-1}")  # -1因为当前用户输入还没处理
            print(f"当前持久模型: {list(agent.persistent_models.keys())}")
            
            # Process user input with conversation history
            models, ops = agent.input(user_input, use_conversation_cache=True)
            
            print(f"\n=== AI 输出 ===")
            print(f"生成的模型数量: {len(models)}")
            print(f"生成的操作数量: {len(ops)}")
            
            if models:
                print("\n模型详情:")
                for i, model in enumerate(models):
                    print(f"  {i+1}. {model.name} ({model.type})")
            
            if ops:
                print("\n操作详情:")
                for i, op in enumerate(ops):
                    print(f"  {i+1}. {op.type} - 目标: {op.models}")
            
            # Transform and render models
            if models or ops:
                print("\n变换和渲染模型...")
                try:
                    transformed_models = backend.transform(models, ops)
                    render_result = backend.render(transformed_models)
                    print(f"渲染完成: {render_result}")
                except Exception as e:
                    print(f"渲染时发生错误: {e}")
            else:
                print("未生成任何模型或操作。")
            
            conversation_turn += 1
            print(f"\n第{conversation_turn}轮对话完成。您可以继续对话来修正或完善模型。")
            print(f"总对话历史长度: {len(agent.conversation_history)}")
            print(f"总持久模型数量: {len(agent.persistent_models)}")
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断。")
            break
        except Exception as e:
            print(f"\n发生错误: {e}")
            print("请重试或输入 'quit' 退出。")
    
    # Clean up
    try:
        backend.close_display()
    except:
        pass

if __name__ == "__main__":
    # Check if user wants to run CLI or original example
    import sys

    if len(sys.argv) == 1 or sys.argv[1] != 'test':
        run_cli()
    else:
        # Original example code
        agent = Agent(tools=gen_tool())
        user_input = """
使用6个airfoil模拟机翼，airfoil沿着y轴方向堆叠。接近x轴的为机翼根部，远离x轴的为机翼尖部。各个airfoil需要调整自身参数以适应这种堆叠方式。模型整体呈流线型，，即参数的变化呈现出一种平滑渐变的效果；此之间的后端不能大于间隙的二分之一，确保每个airfoil的前端与下一个airfoil的后端之间有合理的间隔。再使用2个圆柱体贯穿所有airfoil来支撑整体结构(直径0.1)
"""
        models, ops = agent.input(user_input)
        print(f"Generated Models: {[model for model in models]}")
        print(f"Generated Operations: {[op for op in ops]}")
        backend = Backend("trimesh")
        transformed_models = backend.transform(models, ops)
        print(f"Transformed Models: {[model.to_json() for model in transformed_models]}")
        backend.render(transformed_models)
