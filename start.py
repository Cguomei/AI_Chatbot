"""
快速启动脚本
"""
import os
import sys

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查 Python 版本
    import sys
    print(f"✅ Python 版本：{sys.version}")
    
    # 检查依赖
    try:
        import fastapi
        import uvicorn
        import requests
        from sklearn.naive_bayes import MultinomialNB
        print("✅ 依赖包已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖包：{e}")
        print("💡 请运行：pip install -r requirements.txt")
        return False
    
    # 检查配置文件
    if not os.path.exists(".env"):
        print("⚠️  未找到 .env 配置文件")
        print("💡 提示：复制 .env.example 为 .env 并配置 API Key")
        print("   （不配置也可以使用模拟模式测试）")
    else:
        print("✅ 配置文件已就绪")
    
    # 检查目录结构
    required_dirs = ["data", "core", "knowledge", "training", "api", "static"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ 缺少目录：{dir_name}")
            return False
    
    print("✅ 目录结构完整")
    return True


def main():
    """主函数"""
    print("="*60)
    print("🤖 AI 智能电商客服系统")
    print("="*60)
    
    if not check_environment():
        print("\n❌ 环境检查失败，请先修复上述问题")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ 环境检查通过，正在启动服务...")
    print("="*60)
    print()
    print("📚 访问以下地址使用系统:")
    print("   - Web 测试界面：http://localhost:8000/static/index.html")
    print("   - API 文档：http://localhost:8000/docs")
    print("   - 健康检查：http://localhost:8000/health")
    print()
    print("💡 提示:")
    print("   - 按 Ctrl+C 停止服务")
    print("   - 修改代码会自动重启（热重载）")
    print()
    
    # 启动服务
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
