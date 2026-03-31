# 📖 AI 智能电商客服系统 - 技术文档

## 项目概述

### 项目名称
AI 智能电商客服系统（教学版）

### 项目定位
面向 AI 训练师学习实践的电商客服对话系统，提供完整的对话管理、知识库构建、意图识别、日志分析等功能。

### 技术栈
- **后端框架**: Python 3.11 + FastAPI 0.109.0
- **AI 模型**: DeepSeek / GPT-3.5 / 通义千问（可切换）
- **数据库**: JSON 文件存储（轻量级，无需配置）
- **前端界面**: 原生 HTML + JavaScript
- **机器学习**: scikit-learn 1.4.0（意图识别）
- **部署方式**: 本地运行 / Uvicorn 服务器

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────┐
│              Web 管理后台 (static/admin.html)           │
│  - 对话测试 | 日志管理 | 知识库 | 坏案例复盘          │
└──────────────┬────────────────────────────────────┘
               │ HTTP/REST API
┌──────────────▼────────────────────────────────────┐
│            FastAPI 应用层 (api/routes.py)          │
│  - /api/chat         聊天接口                     │
│  - /api/logs/*       日志管理接口                 │
│  - /api/knowledge/*  知识库接口                   │
└──────────────┬────────────────────────────────────┘
               │
┌──────────────▼────────────────────────────────────┐
│             核心业务层 (core/*.py)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ bot.py   │ │ logger.py│ │context.py│          │
│  │机器人逻辑│ │日志记录  │ │上下文管理│          │
│  └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐                                     │
│  │ llm.py   │                                     │
│  │大模型调用│                                     │
│  └──────────┘                                     │
└──────────────┬────────────────────────────────────┘
               │
┌──────────────▼────────────────────────────────────┐
│             功能模块层                             │
│  ┌──────────┐ ┌──────────┐                        │
│  │intent.py │ │ faq.py   │                        │
│  │意图识别  │ │知识库管理│                        │
│  └──────────┘ └──────────┘                        │
└──────────────┬────────────────────────────────────┘
               │
┌──────────────▼────────────────────────────────────┐
│             数据存储层 (data/*.json)               │
│  - logs/        对话日志目录                      │
│  - contexts.json  会话上下文                      │
│  - faq.json       FAQ 知识库                       │
│  - products.json  商品信息                        │
└───────────────────────────────────────────────────┘
```

---

## 核心模块详解

### 1. ECommerceBot (`core/bot.py`)

**职责**: 机器人主控制器，整合各个模块

**核心方法**:
```python
class ECommerceBot:
    def __init__(self):
        """初始化所有模块"""
        self.llm_client = get_llm_client()      # LLM 调用
        self.context_manager = ContextManager()  # 上下文管理
        self.intent_classifier = IntentClassifier()  # 意图识别
        self.faq_manager = FAQManager()         # FAQ 管理
        self.product_db = ProductDatabase()     # 商品数据库
        self.logger = ConversationLogger()      # 日志记录器
    
    def chat(self, user_input: str, session_id: str) -> Dict:
        """
        处理用户对话的核心流程
        
        执行步骤:
        1. 获取/创建会话上下文
        2. 意图识别（优先级最高）
        3. 根据意图选择回复策略:
           - 置信度 < 0.5: 直接使用 LLM
           - human_service: 转人工客服
           - greeting/goodbye: 固定回复
           - 其他: 先搜索 FAQ，匹配度高则返回，否则使用 LLM
        4. 添加回复到上下文
        5. 记录对话日志
        6. 返回结果（包含意图、策略、耗时等）
        
        Returns:
            {
                "response": str,        # AI 回复
                "intent": str,          # 识别的意图
                "intent_cn": str,       # 意图中文名
                "confidence": float,    # 置信度
                "strategy": str,        # 使用的策略
                "session_id": str,      # 会话 ID
                "processing_time": str  # 处理耗时
            }
        """
    
    def train_intent(self, text: str, correct_intent: str):
        """在线训练意图识别"""
    
    def update_feedback(self, log_id: str, feedback: str) -> bool:
        """更新日志评价"""
    
    def get_statistics(self, date: Optional[str]) -> Dict:
        """获取统计数据"""
    
    def analyze_bad_cases(self) -> Dict:
        """分析坏案例"""
```

**对话流程图**:
```
用户输入 → 意图识别 → 判断置信度
                    ├─ < 0.5 → LLM 直接生成
                    ├─ human_service → 转人工
                    ├─ greeting → 固定回复
                    ├─ goodbye → 固定回复
                    └─ 其他 → FAQ 检索
                              ├─ 匹配度高 → FAQ 答案
                              └─ 匹配度低 → LLM 生成
                                        ↓
                                    记录日志 → 返回结果
```

---

### 2. ConversationLogger (`core/logger.py`)

**职责**: 对话日志记录与分析

**数据结构**:
```python
log_entry = {
    "id": "20260331163045123456",      # 时间戳 ID
    "timestamp": "2026-03-31T16:30:45.123456",
    "session_id": "user_001",
    "user_input": "什么时候发货？",
    "response": "我们一般在下单后 24 小时内发货...",
    "intent": "shipping",
    "confidence": 0.95,
    "strategy": "faq_match",
    "feedback": "normal"  # good/bad/normal
}
```

**核心方法**:
```python
class ConversationLogger:
    def log(self, session_id, user_input, response, intent, confidence, strategy, feedback="normal"):
        """记录一条对话"""
    
    def get_logs(self, feedback=None, limit=100) -> List[Dict]:
        """获取日志（支持筛选）"""
    
    def update_feedback(self, log_id, feedback) -> bool:
        """更新某条日志的评价"""
    
    def get_statistics(self, date=None) -> Dict:
        """获取统计数据"""
    
    def analyze_bad_cases(self) -> Dict:
        """分析坏案例（返回常见意图、低置信度比例等）"""
    
    def export_logs(self, output_file, feedback=None):
        """导出日志到文件"""
```

**日志文件组织**:
```
data/logs/
├── all_conversations.json    # 所有对话（最多 1000 条）
├── good_cases.json          # 好评案例
└── bad_cases.json           # 差评案例
```

**统计指标计算**:
```python
总对话数 = len(logs)
好评数 = sum(1 for log in logs if log.feedback == "good")
差评数 = sum(1 for log in logs if log.feedback == "bad")
准确率 = (好评数 / 总对话数) × 100%
平均置信度 = sum(log.confidence) / len(logs)
```

---

### 3. IntentClassifier (`training/intent.py`)

**职责**: 用户意图识别（基于机器学习）

**预定义意图类型**:
```python
INTENT_TYPES = {
    "greeting": "打招呼",
    "shipping": "物流查询",
    "order_status": "订单状态",
    "return_refund": "退换货",
    "product_info": "商品信息",
    "payment": "支付问题",
    "invoice": "发票问题",
    "complaint": "投诉建议",
    "human_service": "转人工客服",
    "goodbye": "告别"
}
```

**训练数据示例**:
```python
"greeting": [
    "你好", "您好", "在吗", "有人吗", "hi", "hello"
],
"shipping": [
    "什么时候发货", "发货了吗", "物流信息", "快递到哪了"
]
```

**算法流程**:
```python
1. TF-IDF 向量化
   - ngram_range=(1, 2)  # 使用 unigram 和 bigram
   - max_features=5000   # 最多 5000 个特征
   
2. MultinomialNB 分类
   - alpha=0.5  # 平滑参数
   
3. 输出预测结果和置信度
```

**训练方法**:
```python
classifier = IntentClassifier()
classifier.train()  # 使用预置数据训练

# 在线学习
classifier.add_training_sample("新样本", "正确意图")
# 每积累 10 个新样本自动重新训练
```

**使用方法**:
```python
intent, confidence, intent_cn = classifier.predict("用户输入")
# 返回：("shipping", 0.95, "物流查询")
```

---

### 4. FAQManager (`knowledge/faq.py`)

**职责**: FAQ 问答对管理

**数据结构**:
```python
faq_entry = {
    "id": 1,
    "question": "什么时候发货？",
    "answer": "亲，我们一般在下单后 24 小时内发货...",
    "keywords": ["发货", "配送", "快递", "什么时候发"],
    "category": "物流",
    "create_time": "2026-03-31T16:30:45"
}
```

**搜索算法**:
```python
def search_faq(self, query, top_k=3):
    """
    搜索相关 FAQ
    
    评分规则:
    1. 关键词匹配：每个关键词 +2 分
    2. 问题相似度：重叠词数 × 0.5 分
    3. 按分数降序排序
    4. 返回前 K 个结果
    """
```

**匹配度计算**:
```python
match_score = calculate_match_score(user_query, faq_question)
if match_score > 0.6:
    return faq.answer  # 直接返回 FAQ 答案
else:
    return llm.generate()  # 使用 LLM 生成
```

---

### 5. ContextManager (`core/context.py`)

**职责**: 多轮对话上下文管理

**数据结构**:
```python
class ConversationContext:
    session_id: str
    messages: List[Dict]  # [{"role": "user/assistant", "content": "..."}]
    user_info: Dict
    current_order: Optional[str]
    intent_stack: List[str]  # 意图栈（用于多轮对话）
    max_history: int = 10  # 最多保留 10 轮对话
```

**上下文限制策略**:
```python
if len(messages) > max_history * 2:
    messages = messages[-max_history * 2:]  # 截断到最近 10 轮
```

**持久化机制**:
```python
# 保存
manager.save_contexts()  # 保存到 data/contexts.json

# 加载
manager._load_contexts()  # 启动时自动加载

# 清理不活跃会话
manager.cleanup_inactive(hours=24)  # 清理 24 小时未活动的会话
```

---

### 6. LLM Client (`core/llm.py`)

**职责**: 统一的大模型调用接口

**支持的模型**:
```python
- MockLLMClient     # 模拟模式（免费测试）
- DeepSeekClient    # DeepSeek Chat
- (可扩展 GPT、通义千问等)
```

**DeepSeek 调用示例**:
```python
def chat(self, messages: List[Dict], **kwargs) -> str:
    url = "https://api.deepseek.com/v1/chat/completions"
    
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "stream": False
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]
```

**System Prompt 设计**:
```python
SYSTEM_PROMPT = """你是一个专业的电商客服助手，名叫{bot_name}。
你服务的店铺是：{shop_name}

你的职责：
1. 热情、专业地回答客户关于商品、订单、物流、售后等问题
2. 使用亲切友好的语气，适当使用 emoji 表情 😊
3. 对于不确定的问题，诚实告知并建议转人工客服

回复风格：
- 简洁明了，避免长篇大论
- 使用"亲"、"您"等敬语
- 重要信息用数字标注（1、2、3...）
- 结尾可以加上温馨提示
"""
```

---

## API 接口文档

### 基础信息

**Base URL**: `http://localhost:8000/api`

**认证方式**: 暂无（内网使用）

**数据格式**: JSON

---

### 接口列表

#### 1. POST `/chat` - 聊天接口

**请求**:
```json
{
    "message": "你好，我想问一下什么时候发货？",
    "session_id": "user_001"  // 可选，不传则自动生成
}
```

**响应**:
```json
{
    "response": "亲，我们一般在下单后 24 小时内发货哦~",
    "intent": "shipping",
    "intent_cn": "物流查询",
    "confidence": 0.95,
    "strategy": "faq_match",
    "session_id": "user_001",
    "processing_time": "0.15s"
}
```

**错误码**:
- `500`: 服务器内部错误

---

#### 2. POST `/train/intent` - 训练意图识别

**请求**:
```json
{
    "text": "怎么开发票",
    "correct_intent": "invoice"
}
```

**响应**:
```json
{
    "status": "success",
    "message": "已添加训练样本：'怎么开发票' -> invoice"
}
```

---

#### 3. POST `/knowledge/faq` - 添加 FAQ

**请求**:
```json
{
    "question": "你们的客服电话是多少？",
    "answer": "我们的客服电话是 400-123-4567",
    "keywords": ["电话", "客服", "联系方式"],
    "category": "其他"
}
```

**响应**:
```json
{
    "status": "success",
    "faq_id": 15,
    "message": "FAQ #15 已添加"
}
```

---

#### 4. GET `/logs` - 获取对话日志

**请求参数**:
```
GET /logs?feedback=bad&limit=50
// feedback: null | "good" | "bad" | "normal"
// limit: 默认 100
```

**响应**:
```json
{
    "logs": [
        {
            "id": "20260331163045123456",
            "timestamp": "2026-03-31T16:30:45.123456",
            "user_input": "什么时候发货？",
            "response": "我们一般在下单后 24 小时内发货...",
            "intent": "shipping",
            "confidence": 0.95,
            "strategy": "faq_match",
            "feedback": "bad"
        }
    ],
    "count": 50
}
```

---

#### 5. POST `/logs/feedback` - 更新日志评价

**请求**:
```json
{
    "log_id": "20260331163045123456",
    "feedback": "good"
}
```

**响应**:
```json
{
    "status": "success",
    "message": "已更新评价为：good"
}
```

**错误码**:
- `404`: 日志记录不存在

---

#### 6. GET `/logs/statistics` - 获取统计数据

**请求参数**:
```
GET /logs/statistics?date=2026-03-31
// date: 可选，YYYY-MM-DD 格式，不传则统计所有时间
```

**响应**:
```json
{
    "statistics": {
        "total": 150,
        "good": 120,
        "bad": 15,
        "normal": 15,
        "accuracy": 80.0,
        "avg_confidence": 0.85,
        "date": "2026-03-31"
    }
}
```

---

#### 7. GET `/logs/bad-cases/analysis` - 坏案例分析

**响应**:
```json
{
    "analysis": {
        "count": 15,
        "common_intents": [
            {"intent": "shipping", "count": 5},
            {"intent": "return_refund", "count": 3}
        ],
        "low_confidence_count": 8,
        "percentage": 53.33,
        "suggestions": [
            "最多的坏案例意图是 'shipping'，建议加强该意图的训练",
            "超过 50% 的坏案例置信度较低，建议优化意图识别模型"
        ]
    }
}
```

---

## 数据模型

### Pydantic Models (`api/routes.py`)

```python
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    intent_cn: str
    confidence: float
    strategy: str
    session_id: str
    processing_time: str

class TrainIntentRequest(BaseModel):
    text: str
    correct_intent: str

class AddFAQRequest(BaseModel):
    question: str
    answer: str
    keywords: List[str]
    category: Optional[str] = "其他"

class UpdateFeedbackRequest(BaseModel):
    log_id: str
    feedback: str  # good/bad/normal
```

---

## 部署说明

### 环境要求

- **操作系统**: Windows / Linux / macOS
- **Python 版本**: 3.8+ (推荐 3.11)
- **内存**: 至少 2GB
- **磁盘**: 至少 500MB

### 安装步骤

#### 1. 创建虚拟环境（使用 Anaconda）

```bash
# 打开 Anaconda Prompt
conda create -n ai_ecommerce_bot python=3.11 -y
conda activate ai_ecommerce_bot
```

#### 2. 安装依赖

```bash
cd ai_ecommerce_bot
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3. 配置环境变量

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env，填入 API Key（可选，不填则使用模拟模式）
DEEPSEEK_API_KEY=your_api_key_here
```

#### 4. 启动服务

```bash
python start.py
```

#### 5. 访问系统

- Web 管理后台：http://localhost:8000/static/admin.html
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

---

## 开发指南

### 代码规范

#### 命名规范
```python
# 类名：大驼峰
class ECommerceBot:
    pass

# 函数名：小写 + 下划线
def get_llm_client():
    pass

# 变量名：小写 + 下划线
session_id = "user_001"

# 常量：全大写 + 下划线
SYSTEM_PROMPT = "..."
```

#### 注释规范
```python
def chat(self, user_input: str, session_id: str) -> Dict:
    """
    处理用户对话
    
    Args:
        user_input: 用户输入的文本
        session_id: 会话 ID
        
    Returns:
        包含回复内容和其他信息的字典
        
    Raises:
        Exception: 处理失败时抛出异常
    """
```

---

### 添加新功能

#### 示例：添加新的意图类型

**Step 1**: 修改 `training/intent.py`

```python
INTENT_TYPES = {
    # ... 现有意图 ...
    "membership": "会员咨询"  # 新增
}

def prepare_training_data(self):
    data = {
        # ... 现有数据 ...
        "membership": [
            "怎么成为会员",
            "会员有什么好处",
            "积分怎么用"
        ]
    }
```

**Step 2**: 重新训练

```python
classifier = IntentClassifier()
classifier.train()
```

**Step 3**: 在 `core/bot.py` 中处理新意图

```python
def chat(self, user_input, session_id):
    # ... 
    elif intent == "membership":
        response = self._handle_membership(user_input)
        strategy = "membership"
```

---

### 调试技巧

#### 1. 查看日志输出

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
```

#### 2. 使用断点调试

```python
def chat(self, user_input, session_id):
    breakpoint()  # Python 3.7+
    # ... 代码会在断点处暂停
```

#### 3. 测试 API 接口

```bash
# 使用 curl 测试
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'

# 或使用 Postman 等工具
```

---

## 性能优化

### 1. 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def search_faq_cached(query: str) -> List[Dict]:
    """缓存 FAQ 搜索结果"""
    return faq_manager.search_faq(query)
```

### 2. 异步处理

```python
@app.post("/chat")
async def chat(request: ChatRequest):
    """使用异步 IO"""
    result = await asyncio.to_thread(bot.chat, request.message, session_id)
    return result
```

### 3. 批量操作

```python
def batch_add_faqs(self, faq_list: List[Dict]):
    """批量添加 FAQ"""
    for faq in faq_list:
        self.faqs.append(faq)
    self._save_faqs()  # 一次性保存
```

---

## 安全考虑

### 1. API 限流

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat")
@limiter.limit("10/minute")  # 每分钟最多 10 次
async def chat(request: Request):
    pass
```

### 2. 输入验证

```python
from pydantic import validator

class ChatRequest(BaseModel):
    message: str
    
    @validator('message')
    def validate_message(cls, v):
        if len(v) > 1000:
            raise ValueError("消息太长")
        if "<script>" in v:
            raise ValueError("禁止脚本注入")
        return v
```

### 3. 敏感信息保护

```python
# .env 文件不应提交到 Git
.env
.env.local
*.key
```

---

## 故障排查

### 常见问题

#### Q1: 服务启动失败

**症状**: `Address already in use`

**解决**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <进程号> /F

# Linux/Mac
lsof -i :8000
kill -9 <进程号>
```

#### Q2: 意图识别准确率低

**症状**: 经常识别错误意图

**解决**:
1. 增加训练样本（每个意图至少 20 条）
2. 确保不同意图之间边界清晰
3. 添加易混淆样本的专项训练

#### Q3: FAQ 匹配不到

**症状**: 明明有相关 FAQ，但就是匹配不到

**解决**:
1. 增加关键词数量
2. 优化关键词质量（使用高频词）
3. 考虑同义词、近义词

#### Q4: LLM 调用失败

**症状**: `API call failed`

**解决**:
1. 检查 API Key 是否正确
2. 检查网络连接
3. 查看账户余额
4. 切换到模拟模式测试

---

## 扩展方向

### 短期（1-2 周）

- [ ] 批量导入 FAQ（Excel/CSV）
- [ ] 更多统计图表（折线图、饼图）
- [ ] 用户登录系统
- [ ] 多会话管理

### 中期（1 个月）

- [ ] 自动化坏案例分析
- [ ] 智能推荐优化方案
- [ ] 集成更多 AI 模型
- [ ] 移动端适配

### 长期（3 个月+）

- [ ] 完全自动化学习
- [ ] 多语言支持
- [ ] 语音客服集成
- [ ] 开放 API 平台

---

## 参考资料

### 官方文档
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [scikit-learn 用户指南](https://scikit-learn.org/stable/user_guide.html)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)

### 学习资源
- 《自然语言处理入门》
- 《深度学习与神经网络》
- Prompt Engineering 官方指南

### 相关项目
- GitHub: shop-assist-ai-free
- GitHub: PandaWiki
- GitHub: ChatGPT-On-CS

---

## 更新日志

### v1.0.0 (2026-03-31)
- ✅ 完整的对话系统
- ✅ 管理后台界面
- ✅ 日志记录与分析
- ✅ 意图识别训练
- ✅ FAQ 知识库管理
- ✅ 数据统计看板

---

## 许可证

本项目仅供学习实践使用。

---

## 联系方式

- 项目地址：`d:\PycharmProjects\AI_Chatbot\ai_ecommerce_bot`
- 技术文档：详见项目根目录 `.md` 文件

---

*最后更新：2026 年 3 月 31 日*
