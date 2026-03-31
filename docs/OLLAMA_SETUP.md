# Ollama 本地模型配置指南

## 📦 快速开始

### 1. 确认 Ollama 已安装并运行

```bash
# 检查 Ollama 是否安装
ollama --version

# 启动 Ollama 服务（如果未运行）
ollama serve
```

### 2. 查看已下载的模型

```bash
# 列出所有已下载的模型
ollama list
```

你会看到类似这样的输出：
```
NAME            ID           SIZE      MODIFIED
qwen:7b         a634545505c0 4.5 GB    2 days ago
llama2          78e2601ac742 3.8 GB    1 week ago
gemma:7b        22f8de8739a2 5.0 GB    2 weeks ago
```

### 3. 配置 .env 文件

编辑项目根目录的 `.env` 文件：

```env
# Ollama 本地模型配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen:7b  # 替换为你的模型名称（从 ollama list 获取）
USE_OLLAMA=true       # 设置为 true 启用 Ollama
```

**重要：**
- `OLLAMA_MODEL` 必须与 `ollama list` 中显示的 NAME 完全一致
- `USE_OLLAMA=true` 才会启用本地模型，否则使用 DeepSeek 或模拟模式

### 4. 测试配置

运行测试脚本：

```bash
python scripts/test_ollama.py
```

如果看到 "✅ 测试成功！"，说明配置正确！

### 5. 在主程序中使用

现在运行你的客服机器人，它会自动使用 Ollama 本地模型：

```bash
python main.py
```

## 🔧 常见问题

### Q1: "Ollama API 调用失败：Connection refused"
**解决：** Ollama 服务未运行，执行 `ollama serve`

### Q2: "模型未找到"
**解决：** 
1. 检查 `.env` 中的 `OLLAMA_MODEL` 是否正确
2. 下载模型：`ollama pull qwen:7b`（替换为你的模型名）

### Q3: 响应速度很慢
**解决：** 
- 本地模型对硬件要求较高，确保有足够内存（7B 模型至少需要 8GB 内存）
- 考虑使用更小的模型（如 qwen:1.8b、phi:2.7b）

### Q4: 如何在 Ollama 和 DeepSeek 之间切换？
**解决：**
- 使用 Ollama：设置 `USE_OLLAMA=true`
- 使用 DeepSeek：设置 `USE_OLLAMA=false` 并配置 `DEEPSEEK_API_KEY`

## 📊 支持的模型

Ollama 支持多种开源模型，常用的有：

| 模型名称 | 大小 | 特点 | 推荐配置 |
|---------|------|------|---------|
| qwen:7b | 7B | 中文支持好，适合客服 | 8GB+ 内存 |
| llama2:7b | 7B | 通用性强 | 8GB+ 内存 |
| gemma:7b | 7B | Google 出品，质量高 | 8GB+ 内存 |
| phi:2.7b | 2.7B | 轻量级，速度快 | 4GB+ 内存 |
| mistral:7b | 7B | 性能优秀 | 8GB+ 内存 |

下载模型示例：
```bash
ollama pull qwen:7b
ollama pull llama2
ollama pull phi
```

## 🎯 性能优化建议

1. **使用 GPU 加速**（如果有 NVIDIA 显卡）
   - Ollama 会自动使用 GPU，无需额外配置

2. **调整温度参数**
   - 在 `.env` 中修改 `TEMPERATURE`（0-1 之间）
   - 越低越保守，越高越有创造性

3. **批量下载模型**
   ```bash
   ollama pull qwen:7b
   ollama pull llama2
   ollama pull gemma:7b
   ```

## 📝 注意事项

- ⚠️ 本地模型需要较多内存和 CPU 资源
- ⚠️ 首次运行会加载模型，可能需要几秒到几十秒
- ⚠️ 确保 Ollama 版本是最新的：`ollama --version`
- ✅ 本地模型完全免费，无需 API Key
- ✅ 数据完全本地，保护隐私

## 🔗 相关资源

- Ollama 官网：https://ollama.ai
- Ollama 模型库：https://ollama.ai/library
- 项目文档：docs/README.md
