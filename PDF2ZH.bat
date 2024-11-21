@echo off
chcp 65001 > nul
echo 正在启动PDF翻译程序...

:: 检查Python版本 (3.8-3.12)
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python，请确保已安装Python并添加到系统环境变量中
    pause
    exit /b
)

for /f "tokens=2" %%I in ('python --version 2^>^&1') do (
    set PYTHON_VERSION=%%I
)
echo 检测到Python版本: %PYTHON_VERSION%

:: 检查pdf2zh是否安装
python -c "import pdf2zh" >nul 2>&1
if errorlevel 1 (
    echo 正在安装pdf2zh...
    pip install pdf2zh
    if errorlevel 1 (
        echo 错误：安装pdf2zh失败
        pause
        exit /b
    )
)

:: 检查PyQt5是否安装
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyQt5...
    pip install PyQt5
    if errorlevel 1 (
        echo 错误：安装PyQt5失败
        pause
        exit /b
    )
)

:: 检查plyer是否安装
python -c "import plyer" >nul 2>&1
if errorlevel 1 (
    echo 正在安装plyer...
    pip install plyer
    if errorlevel 1 (
        echo 错误：安装plyer失败
        pause
        exit /b
    )
)

:: 检查配置文件
if not exist "pdf2zh_config.json" (
    echo 提示：未检测到配置文件，将在首次使用时创建
)

:: 启动程序
echo 正在启动程序...
python main.py

if errorlevel 1 (
    echo 程序异常退出，错误代码：%errorlevel%
    pause
    exit /b
)

pause