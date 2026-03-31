"""
电商客服机器人核心逻辑
整合 LLM、意图识别、知识库等模块

文档维护说明：
- 本文档是系统核心，修改时请同步更新 TECHNICAL_DOCS.md 对应章节
- Prompt 工程优化请参考 README.md 最佳实践
- 日志记录功能详见 MAINTENANCE_GUIDE.md 日常维护清单
"""
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from core.llm import get_llm_client, LLMClient
from core.context import ContextManager, ConversationContext
from core.logger import ConversationLogger
from training.intent import IntentClassifier
from knowledge.faq import FAQManager, ProductDatabase


class ECommerceBot:
    """智能电商客服机器人"""
    
    # 系统提示词（Prompt Engineering 的核心）
    SYSTEM_PROMPT = """你是一个专业的电商客服助手，名叫{bot_name}。
你服务的店铺是：{shop_name}

你的职责：
1. 热情、专业地回答客户关于商品、订单、物流、售后等问题
2. 使用亲切友好的语气，适当使用 emoji 表情 😊
3. 对于不确定的问题，诚实告知并建议转人工客服
4. 遵守客服规范，不承诺无法兑现的服务

回复风格：
- 简洁明了，避免长篇大论
- 使用"亲"、"您"等敬语
- 重要信息用数字标注（如 1、2、3）
- 结尾可以加上温馨提示

工作时间：{working_hours}
客服电话：{customer_service_phone}
"""
    
    def __init__(self):
        print("🤖 正在初始化电商客服机器人...")
        
        # 加载配置
        from dotenv import load_dotenv
        load_dotenv()
        
        self.bot_name = os.getenv("BOT_NAME", "小智客服")
        self.shop_name = os.getenv("SHOP_NAME", "智能电商商城")
        self.working_hours = os.getenv("WORKING_HOURS", "9:00-22:00")
        self.customer_service_phone = os.getenv("CUSTOMER_SERVICE_PHONE", "400-123-4567")
        
        # 初始化各个模块
        self.llm_client = get_llm_client()
        self.context_manager = ContextManager()
        self.intent_classifier = IntentClassifier()
        self.faq_manager = FAQManager()
        self.product_db = ProductDatabase()
        self.logger = ConversationLogger()  # 新增：日志记录器
        
        # 训练意图识别模型（如果不存在）
        try:
            self.intent_classifier.load_model()
        except FileNotFoundError:
            print("⚠️  意图模型不存在，开始训练...")
            self.intent_classifier.train()
        
        # 构建系统提示词
        self.system_prompt = self.SYSTEM_PROMPT.format(
            bot_name=self.bot_name,
            shop_name=self.shop_name,
            working_hours=self.working_hours,
            customer_service_phone=self.customer_service_phone
        )
        
        print(f"✅ 机器人初始化完成！我是{self.bot_name}，很高兴为您服务~")
    
    def chat(self, user_input: str, session_id: str = "default") -> Dict:
        """
        处理用户对话
        
        Args:
            user_input: 用户输入的文本
            session_id: 会话 ID
            
        Returns:
            包含回复内容和其他信息的字典
        """
        start_time = datetime.now()
        
        # 获取或创建会话上下文
        context = self.context_manager.get_or_create_context(session_id)
        
        # 添加用户消息到上下文
        context.add_message("user", user_input)
        
        # 1. 意图识别
        intent, confidence, intent_cn = self.intent_classifier.predict(user_input)
        print(f"\n🎯 意图识别：{intent} ({intent_cn}) - 置信度：{confidence:.2%}")
        
        # 2. 根据意图选择回复策略
        if confidence < 0.5:
            # 置信度太低，直接使用 LLM
            response = self._use_llm_response(user_input, context)
            strategy = "llm_direct"
        elif intent == "human_service":
            # 转人工客服
            response = self._transfer_to_human(context)
            strategy = "human_transfer"
        elif intent == "greeting":
            # 打招呼
            response = self._handle_greeting(user_input)
            strategy = "greeting"
        elif intent == "goodbye":
            # 告别
            response = self._handle_goodbye(user_input)
            strategy = "goodbye"
        else:
            # 其他意图：先搜索 FAQ，再决定
            faq_results = self.faq_manager.search_faq(user_input, top_k=1)
            
            if faq_results and len(faq_results) > 0:
                best_match = faq_results[0]
                # 计算匹配度（简单版本）
                match_score = self._calculate_match_score(user_input, best_match["question"])
                
                if match_score > 0.6:
                    # FAQ 匹配度高，直接返回 FAQ 答案
                    response = best_match["answer"]
                    strategy = "faq_match"
                else:
                    # FAQ 匹配度低，使用 LLM
                    response = self._use_llm_response(user_input, context)
                    strategy = "llm_with_context"
            else:
                # 没有相关 FAQ，使用 LLM
                response = self._use_llm_response(user_input, context)
                strategy = "llm_with_context"
        
        # 3. 添加助手回复到上下文
        context.add_message("assistant", response)
        
        # 4. 保存上下文
        self.context_manager.save_contexts()
        
        # 5. 记录对话日志（使用新的日志模块）
        # 检测是否快速转人工
        is_quick_human_transfer = "人工客服" in result["response"] and len(context.messages) <= 4  # 2 轮对话（用户+助手各算一条）
        
        # 检测是否偏离主题（简单判断：没有商品、订单、物流等关键词）
        topic_keywords = ["商品", "订单", "物流", "发货", "退货", "价格", "质量", "购买", "付款", "快递"]
        is_off_topic = not any(keyword in user_input.lower() for keyword in topic_keywords)
        
        # 检测是否有负面情绪
        negative_emotion_keywords = ["生气", "愤怒", "失望", "投诉", "举报", "太差", "垃圾", "骗子"]
        has_negative_emotion = any(keyword in user_input.lower() for keyword in negative_emotion_keywords)
        
        self.logger.log(
            session_id=session_id,
            user_input=user_input,
            response=result["response"],
            intent=intent,
            confidence=confidence,
            strategy=strategy,
            feedback="normal",  # 初始为普通，用户可以在前端标记好坏
            turn_count=len(context.messages) // 2,  # 对话轮数
            is_off_topic=is_off_topic,
            has_negative_emotion=has_negative_emotion
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # 返回结果
        return {
            "response": response,
            "intent": intent,
            "intent_cn": intent_cn,
            "confidence": confidence,
            "strategy": strategy,
            "session_id": session_id,
            "processing_time": f"{processing_time:.2f}s"
        }
    
    def _use_llm_response(self, user_input: str, context: ConversationContext) -> str:
        """使用 LLM 生成回复"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            *context.get_messages_for_llm()
        ]
        
        response = self.llm_client.chat(messages)
        return response
    
    def _handle_greeting(self, user_input: str) -> str:
        """处理打招呼"""
        greetings = [
            f"您好！我是{self.bot_name}，很高兴为您服务~😊 请问有什么可以帮助您的？",
            "亲，您好呀！欢迎来到我们的店铺，有什么问题尽管问我哦~",
            "哈喽~ 我是您的专属客服小助手，想了解什么商品呢？"
        ]
        return greetings[hash(user_input) % len(greetings)]
    
    def _handle_goodbye(self, user_input: str) -> str:
        """处理告别"""
        goodbyes = [
            "好的呢，感谢您的咨询，祝您生活愉快！再见~ 👋",
            "不客气哒，有任何问题随时来找我哦！拜拜~",
            "应该的~ 期待您的再次光临，再见！😊"
        ]
        return goodbyes[hash(user_input) % len(goodbyes)]
    
    def _transfer_to_human(self, context: ConversationContext) -> str:
        """转人工客服"""
        return f"""好的，已为您转接人工客服~ 🤝

人工客服工作时间：{self.working_hours}
如需电话支持，请拨打：{self.customer_service_phone}

当前排队人数：3 人，预计等待时间：2-3 分钟
请稍候，人工客服马上就来为您服务~"""
    
    def _calculate_match_score(self, query: str, faq_question: str) -> float:
        """计算查询与 FAQ 问题的匹配度（简化版）"""
        query_words = set(query.lower())
        question_words = set(faq_question.lower())
        
        # Jaccard 相似度
        intersection = query_words & question_words
        union = query_words | question_words
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    

    
    def train_intent(self, text: str, correct_intent: str):
        """
        在线训练意图识别
        
        Args:
            text: 用户输入
            correct_intent: 正确的意图标签
        """
        print(f"🎯 收到训练样本：'{text}' -> {correct_intent}")
        self.intent_classifier.add_training_sample(text, correct_intent)
    
    def update_feedback(self, log_id: str, feedback: str) -> bool:
        """
        更新某条日志的评价
        
        Args:
            log_id: 日志 ID
            feedback: 评价 (good/bad/normal)
        """
        return self.logger.update_feedback(log_id, feedback)
    
    def get_statistics(self, date: Optional[str] = None) -> Dict:
        """
        获取统计信息
        
        Args:
            date: 日期 (YYYY-MM-DD)，None 表示所有时间
        """
        return self.logger.get_statistics(date)
    
    def analyze_bad_cases(self) -> Dict:
        """
        分析坏案例
        """
        return self.logger.analyze_bad_cases()
    
    def add_faq(self, question: str, answer: str, keywords: List[str], category: str = "其他"):
        """添加新的 FAQ"""
        faq_id = self.faq_manager.add_faq(question, answer, keywords, category)
        print(f"✅ FAQ #{faq_id} 已添加到知识库")
        return faq_id


# 需要导入 json
import json

# 使用示例
if __name__ == "__main__":
    bot = ECommerceBot()
    
    print("\n" + "="*60)
    print("🎮 开始与机器人对话（输入'quit'退出）")
    print("="*60)
    
    while True:
        user_input = input("\n👤 你：").strip()
        if user_input.lower() in ['quit', 'exit', '退出']:
            print("👋 再见！")
            break
        
        if not user_input:
            continue
        
        result = bot.chat(user_input, session_id="test_user")
        
        print(f"\n🤖 {bot.bot_name}: {result['response']}")
        print(f"   意图：{result['intent_cn']} ({result['confidence']:.2%})")
        print(f"   策略：{result['strategy']}")
        print(f"   耗时：{result['processing_time']}")
