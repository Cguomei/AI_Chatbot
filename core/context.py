"""
上下文管理模块
负责维护多轮对话的上下文信息
"""
from typing import List, Dict, Optional
from datetime import datetime
import json


class ConversationContext:
    """单个会话的上下文"""
    
    def __init__(self, session_id: str, max_history: int = 10):
        self.session_id = session_id
        self.max_history = max_history  # 最多保留多少轮对话
        self.messages: List[Dict] = []  # 对话历史
        self.user_info: Dict = {}  # 用户信息
        self.current_order: Optional[str] = None  # 当前处理的订单号
        self.intent_stack: List[str] = []  # 意图栈（用于多轮对话）
        self.created_at = datetime.now()
        self.last_active = datetime.now()
    
    def add_message(self, role: str, content: str):
        """添加一条消息到上下文"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 限制历史长度
        if len(self.messages) > self.max_history * 2:  # 用户和助手各算一条
            self.messages = self.messages[-self.max_history * 2:]
        
        self.last_active = datetime.now()
    
    def clear(self):
        """清空上下文"""
        self.messages = []
        self.intent_stack = []
        self.current_order = None
    
    def get_messages_for_llm(self) -> List[Dict]:
        """获取格式化后的消息列表（用于发送给 LLM）"""
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.messages
        ]
    
    def to_dict(self) -> Dict:
        """转换为字典（用于序列化）"""
        return {
            "session_id": self.session_id,
            "messages": self.messages,
            "user_info": self.user_info,
            "current_order": self.current_order,
            "intent_stack": self.intent_stack,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ConversationContext":
        """从字典加载"""
        ctx = cls(data["session_id"])
        ctx.messages = data.get("messages", [])
        ctx.user_info = data.get("user_info", {})
        ctx.current_order = data.get("current_order")
        ctx.intent_stack = data.get("intent_stack", [])
        ctx.created_at = datetime.fromisoformat(data["created_at"])
        ctx.last_active = datetime.fromisoformat(data["last_active"])
        return ctx


class ContextManager:
    """上下文管理器（管理多个会话）"""
    
    def __init__(self, storage_file: str = "data/contexts.json"):
        self.storage_file = storage_file
        self.contexts: Dict[str, ConversationContext] = {}
        self._load_contexts()
    
    def get_or_create_context(self, session_id: str) -> ConversationContext:
        """获取或创建会话上下文"""
        if session_id not in self.contexts:
            self.contexts[session_id] = ConversationContext(session_id)
            print(f"✨ 创建新会话：{session_id}")
        return self.contexts[session_id]
    
    def get_context(self, session_id: str) -> Optional[ConversationContext]:
        """获取会话上下文（不存在则返回 None）"""
        return self.contexts.get(session_id)
    
    def delete_context(self, session_id: str):
        """删除会话上下文"""
        if session_id in self.contexts:
            del self.contexts[session_id]
            print(f"🗑️  删除会话：{session_id}")
    
    def save_contexts(self):
        """保存所有上下文到文件"""
        data = {
            sid: ctx.to_dict() 
            for sid, ctx in self.contexts.items()
        }
        
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 已保存 {len(self.contexts)} 个会话上下文")
        except Exception as e:
            print(f"❌ 保存上下文失败：{e}")
    
    def _load_contexts(self):
        """从文件加载上下文"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.contexts = {
                    sid: ConversationContext.from_dict(ctx_data)
                    for sid, ctx_data in data.items()
                }
                print(f"📂 已加载 {len(self.contexts)} 个会话上下文")
        except Exception as e:
            print(f"⚠️  加载上下文失败：{e}")
            self.contexts = {}
    
    def cleanup_inactive(self, hours: int = 24):
        """清理不活跃的会话"""
        now = datetime.now()
        to_delete = []
        
        for sid, ctx in self.contexts.items():
            last_active = datetime.fromisoformat(ctx.last_active)
            if (now - last_active).total_seconds() > hours * 3600:
                to_delete.append(sid)
        
        for sid in to_delete:
            self.delete_context(sid)
        
        if to_delete:
            print(f"🧹 清理了 {len(to_delete)} 个不活跃会话")


# 导入需要的模块
import os

# 使用示例
if __name__ == "__main__":
    manager = ContextManager()
    
    # 创建会话
    ctx = manager.get_or_create_context("user_001")
    ctx.add_message("user", "你好，我想查一下订单")
    ctx.add_message("assistant", "好的，请提供您的订单号~")
    
    # 保存
    manager.save_contexts()
    
    # 再次加载
    ctx = manager.get_context("user_001")
    print(f"会话历史：{len(ctx.messages)} 条消息")
