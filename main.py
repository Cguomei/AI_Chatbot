"""
AI 电商客服 - 主程序入口

文档维护说明：
- 项目文档位于 docs/ 目录
- README.md - 快速开始和使用指南
- TECHNICAL_DOCS.md - 核心技术文档和 API 说明
- MAINTENANCE_GUIDE.md - 日常维护和故障排查
- UPDATE_LOG.md - 版本更新记录

开发时请同步更新相关文档
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router as chat_router

app = FastAPI(
    title="AI 智能电商客服",
    description="学习用 AI 电商客服系统",
    version="0.1.0"
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(chat_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "欢迎使用 AI 智能电商客服系统",
        "docs": "/docs",
        "chat": "/api/chat"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    print("🤖 AI 智能电商客服系统启动中...")
    print("🤖 访问 http://localhost:8000 查看欢迎页面")
    print("🤖 访问 http://localhost:8000/health 查看健康检查接口")
    print("📚 访问 http://localhost:8000/static 查看静态文件")
    print("📚 访问 http://localhost:8000/api 查看 API 接口")
    print("📚 访问http://localhost:8000/static/console.html ")
    print("📚 访问 http://localhost:8000/docs 查看 API 文档")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    print("🤖 AI 智能电商客服系统已启动")
