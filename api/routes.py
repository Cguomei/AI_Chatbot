"""
API 路由模块
提供 HTTP 接口供前端或其他服务调用

文档维护说明：
- 本模块定义所有 REST API 接口
- 接口变更需同步更新 TECHNICAL_DOCS.md API 接口文档章节
- 新增/修改接口时请同时更新 README.md 使用指南
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid

router = APIRouter()

# 延迟导入 bot 实例（避免循环导入）
_bot_instance = None

def get_bot():
    """获取 bot 单例"""
    global _bot_instance
    if _bot_instance is None:
        from core.bot import ECommerceBot
        _bot_instance = ECommerceBot()
    return _bot_instance


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    intent: str
    intent_cn: str
    confidence: float
    strategy: str
    session_id: str
    processing_time: str


class TrainIntentRequest(BaseModel):
    """意图训练请求模型"""
    text: str
    correct_intent: str


class AddFAQRequest(BaseModel):
    """添加 FAQ 请求模型"""
    question: str
    answer: str
    keywords: List[str]
    category: Optional[str] = "其他"


class UpdateFeedbackRequest(BaseModel):
    """更新评价请求模型"""
    log_id: str
    feedback: str  # good, bad, normal


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口
    
    接收用户消息，返回 AI 回复
    """
    bot = get_bot()
    
    # 如果没有 session_id，生成一个新的
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        result = bot.chat(request.message, session_id=session_id)
        
        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            intent_cn=result["intent_cn"],
            confidence=result["confidence"],
            strategy=result["strategy"],
            session_id=session_id,
            processing_time=result["processing_time"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败：{str(e)}")


@router.post("/train/intent")
async def train_intent(request: TrainIntentRequest):
    """
    训练意图识别
    
    用于在线学习，纠正错误的意图识别
    """
    bot = get_bot()
    
    try:
        bot.train_intent(request.text, request.correct_intent)
        return {
            "status": "success",
            "message": f"已添加训练样本：'{request.text}' -> {request.correct_intent}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"训练失败：{str(e)}")


@router.post("/knowledge/faq")
async def add_faq(request: AddFAQRequest):
    """
    添加 FAQ 到知识库
    """
    bot = get_bot()
    
    try:
        faq_id = bot.add_faq(
            question=request.question,
            answer=request.answer,
            keywords=request.keywords,
            category=request.category
        )
        return {
            "status": "success",
            "faq_id": faq_id,
            "message": f"FAQ #{faq_id} 已添加"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加失败：{str(e)}")


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "service": "AI 电商客服"}


@router.get("/logs")
async def get_logs(feedback: Optional[str] = None, limit: int = 100):
    """
    获取对话日志
    
    Args:
        feedback: 筛选评价类型 (None=all, good, bad, normal)
        limit: 返回数量限制
    """
    bot = get_bot()
    logs = bot.logger.get_logs(feedback=feedback, limit=limit)
    return {"logs": logs, "count": len(logs)}


@router.post("/logs/feedback")
async def update_feedback(request: UpdateFeedbackRequest):
    """
    更新日志评价
    """
    bot = get_bot()
    
    success = bot.update_feedback(request.log_id, request.feedback)
    
    if success:
        return {
            "status": "success",
            "message": f"已更新评价为：{request.feedback}"
        }
    else:
        raise HTTPException(status_code=404, detail="日志记录不存在")


@router.get("/logs/statistics")
async def get_statistics(date: Optional[str] = None):
    """
    获取统计数据
    
    Args:
        date: 日期 (YYYY-MM-DD)，None 表示所有时间
    """
    bot = get_bot()
    stats = bot.get_statistics(date)
    return {"statistics": stats}


@router.get("/logs/bad-cases/analysis")
async def analyze_bad_cases():
    """
    坏案例分析
    """
    bot = get_bot()
    analysis = bot.analyze_bad_cases()
    return {"analysis": analysis}


@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用 AI 电商客服 API",
        "docs": "/docs",
        "endpoints": {
            "POST /api/chat": "聊天接口",
            "POST /api/train/intent": "训练意图识别",
            "POST /api/knowledge/faq": "添加 FAQ",
            "GET /api/logs": "获取对话日志",
            "POST /api/logs/feedback": "更新日志评价",
            "GET /api/logs/statistics": "获取统计数据",
            "GET /api/logs/bad-cases/analysis": "坏案例分析"
        }
    }
