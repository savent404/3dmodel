import os, json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import openai
from dotenv import load_dotenv

load_dotenv()

class ChatMessagePrompt:
    def get(self) -> str:
        return """
The results should be a list of ChatMessage objects, each containing the following fields:
1. tool_type: A string indicating the type of tool used in the message. It can be "model" for model-related messages or "operation" for operation-related messages.
2. tool: The name of the tool used in the message.
3. tool_parameters: A dictionary containing the parameters used for the tool, if applicable.
4. has_content: A boolean indicating whether the message contains tool related content or not.
The tool_parameters field should contain the necessary parameters for the tool, which is specific to the tool being used.
"""

@dataclass
class ChatMessage:
    has_model_content: bool = False
    tool: str = ""
    tool_parameters: Optional[Dict] = None

class ChatGPTClient:
    def __init__(self, system_prompt: str = None):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_API_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 1000))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
        self.history_depth = int(os.getenv("OPENAI_HISTORY_DEPTH", 10))
        self.system_prompt = system_prompt

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
    
    def chat(self, message: str, conversation: List[ChatMessage]) -> str:
        try:
            m = [{"role": "system", "content": self.system_prompt}]
            for msg in conversation[-self.history_depth:]:
                m.append({
                    "role": msg.role,
                    "content": msg.content,
                    "has_model_content": msg.has_model_content,
                    "model_data": json.dumps(msg.model_data) if msg.model_data else None
                })
            m.append({"role": "user", "content": message})
            rsp = self.client.chat.completions.create(
                model = self.model,
                messages = m,
                max_tokens = self.max_tokens,
                temperature = self.temperature,
            )
            return rsp.choices[0].message.content.strip()
        except Exception as e:
            print(f"================= ChatGPTClient Error ==========")
            print(f"Message: \n{message} \nConversation: \n{conversation}")
            print(f"System Prompt: \n{self.system_prompt}")
            print(f"Error during chat: \n{e}")
            print(f"=================================================")
            raise e
        
import unittest
class TestChatGPTClient(unittest.TestCase):
    def setUp(self):
        self.client = ChatGPTClient(system_prompt="You are a test AI.")

    def test_chat(self):
        response = self.client.chat("Hello, AI!", [])
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_invalid_api_key(self):
        os.environ["OPENAI_API_KEY"] = "invalid_key"
        ChatGPTClient()
    def test_system_prompt(self):
        client = ChatGPTClient(system_prompt="You are a test AI with a custom prompt.")
        self.assertEqual(client.system_prompt, "You are a test AI with a custom prompt.")
    def test_chat_with_system_prompt(self):
        client = ChatGPTClient(system_prompt="You are a test AI with a custom prompt.")
        response = client.chat("Hello, AI!", [])
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
    def test_chat_with_history(self):
        client = ChatGPTClient(system_prompt="You are a test AI with a custom prompt.")
        conversation = [
            ChatMessage(role="user", content="Hello, AI!"),
            ChatMessage(role="assistant", content="Hello! How can I assist you today?")
        ]
        response = client.chat("What can you do?", conversation)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
if __name__ == "__main__":
    unittest.main()