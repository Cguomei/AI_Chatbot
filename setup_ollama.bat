@echo off
echo ========================================
echo 🦙 Ollama 本地模型配置助手
echo ========================================
echo.

:menu
echo.
echo 请选择操作：
echo 1. 检查 Ollama 是否安装
echo 2. 查看已下载的模型
echo 3. 启动 Ollama 服务
echo 4. 测试 Ollama 配置
echo 5. 编辑 .env 文件
echo 6. 退出
echo.

set /p choice=请输入选项 (1-6): 

if "%choice%"=="1" goto check_ollama
if "%choice%"=="2" goto list_models
if "%choice%"=="3" goto start_ollama
if "%choice%"=="4" goto test_config
if "%choice%"=="5" goto edit_env
if "%choice%"=="6" goto end

echo 无效的选项，请重新输入！
goto menu

:check_ollama
echo.
echo 正在检查 Ollama...
ollama --version
if errorlevel 1 (
    echo ❌ Ollama 未安装或未添加到 PATH
    echo 💡 请访问 https://ollama.ai 下载安装
) else (
    echo ✅ Ollama 已安装
)
pause
goto menu

:list_models
echo.
echo 已下载的模型列表：
echo ----------------------------------------
ollama list
if errorlevel 1 (
    echo ❌ 无法获取模型列表，请确保 Ollama 服务正在运行
)
echo.
echo 💡 提示：复制上面的 NAME 列内容，粘贴到 .env 文件的 OLLAMA_MODEL 中
pause
goto menu

:start_ollama
echo.
echo 正在启动 Ollama 服务...
echo 💡 Ollama 会在后台运行，请勿关闭此窗口
start ollama serve
echo ✅ Ollama 服务已启动！
timeout /t 2 /nobreak >nul
goto menu

:test_config
echo.
echo 正在测试 Ollama 配置...
python scripts\test_ollama.py
if errorlevel 1 (
    echo.
    echo ❌ 测试失败，请检查配置
)
pause
goto menu

:edit_env
echo.
echo 正在打开 .env 文件...
notepad .env
echo ✅ 编辑完成！请重启程序使配置生效
pause
goto menu

:end
echo.
echo 👋 再见！
exit /b 0
