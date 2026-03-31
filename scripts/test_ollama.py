"""
Ollama 本地模型测试脚本
用于快速测试 Ollama 配置是否正确
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm import get_llm_client, OllamaClient

def test_ollama():
    """测试 Ollama 模型"""
    print("="*60)
    print("🦙 Ollama 本地模型测试")
    print("="*60)
    
    # 检查环境变量
    print("\n📋 检查配置：")
    print(f"   USE_OLLAMA: {os.getenv('USE_OLLAMA', 'false')}")
    print(f"   OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
    print(f"   OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'qwen:7b')}")
    
    # 获取 Ollama 客户端
    print("\n🔧 初始化 Ollama 客户端...")
    client = get_llm_client(use_ollama=True)
    
    if not isinstance(client, OllamaClient):
        print("❌ 客户端初始化失败！")
        return
    
    print("✅ 客户端初始化成功！")
    
    # 测试对话
    print("\n💬 开始测试对话...")
    print("-"*60)
    
    test_messages = [
        {"role": "system", "content": "你是一个友好的电商客服助手"},
        {"role": "user", "content": "你好，请问什么时候发货？"}
    ]
    
    print(f"👤 用户：{test_messages[1]['content']}")
    print(f"🤖 AI 回复：", end="", flush=True)
    
    try:
        response = client.chat(test_messages)
        print(response)
        print("\n✅ 测试成功！")
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        print("\n💡 可能的原因：")
        print("   1. Ollama 服务未运行，请执行：ollama serve")
        print("   2. 模型未下载，请执行：ollama pull <模型名>")
        print("   3. 模型名称配置错误，请检查 .env 中的 OLLAMA_MODEL")
    
    print("="*60)
    
    # 交互模式
    print("\n🎮 进入交互模式（输入 'quit' 退出）")
    print("-"*60)
    
    while True:
        user_input = input("\n👤 你：").strip()
        if user_input.lower() in ['quit', 'exit', '退出']:
            print("👋 再见！")
            break
        
        if not user_input:
            continue
        
        messages = [
            {"role": "system", "content": "你是一个友好的电商客服助手"},
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = client.chat(messages)
            print(f"🤖 AI: {response}")
        except Exception as e:
            print(f"❌ 错误：{e}")

if __name__ == "__main__":
    test_ollama()
