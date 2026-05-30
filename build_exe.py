"""
桌游排行 - 打包为 EXE
生成: 桌游排行-v{version}.exe (带自定义图标)

使用方法:
    pip install pyinstaller pillow
    python build_exe.py
"""

import os, sys, subprocess

APP_NAME = "桌游排行"
VERSION = "1.0.14"
EXE_NAME = f"{APP_NAME}-v{VERSION}"

def step(msg):
    print("")
    print("=" * 50)
    print(f"  {msg}")
    print("=" * 50)

# ---- 1. 生成图标 ----
step("生成图标 icon.ico")
if not os.path.exists("icon.ico"):
    subprocess.run([sys.executable, "generate_icon.py"], check=True)
else:
    print("icon.ico 已存在，跳过生成")

# ---- 2. 打包 ----
step(f"PyInstaller 打包 -> {EXE_NAME}.exe")

# 收集数据文件
datas = []
# 模板文件
if os.path.isdir("templates"):
    for root, dirs, files in os.walk("templates"):
        for f in files:
            src = os.path.join(root, f)
            dst_dir = os.path.relpath(root)
            datas.append(f"{src};{dst_dir}")

# 静态文件
if os.path.isdir("static"):
    for root, dirs, files in os.walk("static"):
        for f in files:
            src = os.path.join(root, f)
            dst_dir = os.path.relpath(root)
            datas.append(f"{src};{dst_dir}")

# db 目录（空目录也需要）
if os.path.isdir("db"):
    for f in os.listdir("db"):
        if f.endswith(".db"):
            datas.append(f"db/{f};db")

# 日志目录
if os.path.isdir("logs"):
    pass  # 日志目录运行时动态创建

# 构建 PyInstaller 命令
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--console",
    f"--name={EXE_NAME}",
    "--icon=icon.ico",
    "--clean",
    "--noconfirm",
]

for d in datas:
    cmd.append(f"--add-data={d}")

# 隐藏导入
cmd += [
    "--hidden-import=uvicorn.logging",
    "--hidden-import=uvicorn.loops",
    "--hidden-import=uvicorn.loops.auto",
    "--hidden-import=uvicorn.protocols",
    "--hidden-import=uvicorn.protocols.http",
    "--hidden-import=uvicorn.protocols.http.auto",
    "--hidden-import=uvicorn.protocols.websockets",
    "--hidden-import=uvicorn.protocols.websockets.auto",
    "--hidden-import=uvicorn.lifespan",
    "--hidden-import=uvicorn.lifespan.on",
    "--hidden-import=jinja2.ext",
    "--hidden-import=openpyxl",
    "--collect-all=pyngrok",
]

cmd.append("main.py")

print(" ".join(cmd))
subprocess.run(cmd, check=True)

# ---- 3. 输出信息 ----
step("打包完成")
dist_dir = "dist"
exe_path = os.path.join(dist_dir, f"{EXE_NAME}.exe")
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"  EXE: {exe_path}")
    print(f"  Size: {size_mb:.1f} MB")

    # 复制说明书到 dist
    import shutil
    manual_src = "使用说明.txt"
    manual_dst = os.path.join(dist_dir, "使用说明.txt")
    if os.path.exists(manual_src):
        shutil.copy2(manual_src, manual_dst)
        print(f"  Manual: {manual_dst}")

    print(f"\n  Double-click to run, open http://127.0.0.1:8000")
    print(f"  Admin: admin / admin123")
else:
    print("  ERROR: EXE not found, check build log above")
