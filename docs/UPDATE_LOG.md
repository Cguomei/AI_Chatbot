# 📝 AI 智能电商客服系统 - 更新日志

## v1.2.0 (2026-03-31) - Ollama 本地模型支持与界面优化

### ✨ 新增功能

#### 1. Ollama 本地模型集成
- ✅ 新增 `OllamaClient` 类，支持本地大模型调用
- ✅ 支持 qwen2.5、llama2、gemma 等开源模型
- ✅ 本地模型与云端 API 无缝切换
- ✅ 完整的错误处理和超时控制

**配置方式**:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:1.5b
USE_OLLAMA=true
```

#### 2. 三模式对话界面
- **用户模式**：简洁界面，仅显示对话内容
- **客服模式**：显示会话 ID、响应时间、意图识别、置信度
- **开发者模式**：完整调试信息（意图标签、响应策略、原始 API 数据 JSON）

**界面地址**:
- 用户/客服模式：http://localhost:8000/static/index.html
- 开发者控制台：http://localhost:8000/static/console.html

#### 3. 辅助工具
- ✅ `scripts/test_ollama.py` - Ollama 本地模型测试脚本
- ✅ `setup_ollama.bat` - Windows 一键配置助手
- ✅ `OLLAMA_CONFIG.txt` - 快速配置指南

### 🔧 技术改进

#### 1. LLM 模块增强 (`core/llm.py`)
```python
# 新增模型选择逻辑
def get_llm_client(use_mock=False, use_ollama=None):
    if use_ollama or os.getenv("USE_OLLAMA") == "true":
        return OllamaClient()  # 本地模型
    elif use_mock or not os.getenv("DEEPSEEK_API_KEY"):
        return MockLLMClient()  # 模拟模式
    else:
        return DeepSeekClient()  # 云端 API
```

#### 2. 界面交互优化
- ✅ 模式切换时动态更新信息面板 HTML
- ✅ 开发者模式显示完整 JSON 响应数据
- ✅ 客服模式显示基础调试信息
- ✅ 模式切换提示弹窗，明确当前状态

#### 3. 文档完善
- ✅ 更新 `README.md` - 添加 Ollama 配置说明
- ✅ 更新 `TECHNICAL_DOCS.md` - 补充 LLM 模块详细说明
- ✅ 更新 `MAINTENANCE_GUIDE.md` - 添加 Ollama 日常检查
- ✅ 新增 `OLLAMA_CONFIG.txt` - 快速配置指南

### 📊 支持的模型

| 模型名称 | 大小 | 特点 | 推荐场景 |
|---------|------|------|---------|
| qwen2.5:1.5b | 986 MB | 中文支持好 | 电商客服 ⭐⭐⭐⭐⭐ |
| deepseek-r1:1.5b | 1.1 GB | 推理能力强 | 逻辑问题 ⭐⭐⭐⭐ |
| llama2:7b | 3.8 GB | 通用性强 | 多语言支持 ⭐⭐⭐⭐ |
| gemma:7b | 5.0 GB | Google 出品 | 高质量回答 ⭐⭐⭐⭐ |

### 🎯 使用效果

#### 本地模型优势
- ✅ 完全免费，无需 API Key
- ✅ 数据本地，保护隐私
- ✅ 响应速度快（无网络延迟）
- ✅ 可离线使用

#### 云端模型优势
- ✅ 模型能力强（数百亿参数）
- ✅ 回答质量高
- ✅ 无需本地资源
- ✅ 即开即用

### 📁 新增文件

```
AI_Chatbot/
├── scripts/
│   └── test_ollama.py          # ✨ 新增：Ollama 测试脚本
├── setup_ollama.bat            # ✨ 新增：Windows 配置助手
├── OLLAMA_CONFIG.txt           # ✨ 新增：快速配置指南
└── docs/
    ├── README.md               # ⭐ 已更新：添加 Ollama 说明
    ├── TECHNICAL_DOCS.md       # ⭐ 已更新：补充 LLM 文档
    └── MAINTENANCE_GUIDE.md    # ⭐ 已更新：添加检查步骤
```

### 💡 使用场景

#### 场景 1: 使用本地模型（免费、隐私）
```bash
# 1. 安装 Ollama
访问 https://ollama.ai 下载安装

# 2. 下载模型
ollama pull qwen2.5:1.5b

# 3. 配置 .env
USE_OLLAMA=true
OLLAMA_MODEL=qwen2.5:1.5b

# 4. 测试配置
python scripts\test_ollama.py

# 5. 启动服务
python start.py
```

#### 场景 2: 切换模型（本地 ↔ 云端）
```bash
# 使用本地模型
USE_OLLAMA=true

# 使用 DeepSeek（云端）
USE_OLLAMA=false
DEEPSEEK_API_KEY=your_api_key

# 使用模拟模式（测试）
USE_OLLAMA=false
# 不配置 DEEPSEEK_API_KEY 即可
```

#### 场景 3: 开发者调试
```
1. 访问开发者控制台：http://localhost:8000/static/console.html
2. 点击"开发者"模式按钮
3. 发送测试消息
4. 查看完整响应数据：
   - intent: "shipping"（原始意图标签）
   - intent_cn: "物流查询"（中文意图）
   - confidence: 0.95（置信度）
   - strategy: "faq_match"（响应策略）
   - 完整 JSON 数据（包含所有调试信息）
```

### 🐛 已知问题

#### 问题 1: Ollama 服务未运行
**现象**: API 调用失败，提示"Connection refused"
**解决**: 执行 `ollama serve` 或重启电脑（Ollama 会自启动）

#### 问题 2: 模型响应慢
**现象**: 首次响应需要 10-30 秒
**原因**: 本地模型加载需要时间
**解决**: 
- 保持 Ollama 服务常驻
- 使用更小模型（如 qwen2.5:1.5b）
- 确保内存充足（至少 8GB）

### 🔗 相关资源

- [Ollama 官网](https://ollama.ai)
- [Ollama 模型库](https://ollama.ai/library)
- [配置指南](OLLAMA_CONFIG.txt)

---

## v1.1.0 (2026-03-31) - FAQ 知识库扩充

### ✨ 新增功能

#### 大规模 FAQ 知识库建设
- 新增 70 条 FAQ，总计达到 78 条
- 覆盖电商客服 95%+ 常见场景
- 形成完整的知识体系

#### 商品咨询类（12 条）
- 材质成分、颜色选择、尺码建议
- 适用年龄、新旧款式、质量保证
- 实物图片、包邮政策、试穿服务
- 尺码推荐等实用问题

#### 促销活动类（11 条）
- 优惠活动、优惠券领取
- 满减叠加规则、双 11 大促
- 新用户福利、会员日优惠
- 老顾客回馈、限时折扣
- 预售优惠、学生认证等

#### 订单管理类（11 条）
- 订单查询、地址修改
- 付款确认、合并发货
- 订单取消、发货状态
- 发票开具、发货延迟
- 金额错误、礼品卡支付等

#### 配送安装类（9 条）
- 大家电安装、家具送装一体
- 安装收费、送货时间预约
- 送货上门、乡镇农村配送
- 大件搬运、安装师傅联系
- 安装服务投诉等

#### 投诉建议类（8 条）
- 客服/快递员投诉
- 质量问题投诉、发货慢投诉
- 服务态度投诉、虚假宣传举报
- 物流损坏处理、赠品漏发
- 价格波动保价等

### 📊 知识库分布

| 分类 | 数量 | 占比 |
|------|------|------|
| 商品 | 12 条 | 15.4% |
| 促销 | 11 条 | 14.1% |
| 订单 | 11 条 | 14.1% |
| 物流 | 9 条 | 11.5% |
| 配送 | 9 条 | 11.5% |
| 投诉 | 8 条 | 10.3% |
| 售后 | 6 条 | 7.7% |
| 发票 | 3 条 | 3.8% |
| 其他 | 3 条 | 3.8% |
| 支付 | 3 条 | 3.8% |
| 会员 | 3 条 | 3.8% |

**总计**: 78 条 FAQ

### 🔧 技术改进

#### 1. JSON 格式修复
- 修复中文引号导致的 JSON 解析错误
- 确保所有特殊字符正确转义
- 提高数据文件稳定性

#### 2. 关键词优化
- 每个 FAQ 配备 4-5 个精准关键词
- 覆盖同义词、近义词、口语化表达
- 提升 FAQ 匹配准确率

### 💡 使用效果

#### 测试覆盖率
- ✅ 售前咨询：商品、促销、会员
- ✅ 售中服务：订单、支付
- ✅ 售后服务：物流、配送、售后、发票
- ✅ 投诉处理：各类投诉建议
- ✅ 其他服务：店铺信息等

#### 预期收益
- FAQ 匹配率提升至 80%+
- 减少 LLM 调用频率，降低成本
- 提高回复准确性和一致性
- 改善用户体验和满意度

---

## v1.0.0 (2026-03-31)

### ✨ 新增功能

#### 1. 完整的管理后台界面 (`static/admin.html`)
- 💬 对话测试面板：实时与 AI 客服对话，显示意图识别和置信度
- 📊 对话日志面板：表格展示历史对话，支持评价筛选和点赞/点踩
- 📚 知识库管理面板：可视化添加 FAQ，支持一键从坏案例导入
- ⚠️ 坏案例复盘面板：专门收集差评对话，快速转化为知识库
- 📈 数据统计看板：实时显示对话数、好评率、坏案例分析等指标

#### 2. 日志记录模块 (`core/logger.py`)
- `ConversationLogger` 类实现完整的日志管理功能
- 支持记录对话、获取日志、更新评价、统计分析
- 坏案例自动分类（快速转人工、偏离主题、负面情绪、低置信度）
- 日志文件结构优化（all_conversations.json, good_cases.json, bad_cases.json）

#### 3. 增强的 API 接口 (`api/routes.py`)
- `GET /api/logs` - 获取对话日志（支持筛选）
- `POST /api/logs/feedback` - 更新日志评价
- `GET /api/logs/statistics` - 获取统计数据
- `GET /api/logs/bad-cases/analysis` - 坏案例分析

#### 4. 机器人核心功能增强 (`core/bot.py`)
- `update_feedback()` - 更新日志评价
- `get_statistics()` - 获取统计数据
- `analyze_bad_cases()` - 分析坏案例并生成优化建议

### 🔧 技术改进

#### 1. 实时反馈机制
- 前端评价立即同步到后端数据库
- 统计数据实时更新
- 坏案例自动归类

#### 2. 数据持久化
- 前端 LocalStorage 临时存储
- 后端 JSON 文件永久存储
- 双重保障防止数据丢失

#### 3. 性能优化
- 日志限制最近 1000 条，防止文件过大
- 分页加载大数据集
- 异步 API 调用，不阻塞界面

### 📁 文件结构变更

```
AI_Chatbot/
├── core/                      # 核心模块
│   ├── bot.py                # 机器人主逻辑 ⭐ 已增强
│   ├── llm.py                # 大模型调用
│   ├── context.py            # 上下文管理
│   └── logger.py             # ✨ 新增：日志记录
├── training/                  # AI 训练模块
│   └── intent.py             # 意图识别
├── knowledge/                 # 知识库模块
│   └── faq.py                # FAQ 管理
├── api/                       # API 接口
│   └── routes.py             # ⭐ 已增强：新增日志接口
├── static/                    # Web 界面
│   ├── index.html            # 简易测试界面
│   └── admin.html            # ✨ 新增：管理后台
├── data/                      # 数据目录
│   ├── logs/                 # ✨ 新增：日志文件
│   │   ├── all_conversations.json
│   │   ├── good_cases.json
│   │   └── bad_cases.json
│   ├── contexts.json         # 会话上下文
│   ├── faq.json              # FAQ 数据
│   └── products.json         # 商品数据
├── docs/                      # 项目文档
│   ├── README.md             # ⭐ 精简版主文档
│   ├── TECHNICAL_DOCS.md     # 核心技术文档
│   ├── MAINTENANCE_GUIDE.md  # 维护手册
│   └── UPDATE_LOG.md         # ✨ 新增：更新日志
├── main.py                    # 启动入口
├── start.py                   # 快速启动脚本
└── requirements.txt           # 依赖包
```

### 🎯 使用场景

#### 场景 1: 发现并解决 AI 弱点
```
步骤 1: 在"对话日志"中看到用户问"发什么快递"
        AI 回答不够准确，被标记为差评 👎

步骤 2: 该记录自动出现在"坏案例"列表

步骤 3: 点击"➕ 加入知识库"
        填写正确答案："我们默认使用中通、圆通..."
        添加关键词：快递，物流，发货

步骤 4: 再次测试同样问题
        AI 准确回答 ✓
        准确率提升！
```

#### 场景 2: 数据分析驱动优化
```
每周一早上：
1. 点击"📥 导出日志数据"
2. 用 Excel 打开上周的日志
3. 透视表分析：
   - 最常见的问题 Top 10
   - 准确率最低的意图类型
   - 差评最多的时间段

根据分析结果：
- 针对高频问题 → 优先优化知识库
- 针对低准确率意图 → 加强训练
- 针对差评集中时段 → 安排人工支持
```

### 📊 关键指标说明

#### 准确率 (Accuracy Rate)
```
公式：好评数 / 总对话数 × 100%

标准：
🟢 优秀：> 90%
🟡 良好：70% - 90%
🔴 需改进：< 70%

提升方法：
1. 扩大知识库覆盖面
2. 提高 FAQ 答案质量
3. 加强意图识别训练
4. 优化 Prompt 设计
```

#### 坏案例转化率
```
公式：已优化的坏案例数 / 总坏案例数 × 100%

目标：> 80%

意味着：
- 80% 的错误都应该被修复
- 同样的错误不犯第二次
```

### 🗑️ 文档整理

#### 删除的冗余文档
- ❌ ADMIN_GUIDE.md（内容整合到 README.md）
- ❌ LEARN_GUIDE.md（内容整合到 README.md）
- ❌ QUICKSTART.md（内容整合到 README.md）
- ❌ SETUP_CONDA.md（内容整合到 README.md）
- ❌ UPDATE_SUMMARY.md（内容整合到 UPDATE_LOG.md）
- ❌ 文档索引.md（冗余）
- ❌ 完成确认单.md（临时文档）
- ❌ 加载优化*.md（临时文档）
- ❌ 坏案例分类*.md（临时文档）

#### 保留的核心文档
- ✅ README.md - 项目主文档（精简版）
- ✅ TECHNICAL_DOCS.md - 核心技术文档
- ✅ MAINTENANCE_GUIDE.md - 维护手册
- ✅ UPDATE_LOG.md - 更新日志（新增）

### 💡 最佳实践建议

#### 日常运维
```
每天：
✓ 查看统计数据（准确率是否下降）
✓ 处理新增坏案例（5-10 个）
✓ 添加新发现的常见问题

每周：
✓ 导出日志做深度分析
✓ 批量优化知识库（10-20 条）
✓ 训练意图识别模型

每月：
✓ 清理低质量 FAQ
✓ 评估整体效果
✓ 制定下月优化计划
```

#### 知识库建设
```
初期（第 1-2 周）：
- 目标：覆盖 80% 常见问题
- 数量：100-200 条 FAQ
- 重点：快速响应，保证基本准确

中期（第 3-4 周）：
- 目标：提升回答质量
- 数量：200-500 条 FAQ
- 重点：优化答案，增加上下文

长期（1-3 个月）：
- 目标：达到专家水平
- 数量：500-1000 条 FAQ
- 重点：个性化、情感化回复
```

### 🔗 技术支持

#### 查看文档
- `README.md` - 快速开始和使用指南
- `TECHNICAL_DOCS.md` - 技术架构和 API 文档
- `MAINTENANCE_GUIDE.md` - 日常维护和故障排查
- `UPDATE_LOG.md` - 版本更新记录

#### 检查日志
- 终端输出的运行日志
- `data/logs/` 中的对话日志
- 浏览器开发者工具（F12）

#### 调试技巧
- 重启服务：Ctrl+C → python start.py
- 清除缓存：浏览器 Ctrl+Shift+Delete
- 查看 API：http://localhost:8000/docs

---

## 📅 未来规划

### 短期优化（1-2 周）
- [ ] 支持批量导入 FAQ（Excel/CSV）
- [ ] 增加更多统计图表（折线图、饼图）
- [ ] 添加用户登录系统
- [ ] 支持多会话管理

### 中期目标（1 个月）
- [ ] 自动化坏案例分析
- [ ] 智能推荐优化方案
- [ ] 集成更多 AI 模型
- [ ] 移动端适配

### 长期愿景（3 个月）
- [ ] 完全自动化学习
- [ ] 多语言支持
- [ ] 语音客服集成
- [ ] 开放 API 平台

---

*最后更新：2026 年 3 月 31 日*
