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
besides, when the user describes relative positions, try to avoid collisions as much as possible, and you can increase the distance by 10% to avoid errors.
"""

@dataclass
class ChatMessage:
    role: str = ""
    content: str = ""
    has_model_content: bool = False
    tool: str = ""
    tool_parameters: Optional[Dict] = None
    model_data: Optional[Dict] = None


class BaseAIClient:
    """Base class for AI clients"""
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt
    
    def chat(self, message: str, conversation: List[ChatMessage]) -> str:
        raise NotImplementedError("Subclasses must implement chat method")


class ChatGPTClient(BaseAIClient):
    def __init__(self, system_prompt: str = None):
        super().__init__(system_prompt)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_API_MODEL", "gpt-4o-mini")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", 4000))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", 0.8))
        self.history_depth = int(os.getenv("OPENAI_HISTORY_DEPTH", 10))

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


class SiliconFlowClient(BaseAIClient):
    """SiliconFlow AI Client - compatible with OpenAI API interface"""
    def __init__(self, system_prompt: str = None):
        super().__init__(system_prompt)
        self.api_key = os.getenv("SILICONFLOW_API_KEY")
        self.base_url = os.getenv("SILICONFLOW_API_BASE_URL", "https://api.siliconflow.cn/v1")
        self.model = os.getenv("SILICONFLOW_API_MODEL", "Qwen/Qwen2.5-7B-Instruct")
        self.max_tokens = int(os.getenv("SILICONFLOW_MAX_TOKENS", 4000))
        self.temperature = float(os.getenv("SILICONFLOW_TEMPERATURE", 0.8))
        self.history_depth = int(os.getenv("SILICONFLOW_HISTORY_DEPTH", 10))

        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY environment variable is not set.")
        
        # SiliconFlow uses OpenAI-compatible API
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
            print(f"================= SiliconFlowClient Error =======")
            print(f"Message: \n{message} \nConversation: \n{conversation}")
            print(f"System Prompt: \n{self.system_prompt}")
            print(f"Error during chat: \n{e}")
            print(f"=================================================")
            raise e


def get_ai_client(system_prompt: str = None) -> BaseAIClient:
    """Factory function to get AI client based on environment variable AI_PLATFORM"""
    platform = os.getenv("AI_PLATFORM", "silicon").lower()
    
    if platform == "openai":
        print("🤖 Using OpenAI ChatGPT client")
        return ChatGPTClient(system_prompt)
    elif platform == "silicon":
        print("🤖 Using SiliconFlow client")
        return SiliconFlowClient(system_prompt)
    else:
        print(f"⚠️  Unknown AI platform '{platform}', defaulting to SiliconFlow")
        return SiliconFlowClient(system_prompt)        
import unittest
class TestAIClients(unittest.TestCase):
    def setUp(self):
        # Save original environment
        self.original_platform = os.getenv("AI_PLATFORM")
        
    def tearDown(self):        # Restore original environment
        if self.original_platform:
            os.environ["AI_PLATFORM"] = self.original_platform
        elif "AI_PLATFORM" in os.environ:
            del os.environ["AI_PLATFORM"]
    
    def test_get_ai_client_silicon_default(self):
        """Test that SiliconFlow is the default client"""
        if "AI_PLATFORM" in os.environ:
            del os.environ["AI_PLATFORM"]
        try:
            client = get_ai_client("Test system prompt")
            self.assertIsInstance(client, SiliconFlowClient)
        except ValueError as e:
            if "SILICONFLOW_API_KEY" in str(e):
                self.skipTest("SILICONFLOW_API_KEY not set")
            else:
                raise

    def test_get_ai_client_openai(self):
        """Test OpenAI client selection"""
        os.environ["AI_PLATFORM"] = "openai"
        try:
            client = get_ai_client("Test system prompt")
            self.assertIsInstance(client, ChatGPTClient)
        except ValueError as e:
            if "OPENAI_API_KEY" in str(e):
                self.skipTest("OPENAI_API_KEY not set")
            else:
                raise

    def test_get_ai_client_silicon(self):
        """Test SiliconFlow client selection"""
        os.environ["AI_PLATFORM"] = "silicon"
        try:
            client = get_ai_client("Test system prompt")
            self.assertIsInstance(client, SiliconFlowClient)
        except ValueError as e:
            if "SILICONFLOW_API_KEY" in str(e):
                self.skipTest("SILICONFLOW_API_KEY not set")
            else:
                raise

    def test_get_ai_client_unknown_platform(self):
        """Test unknown platform defaults to SiliconFlow"""
        os.environ["AI_PLATFORM"] = "unknown"
        try:
            client = get_ai_client("Test system prompt")
            self.assertIsInstance(client, SiliconFlowClient)
        except ValueError as e:
            if "SILICONFLOW_API_KEY" in str(e):
                self.skipTest("SILICONFLOW_API_KEY not set")
            else:
                raise

class TestChatGPTClient(unittest.TestCase):
    def setUp(self):
        try:
            self.client = ChatGPTClient(system_prompt="You are a test AI.")
        except ValueError:
            self.skipTest("OPENAI_API_KEY not set")

    def test_chat(self):
        response = self.client.chat("Hello, AI!", [])
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

    def test_system_prompt(self):
        client = ChatGPTClient(system_prompt="You are a test AI with a custom prompt.")
        self.assertEqual(client.system_prompt, "You are a test AI with a custom prompt.")

    def test_chat_with_history(self):
        conversation = [
            ChatMessage(role="user", content="Hello, AI!"),
            ChatMessage(role="assistant", content="Hello! How can I assist you today?")
        ]
        response = self.client.chat("What can you do?", conversation)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

class TestSiliconFlowClient(unittest.TestCase):
    def setUp(self):
        try:
            self.client = SiliconFlowClient(system_prompt="You are a test AI.")
        except ValueError:
            self.skipTest("SILICONFLOW_API_KEY not set")

    def test_system_prompt(self):
        client = SiliconFlowClient(system_prompt="You are a test AI with a custom prompt.")
        self.assertEqual(client.system_prompt, "You are a test AI with a custom prompt.")

    def test_chat_with_history(self):
        conversation = [
            ChatMessage(role="user", content="Hello, AI!"),
            ChatMessage(role="assistant", content="Hello! How can I assist you today?")
        ]
        response = self.client.chat("What can you do?", conversation)
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)

if __name__ == "__main__":
    unittest.main()