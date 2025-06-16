# 提供agent工具api，并按照API提供单项的系统提示，所有api公用同一套API参数
from if_model import Model

# 定义一个通用工具类
class ToolIface:
    def __init__(self, name: str, description: str, parameters: dict, tool_type: str = None):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.tool_type = tool_type if tool_type else "unknown"
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "tool_type": self.tool_type
        }
    
    def call(self, *args, **kwargs) -> Model:
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def to_json(self):
        import json
        return json.dumps(self.to_dict(), indent=2)

    def __str__(self):
        return f"ToolIface(name={self.name}, description={self.description}, parameters={self.parameters}, tool_type={self.tool_type})"