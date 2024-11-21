# PDF翻译程序

一个基于 pdf2zh 的 PDF 文档翻译工具，提供图形用户界面。

## 功能特点

- 📚 支持批量翻译 PDF 文件
- 🌐 支持多种翻译服务：Google、DeepL、Ollama、OpenAI、Azure
- 📊 保留公式、图表、目录和注释
- 🚀 支持多线程翻译
- 💾 自动保存配置
- 📢 翻译完成系统通知

## 安装要求

- Python 3.8-3.12
- pdf2zh
- PyQt5
- plyer (用于系统通知)

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python main.py
```
或直接运行`PDF2ZH.bat`

## 使用说明

1. 选择要翻译的 PDF 文件
2. 选择保存位置
3. 选择翻译服务商
4. 设置相应的环境变量：
   - OpenAI: OPENAI_API_KEY, OPENAI_BASE_URL
   - DeepL: DEEPL_AUTH_KEY
   - Azure: AZURE_APIKEY, AZURE_ENDPOINT, AZURE_REGION
5. 点击开始翻译

## 高级选项

- 线程数：设置翻译使用的线程数
- 页码范围：指定要翻译的页码范围（例如：1-3,5）
- 源语言：指定源文档语言（默认：en）
- 目标语言：指定目标语言（默认：zh）

## 许可证

本项目基于 GNU Affero General Public License v3.0 开源。([1](https://github.com/Byaidu/PDFMathTranslate/blob/main/LICENSE))

## 致谢

本项目基于 [PDFMathTranslate](https://github.com/Byaidu/PDFMathTranslate) 开发，是它的图形化界面版本。