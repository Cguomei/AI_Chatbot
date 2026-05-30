"""
开发模式启动 - 自动重载 + 局域网访问
    python run_server.py
"""
if __name__ == "__main__":
    import uvicorn
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "127.0.0.1"

    try:
        print("=" * 50)
        print("  🎮  桌游排行 - 开发模式")
        print("=" * 50)
        print(f"  本机: http://127.0.0.1:8000")
        print(f"  局域网: http://{ip}:8000")
        print(f"  管理后台账号: admin / admin123")
        print("-" * 50)
    except UnicodeEncodeError:
        print("=" * 50)
        print("  Board Game Ranking - Dev Mode")
        print("=" * 50)
        print(f"  Local: http://127.0.0.1:8000")
        print(f"  LAN:   http://{ip}:8000")
        print(f"  Admin: admin / admin123")
        print("-" * 50)

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
