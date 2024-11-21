@echo off
echo 正在启动PDF翻译程序...

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请确保已安装Python并添加到系统环境变量中
    pause
    exit /b
)

:: 检查pdf2zh是否安装
python -c "import pdf2zh" >nul 2>&1
if errorlevel 1 (
    echo 正在安装pdf2zh...
    pip install pdf2zh
)

:: 启动程序
python main.py

pause