#!/usr/bin/env python3
"""
快速启动脚本 - 支持局域网分享
    python start_server.py          # 仅本机访问
    python start_server.py --lan    # 局域网访问 (0.0.0.0)
    python start_server.py -p 8080  # 指定端口
"""

import socket
import sys


def get_local_ip():
    """获取本机局域网 IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    import uvicorn

    def safe_print(msg, fallback=""):
        """安全打印，字符编码崩溃时用 fallback"""
        try:
            print(msg)
        except (UnicodeEncodeError, UnicodeDecodeError):
            if fallback:
                print(fallback)

    # ====== 全局错误捕获，避免闪退 ======
    exit_code = 0
    try:
        from main import app

        # 解析参数：exe 模式默认局域网，开发模式默认本机
        is_frozen = getattr(sys, 'frozen', False)
        host = "0.0.0.0" if is_frozen else "127.0.0.1"
        port = 8000
        for i, arg in enumerate(sys.argv):
            if arg == "--lan":
                host = "0.0.0.0"
            elif arg == "--local":
                host = "127.0.0.1"
            elif arg == "-p" and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])

        local_ip = get_local_ip()

        safe_print("=" * 50)
        safe_print("  [Board Game] 桌游排行系统", "  Board Game Ranking System")
        safe_print("=" * 50)
        safe_print(f"  本机访问: http://127.0.0.1:{port}")
        safe_print(f"  局域网访问: http://{local_ip}:{port}", f"  LAN: http://{local_ip}:{port}")
        safe_print(f"  管理后台: http://127.0.0.1:{port}/admin", f"  Admin: http://127.0.0.1:{port}/admin")
        safe_print(f"  默认账号: admin / admin123", f"  Account: admin / admin123")
        safe_print("-" * 50)
        safe_print("  按 Ctrl+C 停止服务", "  Ctrl+C to stop")
        safe_print("=" * 50)

        uvicorn.run(app, host=host, port=port, log_level="warning")

    except SystemExit:
        pass
    except KeyboardInterrupt:
        safe_print("\n  已停止。")
    except Exception as e:
        # ====== 出错了！打印错误并停住窗口 ======
        safe_print("\n" + "=" * 50)
        safe_print("  [错误] 启动失败 !!!", "  [ERROR] Failed to start !!!")
        safe_print("=" * 50)
        safe_print(f"  原因: {e}")
        # 尝试用 ascii 安全打印 traceback
        try:
            import traceback
            tb_text = traceback.format_exc()
            safe_print(tb_text)
        except Exception:
            # 连 traceback 都打不了，用最朴素的方式
            print(f"\n  Error: {e}\n  File: {__file__}")
            # 也写入一个错误文件，方便排查
            try:
                with open(os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__), "error_log.txt"), "w", encoding="utf-8") as f:
                    f.write(str(e))
            except:
                pass
        safe_print("-" * 50)
        safe_print("  常见原因:", "  Common causes:")
        safe_print("  1. 端口 8000 被其他程序占用了")
        safe_print("  2. 杀毒软件拦截了网络访问")
        safe_print("  3. 文件权限不足")
        safe_print("=" * 50)
        exit_code = 1
    finally:
        # ====== 关键：停住窗口让用户能看到错误信息 ======
        if exit_code != 0:
            try:
                input("\n  按 Enter 键退出...")
            except (EOFError, KeyboardInterrupt):
                pass
        
    sys.exit(exit_code)
