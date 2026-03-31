"""
LLM 大模型调用模块
支持多种大模型 API 的统一调用接口
"""
import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
import requests

# 加载环境变量
load_dotenv()

class LLMClient:
    """大模型客户端基类"""
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """
        发送对话请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user/system", "content": "..."}]
            **kwargs: 其他参数
            
        Returns:
            模型回复的文本
        """
        raise NotImplementedError
    
    def _prepare_headers(self) -> Dict:
        """准备请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }


class DeepSeekClient(LLMClient):
    """DeepSeek 大模型客户端"""
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "stream": False
        }
        
        try:
            response = requests.post(
                url,
                headers=self._prepare_headers(),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            return f"API 调用失败：{str(e)}"
        except (KeyError, IndexError) as e:
            return f"解析响应失败：{str(e)}"


class OllamaClient(LLMClient):
    """Ollama 本地大模型客户端"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen:7b")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """
        使用 Ollama API 进行对话
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数
            
        Returns:
            模型回复的文本
        """
        url = f"{self.base_url}/api/chat"
        
        # 转换消息格式为 Ollama 格式
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature)
            }
        }
        
        try:
            print(f"🤖 正在调用 Ollama 模型：{self.model}")
            response = requests.post(
                url,
                json=payload,
                timeout=60  # 本地模型可能需要更长时间
            )
            response.raise_for_status()
            result = response.json()
            
            # Ollama 返回格式：{"message": {"role": "assistant", "content": "..."}, ...}
            return result["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama API 调用失败：{str(e)}"
            print(f"❌ {error_msg}")
            print("💡 请检查：1) Ollama 服务是否运行 2) 模型名称是否正确 3) 模型是否已下载")
            return error_msg
        except (KeyError, IndexError) as e:
            error_msg = f"解析 Ollama 响应失败：{str(e)}"
            print(f"❌ {error_msg}")
            return error_msg


class MockLLMClient(LLMClient):
    """
    模拟大模型客户端（用于测试，无需 API Key）
    实际使用时请替换为真实的 API 调用
    """
    
    def __init__(self):
        super().__init__()
        self.responses = {
            "你好": "您好！我是小智客服，很高兴为您服务。请问有什么可以帮助您的？",
            "发货时间": "我们一般在下单后 24 小时内发货，具体以实际发货时间为准哦~",
            "物流查询": "亲，您可以在'我的订单'页面查看物流信息，也可以告诉我订单号，我帮您查询~",
            "退换货": "我们支持 7 天无理由退换货，商品需保持完好未使用状态。请问您遇到什么问题了呢？",
            "默认": "感谢您的咨询，这个问题我需要更多信息才能准确回答您。能详细说说具体情况吗？"
        }
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        # 获取最后一条用户消息
        last_message = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_message = msg["content"].lower()
                break
        
        # 简单关键词匹配
        for key, value in self.responses.items():
            if key in last_message:
                return value
        
        return self.responses["默认"]


def get_llm_client(use_mock: bool = False, use_ollama: bool = None) -> LLMClient:
    """
    获取 LLM 客户端实例
    
    Args:
        use_mock: 是否使用模拟客户端（测试用）
        use_ollama: 是否使用 Ollama 本地模型（None 表示从环境变量读取）
        
    Returns:
        LLMClient 实例
    """
    # 优先检查 use_ollama 参数，其次检查环境变量
    if use_ollama is None:
        use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    
    if use_ollama:
        print("🦙 使用 Ollama 本地模型")
        print(f"📍 服务地址：{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
        print(f"📦 模型名称：{os.getenv('OLLAMA_MODEL', 'qwen:7b')}")
        return OllamaClient()
    elif use_mock or not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️  使用模拟 LLM 客户端（无 API Key）")
        print("💡 提示：请在.env 文件中配置 DEEPSEEK_API_KEY 以使用真实 AI")
        return MockLLMClient()
    else:
        print("✅ 使用 DeepSeek 大模型")
        return DeepSeekClient()


# 使用示例
if __name__ == "__main__":
    # 测试
    client = get_llm_client(use_mock=True)
    
    messages = [
        {"role": "system", "content": "你是一个电商客服助手"},
        {"role": "user", "content": "你好，我想问一下什么时候发货？"}
    ]
    
    response = client.chat(messages)
    print(f"AI 回复：{response}")
