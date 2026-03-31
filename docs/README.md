# 🤖 AI 智能电商客服系统

## 📌 快速开始

### 1. 环境要求
- Python 3.8+
- 操作系统：Windows / Linux / macOS

### 2. 安装步骤
```bash
# 克隆项目后进入目录
cd AI_Chatbot

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 填入 API Key（不配置则使用模拟模式）
```

### 3. 启动服务
```bash
python start.py
```

### 4. 访问系统
- **用户对话页面**: http://localhost:8000/static/index.html
- **管理后台**: http://localhost:8000/static/admin.html
- **开发者控制台**: http://localhost:8000/static/console.html
- **API 文档**: http://localhost:8000/docs

---

## 🎯 项目简介

这是一个教学向的 AI 电商客服对话系统，提供完整的对话管理、知识库构建、意图识别、日志分析等功能。

### 核心功能
- ✅ 智能对话机器人（支持多轮对话）
- ✅ 意图识别（基于机器学习）
- ✅ FAQ 知识库管理
- ✅ 对话日志记录与分析
- ✅ 好评/差评评价系统
- ✅ 坏案例复盘与优化
- ✅ 数据统计看板
- ✅ 可视化 Web 管理后台

### 技术栈
- **后端**: Python 3.11 + FastAPI 0.109.0
- **AI 模型**: 
  - 云端：DeepSeek / GPT-3.5 / 通义千问（可切换）
  - 本地：Ollama（支持 qwen2.5、llama2 等开源模型）
- **机器学习**: scikit-learn 1.4.0（意图识别）
- **数据库**: JSON 文件存储（轻量级）
- **前端**: 原生 HTML + JavaScript

---

## 📁 项目结构

```
AI_Chatbot/
├── core/              # 核心引擎
│   ├── bot.py        # 机器人主逻辑
│   ├── llm.py        # 大模型调用
│   ├── context.py    # 上下文管理
│   └── logger.py     # 日志记录
├── training/          # AI 训练模块
│   └── intent.py     # 意图识别
├── knowledge/         # 知识库模块
│   └── faq.py        # FAQ 管理
├── api/               # API 接口
│   └── routes.py     # RESTful API
├── static/            # Web 界面
│   ├── index.html    # 用户对话页面
│   └── admin.html    # 管理后台
├── data/              # 数据存储
│   ├── logs/         # 对话日志
│   ├── faq.json      # FAQ 知识库
│   ├── products.json # 商品数据
│   └── contexts.json # 会话上下文
├── docs/              # 项目文档
├── main.py           # 应用入口
├── start.py          # 启动脚本
└── requirements.txt  # 依赖列表
```

---

## 🚀 使用指南

### 用户对话页面
访问 `http://localhost:8000/static/index.html` 进行对话测试：
- 输入问题，获取 AI 回复
- 查看意图识别结果和置信度
- 实时显示响应时间
- **三种模式切换**：
  - **用户模式**：简洁界面，仅显示对话
  - **客服模式**：显示会话 ID、响应时间、意图识别、置信度
  - **开发者模式**：显示完整调试信息（意图标签、响应策略、原始 API 数据）

### 管理后台
访问 `http://localhost:8000/static/admin.html` 使用完整功能：

#### 1. 💬 对话测试
- 实时与 AI 客服对话
- 显示意图识别和置信度
- 支持模型切换（模拟/DeepSeek/GPT 等）

#### 2. 📊 对话日志
- 表格展示所有历史对话
- 支持按评价筛选（全部/好评/差评/普通）
- 每条日志可点赞/点踩
- 实时统计数据显示

#### 3. 📚 知识库管理
- 可视化添加 FAQ
- 支持问题、答案、关键词、分类
- 一键从坏案例导入

#### 4. ⚠️ 坏案例复盘
- 专门收集差评对话
- 快速转化为知识库
- 针对性优化 AI 弱点

#### 5. 📈 数据统计
- 总对话数、好评数、差评数
- 准确率统计
- 坏案例分析（快速转人工、偏离主题、负面情绪等）

---

## 🔧 日常维护

### 每日维护（10-15 分钟）
**早上检查**：
1. 查看服务状态
2. 检查统计数据（准确率是否下降）
3. 浏览新增坏案例

**晚上处理**：
1. 处理当天坏案例（每个 2 分钟）
   - 知识库没有 → 添加到知识库
   - 意图识别错误 → 记录样本准备训练
   - 模型回答质量差 → 优化 Prompt
2. 查看好评对话，总结优秀回答

### 每周维护（1-2 小时）
**周一：数据分析**
- 导出上周日志
- 分析最常见问题和最低准确率意图
- 制定本周优化计划

**周三：知识库更新**
- 批量添加 10-20 条新 FAQ
- 优化现有 FAQ 答案质量

**周五：模型调优**
- 检查意图识别准确率
- 重新训练模型
- 调整 System Prompt

### 每月维护（2-4 小时）
- 月度数据统计与报表
- 清理低质量 FAQ
- 制定下月优化计划
- 数据备份

---

## 📊 关键指标

### 准确率 (Accuracy Rate)
```
公式：好评数 / 总对话数 × 100%

标准：
🟢 优秀：> 90%
🟡 良好：70% - 90%
🔴 需改进：< 70%
```

### 坏案例转化率
```
公式：已优化的坏案例数 / 总坏案例数 × 100%

目标：> 80%
```

---

## 🐛 常见问题

### Q1: 服务无法启动（端口被占用）
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <进程号> /F
```

### Q2: 意图识别不准
- 检查训练数据是否充足（每个意图至少 20 条）
- 确保不同意图之间边界清晰
- 添加易混淆样本的专项训练

### Q3: FAQ 匹配不到
- 增加关键词数量
- 优化关键词质量（使用高频词）
- 考虑同义词、近义词

### Q4: API Key 无效
- 检查 API Key 是否正确
- 检查网络连接
- 查看账户余额
- 切换到模拟模式测试

### Q5: 如何使用 Ollama 本地模型
1. 安装 Ollama：https://ollama.ai
2. 下载模型：`ollama pull qwen2.5:1.5b`
3. 配置 `.env` 文件：
   ```env
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=qwen2.5:1.5b
   USE_OLLAMA=true
   ```
4. 重启服务：`python start.py`

**参考文档**：详见 [OLLAMA 配置说明](OLLAMA_CONFIG.txt)

---

## 📚 文档导航

| 文档 | 说明 | 适合人群 |
|------|------|----------|
| [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md) | 核心技术文档（架构、API、源码分析） | 开发者 |
| [MAINTENANCE_GUIDE.md](MAINTENANCE_GUIDE.md) | 维护手册（日常维护、故障排查） | 运维人员、AI 训练师 |
| [UPDATE_LOG.md](UPDATE_LOG.md) | 更新日志（版本变更记录） | 所有用户 |

---

## 💡 最佳实践

### 新手建议
1. **先跑起来** - 不要纠结配置，先用模拟模式体验
2. **多提问** - 尝试各种问题，观察 AI 反应
3. **看日志** - 后台输出意图识别、策略选择等信息
4. **改代码** - 大胆修改参数和 Prompt，看效果变化

### 优秀 AI 训练师素养
1. **坚持** - 每天都要优化，积少成多
2. **细心** - 每个坏案例都是改进机会
3. **思考** - 不仅解决问题，更要理解问题

---

## 🔗 技术支持

### 获取帮助
- **查看文档**: 优先查阅 docs/ 目录下的文档
- **检查日志**: 终端输出、data/logs/ 目录
- **API 文档**: http://localhost:8000/docs
- **GitHub Issues**: 提交问题反馈

### 学习资源
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [scikit-learn 中文文档](https://scikit-learn.org/stable/)
- [DeepSeek API 文档](https://platform.deepseek.com/api-docs/)

---

## 📄 许可证

本项目仅供学习实践使用。

---

*最后更新：2026 年 3 月 31 日*
