"""
修复 main.py:
1. 添加启动崩溃日志（从第1行就开始写文件）
2. 移除重复的 __main__ 块（保留第1个）
3. 增强启动块: 每步写日志 + 全局异常钩子
"""
import re, os

path = os.path.join(os.path.dirname(__file__) or ".", "main.py")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# ========== 1. 在文件最前面插入崩溃日志工具 ==========
crash_header = '''# ==================== 启动崩溃日志（最优先，在一切import之前） ====================
import os as _os, sys as _sys, traceback as _tb, datetime as _dt

def _crash_log(msg):
    try:
        if getattr(_sys, "frozen", False):
            d = _os.path.dirname(_sys.executable)
        else:
            d = _os.path.dirname(_os.path.abspath(__file__))
        with open(_os.path.join(d, "crash.log"), "a", encoding="utf-8") as f:
            f.write(f"{_dt.datetime.now().isoformat()} {msg}\\n")
            f.flush()
    except:
        pass

try:
    _crash_log("=== STARTUP BEGIN ===")
    _crash_log(f"frozen={getattr(_sys, 'frozen', False)}, argv={_sys.argv}, cwd={_os.getcwd()}")
except:
    pass

# 全局未捕获异常 => 写入 crash.log
_orig_hook = _sys.excepthook
def _crash_hook(typ, val, tb):
    _crash_log(f"UNHANDLED: {typ.__name__}: {val}")
    _crash_log("".join(_tb.format_tb(tb)))
    if _orig_hook:
        _orig_hook(typ, val, tb)
_sys.excepthook = _crash_hook

'''

content = crash_header + content

# ========== 2. 删除重复的 __main__ 块 ==========
# 找到所有完整块（从注释头到 sys.exit）
found = list(re.finditer(
    r'^(# ==================== EXE 启动入口 ====================.*?^    sys\.exit\(exit_code\)\n)',
    content, re.MULTILINE | re.DOTALL
))
print(f"Found {len(found)} startup blocks, removing {len(found)-1} duplicates...")

# 从后往前删，保留第1个
for m in reversed(found[1:]):
    content = content[:m.start()] + content[m.end():]

# ========== 3. 增强第1个启动块 ==========
# 在 uvicorn.run 前插入日志
content = content.replace(
    "        import uvicorn\n        uvicorn.run(app, host=host, port=port, log_level=\"warning\")",
    '        _crash_log("init: importing uvicorn...")\n        import uvicorn\n        _crash_log(f"init: uvicorn.run(app, host={host}, port={port})")\n        uvicorn.run(app, host=host, port=port, log_level="warning")'
)

# 在 except 中写 crash.log
content = content.replace(
    '    except Exception as e:\n        safe_print("")\n        safe_print("=" * 50)\n        safe_print("  ERROR: Failed to start !")\n        safe_print("=" * 50)\n        safe_print(f"  {e}")',
    '    except Exception as e:\n        _crash_log(f"FATAL: {e}")\n        _crash_log(_tb.format_exc())\n        safe_print("")\n        safe_print("=" * 50)\n        safe_print("  ERROR: Failed to start !")\n        safe_print("=" * 50)\n        safe_print(f"  {e}")'
)

# ========== 4. 写入 ==========
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

# ========== 5. 验证 ==========
count = content.count('if __name__ == "__main__":')
print(f"Remaining __main__ blocks: {count}")
assert count == 1, f"FAIL: expected 1, got {count}"
print("Done! main.py fixed.")
