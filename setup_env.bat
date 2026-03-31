@echo off
echo ========================================
echo 🤖 AI 电商客服 - 环境配置脚本
echo ========================================
echo.

REM 查找 Anaconda 安装路径
set CONDA_PATHS=C:\ProgramData\Anaconda3;C:\Users\%USERNAME%\Anaconda3;C:\Users\%USERNAME%\miniconda3;C:\Program Files\Anaconda3

for %%p in (%CONDA_PATHS%) do (
    if exist "%%p\Scripts\conda.exe" (
        set CONDA_EXE=%%p\Scripts\conda.exe
        goto :found
    )
)

echo ❌ 未找到 Anaconda/Miniconda 安装
echo.
echo 💡 请手动执行以下步骤：
echo.
echo 1. 打开 Anaconda Prompt
echo 2. 运行：conda create -n ai_ecommerce_bot python=3.11 -y
echo 3. 运行：conda activate ai_ecommerce_bot
echo 4. 运行：pip install -r requirements.txt
echo.
pause
goto :eof

:found
echo ✅ 找到 Conda: %CONDA_EXE%
echo.

REM 创建虚拟环境
echo 📦 正在创建虚拟环境 ai_ecommerce_bot (Python 3.11)...
call "%CONDA_EXE%" create -n ai_ecommerce_bot python=3.11 -y
if errorlevel 1 (
    echo ❌ 创建环境失败
    pause
    goto :eof
)

echo.
echo ✅ 虚拟环境创建成功！
echo.
echo 📚 正在安装依赖包...
call "%CONDA_EXE%" run -n ai_ecommerce_bot pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 安装依赖失败
    echo 💡 请手动运行：conda activate ai_ecommerce_bot
    echo    然后运行：pip install -r requirements.txt
    pause
    goto :eof
)

echo.
echo ========================================
echo ✅ 环境配置完成！
echo ========================================
echo.
echo 💡 下次使用时：
echo 1. 打开 Anaconda Prompt
echo 2. 运行：conda activate ai_ecommerce_bot
echo 3. 运行：python start.py
echo.
echo 或者在 PyCharm 中选择这个解释器：
echo    ...ai_ecommerce_bot\python.exe
echo.
pause
