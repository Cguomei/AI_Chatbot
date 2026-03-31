# 🔧 AI 电商客服系统 - 维护手册

## 📋 日常维护清单

### 每日维护（10-15 分钟）

#### ✅ 早上检查（5 分钟）

**1. 服务状态检查**
```bash
# 检查服务是否运行
curl http://localhost:8000/health

# 预期输出：{"status": "ok", "service": "AI 电商客服"}
```

**2. 查看统计数据**
- 访问管理后台：http://localhost:8000/static/admin.html
- 查看左侧"今日统计"卡片
- 关注指标：
  - 准确率是否大幅下降？（下降超过 10% 需警惕）
  - 差评数是否异常增多？

**3. 快速浏览坏案例**
- 点击"坏案例复盘"标签
- 查看是否有新增的坏案例
- 标记紧急需要处理的

**4. Ollama 本地模型检查**（如使用）
```bash
# 检查 Ollama 服务是否运行
ollama list

# 如果 Ollama 未运行，启动服务
ollama serve
```

---

#### ✅ 晚上处理（5-10 分钟）

**1. 处理当天坏案例**
```
操作流程：
1. 打开"坏案例复盘"页面
2. 逐个分析坏案例产生原因：
   ├─ 知识库没有 → 点击"➕ 加入知识库"
   ├─ 意图识别错误 → 记录样本，准备训练
   └─ 模型回答质量差 → 优化 Prompt 或更换模型
3. 每个坏案例处理时间控制在 2 分钟内
```

**2. 查看好评对话**
- 点击"对话日志" → 筛选"好评"
- 找出用户满意的回答
- 思考能否复制到其他场景

**3. 简单统计**
- 记录当天总对话数
- 记录准确率变化
- 发现异常及时记录

---

### 每周维护（1-2 小时）

#### 📅 周一：深度数据分析（30 分钟）

**1. 导出上周日志**
```
操作：
1. 管理后台 → 左侧"📥 导出日志数据"
2. 保存 JSON 文件到本地
3. 用 Excel 或 Python 分析
```

**2. 数据分析维度**

使用 Excel 透视表：
```
行：意图类型
列：评价（好/差/普通）
值：计数

分析：
- 哪个意图的差评最多？
- 哪个意图的准确率最低？
- 哪些问题用户最常问？
```

**3. 制定本周优化计划**
```
示例：
优先级 1: 优化"物流查询"意图（差评最多）
优先级 2: 添加"会员咨询"相关 FAQ（高频问题）
优先级 3: 训练易混淆样本（意图边界模糊）
```

---

#### 📅 周三：知识库更新（30-60 分钟）

**1. 批量添加 FAQ**
```
目标：每周添加 10-20 条新 FAQ

来源：
- 周一分析出的高频问题
- 坏案例中反复出现的问题
- 业务更新带来的新问题
- 用户反馈的新需求
```

**2. 优化现有 FAQ**
```
检查标准：
- 从未被匹配到的 FAQ（利用率低）→ 删除或优化关键词
- 经常被点踩的 FAQ（质量差）→ 重写答案
- 答案过时的 FAQ → 更新内容
```

**3. 调整分类结构**
```
如果某个分类超过 50 条 FAQ：
- 考虑细分二级分类
- 例如："物流" → "发货时效"、"物流配送"、"运费政策"
```

---

#### 📅 周五：模型调优（30 分钟）

**1. 检查意图识别准确率**
```python
# 测试代码
from training.intent import IntentClassifier

classifier = IntentClassifier()

test_cases = [
    ("什么时候发货", "shipping"),
    ("怎么退货", "return_refund"),
    ("发什么快递", "shipping"),  # 易混淆
]

for text, expected_intent in test_cases:
    intent, confidence, _ = classifier.predict(text)
    if intent != expected_intent:
        print(f"❌ '{text}' 识别错误")
        classifier.add_training_sample(text, expected_intent)

# 重新训练
classifier.train()
```

**2. 调整 System Prompt**
```python
# 根据本周的坏案例，调整 Prompt

# 示例：如果发现 AI 回答太啰嗦
SYSTEM_PROMPT = """
...
回复风格：
- 简洁明了，控制在 100 字以内  # 新增
- 重要信息优先说
...
"""
```

**3. 评估模型效果**
```
如果使用多个模型：
- 对比不同模型的回答质量
- 计算各模型的准确率
- 选择最优模型作为主力
```

---

### 每月维护（2-4 小时）

#### 📅 月初：月度总结与规划

**1. 月度数据统计**
```python
统计维度：
- 月总对话数
- 平均准确率
- 好评率趋势
- 坏案例总数
- 知识库增长数
```

**2. 制作月度报表**
```markdown
## 2026 年 3 月报表

### 核心指标
- 总对话数：1,500
- 平均准确率：85%（↑5%）
- 好评率：82%
- 处理坏案例：120 个

### 主要改进
1. 新增 FAQ 150 条
2. 优化意图识别算法
3. 引入坏案例复盘机制

### 下月目标
1. 准确率提升到 90%
2. 知识库达到 500 条
3. 坏案例减少 50%
```

**3. 制定月度优化计划**
```
重点任务：
□ 大规模知识库整理（删除低质 FAQ）
□ 意图识别模型升级
□ 新功能的开发和测试
□ 文档更新和补充
```

---

## 🔍 健康检查清单

### 系统健康检查（每周一次）

#### 1. 服务性能检查

```bash
# 测试响应时间
time curl http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'

# 正常范围：< 1 秒
# 警告范围：1-3 秒
# 危险范围：> 3 秒
```

**可能的问题**:
- 响应变慢 → 检查服务器负载
- 频繁超时 → 检查网络连接
- 偶发错误 → 查看日志文件

---

#### 2. 数据文件检查

```bash
# 检查日志文件大小
ls -lh data/logs/

# 正常大小：
# - all_conversations.json: < 1MB
# - good_cases.json: < 500KB
# - bad_cases.json: < 500KB
```

**清理策略**:
```python
# 如果文件过大，手动清理
import json

with open('data/logs/all_conversations.json', 'r', encoding='utf-8') as f:
    logs = json.load(f)

# 只保留最近 500 条
logs = logs[-500:]

with open('data/logs/all_conversations.json', 'w', encoding='utf-8') as f:
    json.dump(logs, f, ensure_ascii=False, indent=2)
```

---

#### 3. 依赖包检查

```bash
# 查看已安装的包
pip list

# 检查是否有可更新的包
pip list --outdated

# 谨慎更新（先备份）
pip install --upgrade package_name
```

**注意**: 
- 生产环境不要随意更新依赖
- 更新前先在测试环境验证
- 记录更新日志

---

### 数据备份（每月一次）

#### 备份脚本

创建 `backup.py`:
```python
import os
import shutil
from datetime import datetime

def backup_data():
    """备份所有数据文件"""
    
    # 创建备份目录
    backup_dir = f"backups/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # 要备份的文件
    files_to_backup = [
        "data/logs/all_conversations.json",
        "data/logs/good_cases.json",
        "data/logs/bad_cases.json",
        "data/contexts.json",
        "data/faq.json",
        "data/products.json",
        ".env"
    ]
    
    # 复制文件
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            # 保持目录结构
            dest_path = os.path.join(backup_dir, file_path.replace("/", os.sep))
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(file_path, dest_path)
            print(f"✅ 已备份：{file_path}")
    
    # 压缩备份
    shutil.make_archive(backup_dir, 'zip', backup_dir)
    print(f"\n📦 备份完成：{backup_dir}.zip")
    
    return backup_dir

if __name__ == "__main__":
    backup_data()
```

**使用方法**:
```bash
python backup.py
```

---

## 🐛 故障排查指南

### 常见问题速查

#### Q1: 服务无法启动

**症状**:
```
Error: Address already in use
```

**解决步骤**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <进程号> /F

# 或使用 PowerShell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force
```

---

#### Q2: API 返回 500 错误

**症状**:
```json
{
    "detail": "Internal Server Error"
}
```

**排查步骤**:
```
1. 查看终端输出的错误日志
2. 检查 .env 配置文件是否正确
3. 检查 API Key 是否有效
4. 重启服务看是否恢复
```

**常见原因**:
- API Key 无效或过期
- 依赖包版本冲突
- 数据库文件损坏

---

#### Q3: 意图识别完全不准

**症状**:
```
所有问题都识别为同一个意图
或置信度都很低 (< 0.5)
```

**解决步骤**:
```python
# 1. 检查训练数据
from training.intent import IntentClassifier

classifier = IntentClassifier()

# 2. 查看训练数据量
texts, labels = classifier.prepare_training_data()
print(f"训练数据：{len(texts)} 条")
# 应该 > 100 条

# 3. 重新训练
classifier.train()

# 4. 测试
intent, conf, _ = classifier.predict("你好")
print(f"预测结果：{intent}, 置信度：{conf}")
```

---

#### Q4: FAQ 搜索结果为空

**症状**:
```
明明有相关 FAQ，但 search_faq() 返回空列表
```

**解决步骤**:
```python
# 1. 检查 FAQ 数据
from knowledge.faq import FAQManager

manager = FAQManager()
print(f"FAQ 数量：{len(manager.faqs)}")

# 2. 检查关键词
for faq in manager.faqs:
    print(f"{faq['question']}: {faq['keywords']}")

# 3. 测试搜索
results = manager.search_faq("发货", top_k=3)
print(f"搜索结果：{len(results)} 条")

# 4. 如果结果为空，添加默认 FAQ
manager.add_faq(
    question="什么时候发货？",
    answer="我们一般在下单后 24 小时内发货",
    keywords=["发货", "配送", "快递"],
    category="物流"
)
```

---

#### Q5: 管理后台打不开

**症状**:
```
浏览器显示 404 或空白页
```

**排查步骤**:
```bash
# 1. 检查静态文件是否存在
ls static/admin.html

# 2. 检查 FastAPI 是否挂载了静态文件
# main.py 中应该有：
app.mount("/static", StaticFiles(directory="static"), name="static")

# 3. 重启服务
Ctrl+C
python start.py

# 4. 清除浏览器缓存
Ctrl+Shift+Delete
```

---

### 日志分析方法

#### 1. 查看应用日志

```bash
# 服务运行时，终端会输出日志
INFO:     127.0.0.1:52347 - "GET /api/chat HTTP/1.1" 200 OK

# 正常：200 状态码
# 警告：4xx 客户端错误
# 错误：5xx 服务器错误
```

#### 2. 查看对话日志

```python
import json

with open('data/logs/all_conversations.json', 'r', encoding='utf-8') as f:
    logs = json.load(f)

# 分析最近的对话
for log in logs[-10:]:
    print(f"时间：{log['timestamp']}")
    print(f"问题：{log['user_input']}")
    print(f"回答：{log['response']}")
    print(f"评价：{log['feedback']}")
    print("---")
```

#### 3. 使用日志分析工具

创建 `analyze_logs.py`:
```python
import json
from collections import Counter
from datetime import datetime

def analyze_logs():
    with open('data/logs/all_conversations.json', 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    # 统计评价分布
    feedback_counts = Counter(log['feedback'] for log in logs)
    print("📊 评价分布:")
    for feedback, count in feedback_counts.items():
        percentage = count / len(logs) * 100
        print(f"  {feedback}: {count} ({percentage:.1f}%)")
    
    # 统计意图分布
    intent_counts = Counter(log['intent'] for log in logs)
    print("\n🎯 意图分布 Top 5:")
    for intent, count in intent_counts.most_common(5):
        print(f"  {intent}: {count}次")
    
    # 找出低置信度的对话
    low_confidence = [log for log in logs if log['confidence'] < 0.6]
    print(f"\n⚠️  低置信度对话：{len(low_confidence)} 条")
    
    # 按日期统计
    date_counts = Counter(log['timestamp'][:10] for log in logs)
    print("\n📅 每日对话数:")
    for date, count in sorted(date_counts.items()):
        print(f"  {date}: {count}次")

if __name__ == "__main__":
    analyze_logs()
```

---

## 🔄 版本升级流程

### 代码更新

#### 1. 备份当前版本

```bash
# 复制整个项目目录
cp -r ai_ecommerce_bot ai_ecommerce_bot_backup_$(date +%Y%m%d)
```

#### 2. 拉取新代码

```bash
cd ai_ecommerce_bot
git pull origin main
```

#### 3. 检查依赖更新

```bash
# 查看 requirements.txt 是否有新版本
pip install -r requirements.txt --upgrade
```

#### 4. 测试新功能

```bash
# 在测试环境验证
python -m pytest tests/

# 或手动测试关键功能
curl http://localhost:8000/api/chat ...
```

#### 5. 重启服务

```bash
# 停止旧服务
Ctrl+C

# 启动新服务
python start.py
```

---

### 数据库迁移

#### 如果数据结构发生变化

```python
# 创建迁移脚本 migrate_db.py

import json
import os

def migrate_logs():
    """迁移日志数据到新格式"""
    
    old_file = "data/logs/conversations.json"
    new_file = "data/logs/all_conversations.json"
    
    if not os.path.exists(old_file):
        return
    
    with open(old_file, 'r', encoding='utf-8') as f:
        old_logs = json.load(f)
    
    # 转换格式
    new_logs = []
    for log in old_logs:
        new_log = {
            "id": log.get("id", ""),
            "timestamp": log.get("timestamp", ""),
            "session_id": log.get("session_id", ""),
            "user_input": log.get("user_input", ""),
            "response": log.get("response", ""),
            "intent": log.get("intent", ""),
            "confidence": log.get("confidence", 0),
            "strategy": log.get("strategy", "llm"),
            "feedback": log.get("feedback", "normal")
        }
        new_logs.append(new_log)
    
    # 保存新格式
    with open(new_file, 'w', encoding='utf-8') as f:
        json.dump(new_logs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已迁移 {len(new_logs)} 条日志")

if __name__ == "__main__":
    migrate_logs()
```

---

## 📞 技术支持

### 获取帮助的途径

#### 1. 查看文档
- `TECHNICAL_DOCS.md` - 技术文档
- `ADMIN_GUIDE.md` - 管理后台指南
- `LEARN_GUIDE.md` - 学习教程

#### 2. 检查日志
- 终端输出的运行日志
- `data/logs/` 中的对话日志
- 浏览器开发者工具（F12）

#### 3. 在线资源
- FastAPI 官方文档：https://fastapi.tiangolo.com/
- scikit-learn 中文文档：https://scikit-learn.org/stable/
- GitHub Issues: 提交问题

---

### 应急联系方案

**严重故障**（服务完全不可用）:
```
1. 立即重启服务
2. 如果不行，回滚到备份版本
3. 收集错误日志
4. 寻求技术支持
```

**一般故障**（部分功能异常）:
```
1. 记录故障现象
2. 查看相关日志
3. 尝试复现问题
4. 在工作时间修复
```

---

## 📝 维护记录模板

### 日常维护记录

```markdown
## 维护记录 - 2026-03-31

### 早检（09:00）
- [x] 服务运行正常
- [x] 昨日统计：
  - 总对话：150
  - 准确率：85%
  - 差评：10

### 晚处理（18:00）
- [x] 处理坏案例：5 个
  - 3 个已加入知识库
  - 2 个需要训练
- [x] 查看好评：8 个
- [ ] 待办：明天添加"会员咨询"FAQ

### 备注
今天"物流查询"意图差评较多，需要重点关注
```

### 周维护记录

```markdown
## 周维护记录 - 2026-W14

### 周一分析
- 导出日志：350 条
- 主要问题：物流相关差评占 60%
- 优化重点：物流 FAQ

### 周三更新
- 新增 FAQ: 15 条
- 优化 FAQ: 5 条
- 删除 FAQ: 2 条

### 周五调优
- 重新训练意图模型
- 调整 System Prompt
- 准确率：85% → 88% ✓

### 下周计划
- 重点优化退换货流程
- 添加商品推荐功能
```

---

## 🎯 维护目标 KPI

### 可用性指标
- **服务可用率**: > 99%
- **平均响应时间**: < 1 秒
- **故障恢复时间**: < 30 分钟

### 质量指标
- **对话准确率**: > 85%（初期），> 90%（成熟期）
- **用户满意度**: > 80%
- **坏案例转化率**: > 80%

### 效率指标
- **日均处理对话**: > 100 条
- **周均新增 FAQ**: > 10 条
- **月均优化次数**: > 4 次

---

*最后更新：2026 年 3 月 31 日*
