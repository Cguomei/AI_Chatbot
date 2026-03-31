"""
日志记录与分析模块
负责记录对话、评估质量、导出坏案例

文档维护说明：
- 本模块是数据分析的核心，修改时请同步更新 MAINTENANCE_GUIDE.md
- 日志文件格式变化需更新 TECHNICAL_DOCS.md 数据模型章节
- 统计功能优化请参考 README.md 关键指标说明
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path


class ConversationLogger:
    """对话日志记录器"""
    
    def __init__(self, log_dir: str = "data/logs"):
        self.log_dir = log_dir
        self.logs_file = os.path.join(log_dir, "all_conversations.json")
        self.bad_cases_file = os.path.join(log_dir, "bad_cases.json")
        self.good_cases_file = os.path.join(log_dir, "good_cases.json")
        
        # 确保目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        print(f"📝 日志目录：{log_dir}")
    
    def log(self, session_id: str, user_input: str, response: str, 
            intent: str, confidence: float, strategy: str, 
            feedback: str = "normal", 
            turn_count: int = 1,
            is_off_topic: bool = False,
            has_negative_emotion: bool = False):
        """
        记录一条对话
        
        Args:
            session_id: 会话 ID
            user_input: 用户输入
            response: AI 回复
            intent: 识别的意图
            confidence: 置信度
            strategy: 使用的策略
            feedback: 用户评价 (good/bad/normal)
            turn_count: 对话轮数（几轮后转人工）
            is_off_topic: 是否偏离主题（闲聊而非商品相关）
            has_negative_emotion: 是否有负面情绪（生气等）
        """
        log_entry = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "user_input": user_input,
            "response": response,
            "intent": intent,
            "confidence": confidence,
            "strategy": strategy,
            "feedback": feedback,
            "turn_count": turn_count,
            "is_off_topic": is_off_topic,
            "has_negative_emotion": has_negative_emotion,
            "created_at": datetime.now().isoformat()
        }
        
        # 保存到总日志
        self._append_to_file(self.logs_file, log_entry)
        
        # 根据评价和标记分类保存
        if feedback == "good":
            self._append_to_file(self.good_cases_file, log_entry)
        elif feedback == "bad" or is_off_topic or has_negative_emotion or (turn_count <= 2 and "human" in response.lower()):
            # 坏案例包括：
            # 1. 用户标记为差
            # 2. 偏离主题闲聊
            # 3. 有负面情绪
            # 4. 很快转人工（<=2 轮）
            self._append_to_file(self.bad_cases_file, log_entry)
        
        return log_entry
    
    def _append_to_file(self, filepath: str, data: Dict):
        """追加数据到 JSON 文件"""
        logs = []
        
        # 读取现有数据
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
        
        # 追加新数据
        logs.append(data)
        
        # 保存（限制文件大小，只保留最近 1000 条）
        logs = logs[-1000:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def get_logs(self, feedback: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        获取日志
        
        Args:
            feedback: 筛选评价类型 (None=all, good, bad, normal)
            limit: 返回数量限制
            
        Returns:
            日志列表
        """
        if feedback is None:
            filepath = self.logs_file
        elif feedback == "good":
            filepath = self.good_cases_file
        elif feedback == "bad":
            filepath = self.bad_cases_file
        else:
            filepath = self.logs_file
        
        if not os.path.exists(filepath):
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # 按时间倒序排序
            logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return logs[:limit]
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def get_statistics(self, date: Optional[str] = None) -> Dict:
        """
        获取统计信息
        
        Args:
            date: 日期 (YYYY-MM-DD)，None 表示今天
            
        Returns:
            统计数据字典
        """
        logs = self.get_logs()
        
        if not logs:
            return {
                "total": 0,
                "good": 0,
                "bad": 0,
                "normal": 0,
                "accuracy": 0.0,
                "avg_confidence": 0.0
            }
        
        # 如果指定了日期，过滤当天的日志
        if date:
            logs = [
                log for log in logs 
                if log.get("timestamp", "").startswith(date)
            ]
        
        total = len(logs)
        good = sum(1 for log in logs if log.get("feedback") == "good")
        bad = sum(1 for log in logs if log.get("feedback") == "bad")
        normal = sum(1 for log in logs if log.get("feedback") == "normal")
        
        # 计算平均置信度
        confidences = [log.get("confidence", 0) for log in logs]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # 计算准确率（好评率）
        accuracy = (good / total * 100) if total > 0 else 0
        
        return {
            "total": total,
            "good": good,
            "bad": bad,
            "normal": normal,
            "accuracy": round(accuracy, 2),
            "avg_confidence": round(avg_confidence, 4),
            "date": date or "all"
        }
    
    def update_feedback(self, log_id: str, feedback: str) -> bool:
        """
        更新某条日志的评价
        
        Args:
            log_id: 日志 ID
            feedback: 新的评价 (good/bad/normal)
            
        Returns:
            是否成功
        """
        logs = self.get_logs()
        
        for log in logs:
            if log.get("id") == log_id:
                old_feedback = log.get("feedback")
                log["feedback"] = feedback
                
                # 更新主日志文件
                self._save_logs(logs)
                
                # 如果在不同评价文件间移动，需要重新整理
                if old_feedback != feedback:
                    self._reorganize_files()
                
                return True
        
        return False
    
    def _save_logs(self, logs: List[Dict]):
        """保存日志列表"""
        with open(self.logs_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    def _reorganize_files(self):
        """重新整理评价文件"""
        logs = self.get_logs()
        
        # 清空并重建 good 和 bad 文件
        good_logs = [log for log in logs if log.get("feedback") == "good"]
        bad_logs = [log for log in logs if log.get("feedback") == "bad"]
        
        with open(self.good_cases_file, 'w', encoding='utf-8') as f:
            json.dump(good_logs, f, ensure_ascii=False, indent=2)
        
        with open(self.bad_cases_file, 'w', encoding='utf-8') as f:
            json.dump(bad_logs, f, ensure_ascii=False, indent=2)
    
    def export_logs(self, output_file: str, feedback: Optional[str] = None):
        """
        导出日志到文件
        
        Args:
            output_file: 输出文件路径
            feedback: 筛选评价类型
        """
        logs = self.get_logs(feedback)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已导出 {len(logs)} 条日志到：{output_file}")
    
    def analyze_bad_cases(self) -> Dict:
        """分析坏案例"""
        bad_logs = self.get_logs("bad")
        
        if not bad_logs:
            return {
                "count": 0,
                "common_intents": [],
                "low_confidence_count": 0,
                "quick_human_transfer_count": 0,
                "off_topic_count": 0,
                "negative_emotion_count": 0,
                "suggestions": []
            }
        
        # 统计常见意图
        intents = {}
        low_confidence = 0
        quick_human_transfer = 0  # 快速转人工
        off_topic = 0  # 偏离主题
        negative_emotion = 0  # 负面情绪
        
        for log in bad_logs:
            intent = log.get("intent", "unknown")
            intents[intent] = intents.get(intent, 0) + 1
            
            if log.get("confidence", 0) < 0.6:
                low_confidence += 1
            
            # 检查是否快速转人工（<=2 轮）
            if log.get("turn_count", 999) <= 2:
                quick_human_transfer += 1
            
            # 检查是否偏离主题
            if log.get("is_off_topic", False):
                off_topic += 1
            
            # 检查是否有负面情绪
            if log.get("has_negative_emotion", False):
                negative_emotion += 1
        
        # 按频率排序意图
        sorted_intents = sorted(intents.items(), key=lambda x: x[1], reverse=True)
        
        # 生成建议
        suggestions = []
        if sorted_intents:
            top_intent = sorted_intents[0][0]
            suggestions.append(f"最多的坏案例意图是 '{top_intent}'，建议加强该意图的训练")
        
        if low_confidence > len(bad_logs) * 0.5:
            suggestions.append("超过 50% 的坏案例置信度较低，建议优化意图识别模型")
        
        if quick_human_transfer > len(bad_logs) * 0.3:
            suggestions.append(f"{quick_human_transfer} 个案例在 2 轮内就转人工，建议提升 AI 解决复杂问题的能力")
        
        if off_topic > len(bad_logs) * 0.2:
            suggestions.append(f"{off_topic} 个案例偏离主题闲聊，建议加强话题引导和边界控制")
        
        if negative_emotion > 0:
            suggestions.append(f"{negative_emotion} 个案例出现负面情绪，需要紧急复盘和优化沟通话术")
        
        return {
            "count": len(bad_logs),
            "common_intents": [{"intent": k, "count": v} for k, v in sorted_intents[:5]],
            "low_confidence_count": low_confidence,
            "percentage": round(low_confidence / len(bad_logs) * 100, 2) if bad_logs else 0,
            "quick_human_transfer_count": quick_human_transfer,
            "quick_human_transfer_percentage": round(quick_human_transfer / len(bad_logs) * 100, 2) if bad_logs else 0,
            "off_topic_count": off_topic,
            "off_topic_percentage": round(off_topic / len(bad_logs) * 100, 2) if bad_logs else 0,
            "negative_emotion_count": negative_emotion,
            "negative_emotion_percentage": round(negative_emotion / len(bad_logs) * 100, 2) if bad_logs else 0,
            "suggestions": suggestions
        }
    
    def clear_all_logs(self):
        """清空所有日志"""
        for filepath in [self.logs_file, self.good_cases_file, self.bad_cases_file]:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🗑️  已删除：{filepath}")
        
        print("✅ 所有日志已清空")


# 使用示例
if __name__ == "__main__":
    logger = ConversationLogger()
    
    # 测试记录
    logger.log(
        session_id="test_001",
        user_input="什么时候发货？",
        response="我们一般在下单后 24 小时内发货~",
        intent="物流查询",
        confidence=0.95,
        strategy="faq_match",
        feedback="good"
    )
    
    # 获取统计
    stats = logger.get_statistics()
    print(f"\n📊 统计数据：{stats}")
    
    # 分析坏案例
    analysis = logger.analyze_bad_cases()
    print(f"\n⚠️  坏案例分析：{analysis}")
