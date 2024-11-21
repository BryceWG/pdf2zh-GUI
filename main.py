import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QFileDialog, QLabel, QComboBox, QLineEdit, QMessageBox, QProgressBar
)
from PyQt5.QtCore import QProcess
from plyer import notification

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF2ZH GUI")
        self.resize(600, 400)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        
        # 配置文件路径改为程序同级目录
        self.config_file = os.path.join(os.path.dirname(__file__), "pdf2zh_config.json")
        
        # UI组件
        self.pdf_files = []
        self.save_path = ""
        self.service_providers = ["Google", "DeepL", "Ollama", "OpenAI", "Azure"]
        self.selected_service = ""
        self.model_name = ""
        
        # 加载上次的配置
        self.load_config()
        
        # 设计布局
        self.setup_ui()
        
        # 进程对象
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)  # 合并标准输出和错误输出
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.finished.connect(self.translation_finished)

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 保存配置数据
                    self.selected_service = config.get('service', '')
                    self.model_name = config.get('model', '')
                    self.thread_count = config.get('thread', '')
                    self.src_lang = config.get('src_lang', '')
                    self.tgt_lang = config.get('tgt_lang', '')
                    
                    # 在setup_ui之后应用配置
                    self.apply_config = True
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            self.apply_config = False

    def apply_loaded_config(self):
        """应用已加载的配置到UI组件"""
        if not hasattr(self, 'apply_config') or not self.apply_config:
            return
            
        # 设置服务商
        if self.selected_service:
            index = self.service_combo.findText(self.selected_service)
            if index >= 0:
                self.service_combo.setCurrentIndex(index)
                
        # 设置模型名称
        if self.model_name:
            self.model_input.setText(self.model_name)
            
        # 设置线程数
        if self.thread_count:
            self.thread_input.setText(str(self.thread_count))
            
        # 设置源语言和目标语言
        if self.src_lang:
            self.src_lang_input.setText(self.src_lang)
        if self.tgt_lang:
            self.tgt_lang_input.setText(self.tgt_lang)

    def save_config(self):
        try:
            config = {
                'service': self.selected_service,
                'model': self.model_input.text(),
                'thread': self.thread_input.text(),
                'src_lang': self.src_lang_input.text(),
                'tgt_lang': self.tgt_lang_input.text()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")

    def setup_ui(self):
        # 选择PDF文件按钮
        self.select_pdf_button = QPushButton("选择PDF文件")
        self.select_pdf_button.clicked.connect(self.select_pdf_files)
        self.layout.addWidget(self.select_pdf_button)

        # 显示选择的PDF文件
        self.pdf_label = QLabel("选择的PDF文件：")
        self.layout.addWidget(self.pdf_label)

        # 选择保存位置按钮
        self.select_save_button = QPushButton("选择保存位置")
        self.select_save_button.clicked.connect(self.select_save_path)
        self.layout.addWidget(self.select_save_button)

        # 显示保存位置
        self.save_label = QLabel("保存位置：")
        self.layout.addWidget(self.save_label)

        # 选择翻译服务商
        self.service_label = QLabel("选择翻译服务商：")
        self.layout.addWidget(self.service_label)
        self.service_combo = QComboBox()
        self.service_combo.addItems(self.service_providers)
        self.service_combo.currentIndexChanged.connect(self.update_model_input)
        self.layout.addWidget(self.service_combo)

        # 模型输入框
        self.model_label = QLabel("模型名称：") 
        self.model_label.setVisible(False)
        self.layout.addWidget(self.model_label)
        self.model_input = QLineEdit()
        self.model_input.setVisible(False)
        self.layout.addWidget(self.model_input)
        
        # 高级选项
        self.advanced_label = QLabel("高级选项：")
        self.layout.addWidget(self.advanced_label)
        
        # 线程数设置
        self.thread_label = QLabel("线程数：")
        self.layout.addWidget(self.thread_label)
        self.thread_input = QLineEdit()
        self.thread_input.setPlaceholderText("默认为1")
        self.layout.addWidget(self.thread_input)
        
        # 页码范围
        self.pages_label = QLabel("页码范围：")
        self.layout.addWidget(self.pages_label)
        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("例如: 1-3,5")
        self.layout.addWidget(self.pages_input)
        
        # 源语言和目标语言
        self.src_lang_label = QLabel("源语言：")
        self.layout.addWidget(self.src_lang_label)
        self.src_lang_input = QLineEdit()
        self.src_lang_input.setPlaceholderText("例如: en")
        self.layout.addWidget(self.src_lang_input)
        
        self.tgt_lang_label = QLabel("目标语言：")
        self.layout.addWidget(self.tgt_lang_label)
        self.tgt_lang_input = QLineEdit()
        self.tgt_lang_input.setPlaceholderText("例如: zh") 
        self.layout.addWidget(self.tgt_lang_input)

        # 操作提示按钮
        self.info_button = QPushButton("操作提示")
        self.info_button.clicked.connect(self.show_info)
        self.layout.addWidget(self.info_button)

        # 开始翻译按钮
        self.start_button = QPushButton("开始翻译")
        self.start_button.clicked.connect(self.start_translation)
        self.layout.addWidget(self.start_button)

        # 文件总进度条
        self.total_progress_label = QLabel("总体进度：")
        self.layout.addWidget(self.total_progress_label)
        self.total_progress_bar = QProgressBar()
        self.total_progress_bar.setVisible(False)
        self.layout.addWidget(self.total_progress_bar)

        # 当前文件进度条
        self.current_progress_label = QLabel("当前文件进度：")
        self.layout.addWidget(self.current_progress_label)
        self.current_progress_bar = QProgressBar()
        self.current_progress_bar.setVisible(False)
        self.layout.addWidget(self.current_progress_bar)
        
        # 进度详情标签
        self.progress_detail_label = QLabel("")
        self.layout.addWidget(self.progress_detail_label)

        # 在所有UI组件创建完成后应用配置
        self.apply_loaded_config()

    def select_pdf_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择PDF文件", "", "PDF Files (*.pdf)")
        if files:
            self.pdf_files = files
            self.pdf_label.setText(f"选择的PDF文件：{', '.join(self.pdf_files)}")
            
            # 自动设置保存位置为第一个PDF文件所在目录
            default_save_path = os.path.dirname(self.pdf_files[0])
            self.save_path = default_save_path
            self.save_label.setText(f"保存位置：{self.save_path}")

    def select_save_path(self):
        # 如果已有PDF文件，则从PDF文件所在目录开始选择
        start_dir = os.path.dirname(self.pdf_files[0]) if self.pdf_files else ""
        path = QFileDialog.getExistingDirectory(self, "选择保存位置", start_dir)
        if path:
            self.save_path = path
            self.save_label.setText(f"保存位置：{self.save_path}")

    def update_model_input(self, index):
        self.selected_service = self.service_combo.currentText()
        
        # 只有OpenAI和Ollama需要显示模型输入
        if self.selected_service in ["OpenAI", "Ollama"]:
            self.model_label.setVisible(True)
            self.model_input.setVisible(True)
            
            # 设置默认模型提示
            if self.selected_service == "OpenAI":
                self.model_input.setPlaceholderText("例如: gpt-4o-mini")
            else:
                self.model_input.setPlaceholderText("例如: gemma2") 
        else:
            self.model_label.setVisible(False)
            self.model_input.setVisible(False)

    def show_info(self):
        QMessageBox.information(
            self, "操作提示",
            "步骤：\n"
            "1. 选择要翻译的PDF文件\n"
            "2. 选择翻译后的文件保存位置\n"
            "3. 选择翻译服务商\n"
            "4. 确保已设置相应的系统环境变量:\n"
            "   - OpenAI: OPENAI_API_KEY\n"
            "   - OpenAI: OPENAI_BASE_URL\n"
            "   - DeepL: DEEPL_AUTH_KEY\n"
            "   - Azure: AZURE_APIKEY, AZURE_ENDPOINT, AZURE_REGION\n"
            "5. 点击开始翻译按钮\n"
            "6. 查看翻译进度\n"
            "\n"
            "注意：确保API Key已经在系统环境变量中正确设置，并且网络连接正常。"
        )

    def start_translation(self):
        if not self.pdf_files:
            QMessageBox.warning(self, "错误", "请选择至少一个PDF文件。")
            return
        if not self.save_path:
            QMessageBox.warning(self, "错误", "请选择保存位置。")
            return
            
        try:
            # 保存当前配置
            self.save_config()
            
            # 构造命令行命令
            command = ["pdf2zh"]
            
            # 添加PDF文件路径
            for pdf in self.pdf_files:
                command.append(pdf)  # 不需要引号
            
            # 添加服务商和模型
            if self.selected_service in ["OpenAI", "Ollama"] and self.model_input.text():
                command.extend(["--service", f"{self.selected_service.lower()}:{self.model_input.text()}"])
            else:
                command.extend(["--service", self.selected_service.lower()])
                
            # 添加高级选项
            if self.thread_input.text():
                command.extend(["--thread", self.thread_input.text()])
            if self.pages_input.text():
                command.extend(["--pages", self.pages_input.text()])
            if self.src_lang_input.text():
                command.extend(["--lang-in", self.src_lang_input.text()])
            if self.tgt_lang_input.text():
                command.extend(["--lang-out", self.tgt_lang_input.text()])
            
            self.process.setWorkingDirectory(self.save_path)

            print(f"执行命令: {' '.join(command)}")  # 调试用

            # 设置进度条和状态
            self.current_file_index = 0
            self.total_progress_bar.setVisible(True)
            self.current_progress_bar.setVisible(True)
            self.total_progress_bar.setValue(0)
            self.current_progress_bar.setValue(0)
            self.total_progress_bar.setMaximum(len(self.pdf_files))
            self.progress_detail_label.setText("正在解析PDF文件...")
            
            # 禁用开始按钮，防止重复点击
            self.start_button.setEnabled(False)
            
            # 启动翻译进程
            self.process.start(command[0], command[1:])
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动翻译进程失败：{str(e)}")
            self.start_button.setEnabled(True)
            self.total_progress_bar.setVisible(False)
            self.current_progress_bar.setVisible(False)
            self.progress_detail_label.setText("")

    def handle_output(self):
        try:
            output = self.process.readAllStandardOutput().data().decode('gbk', errors='ignore')
            print(f"输出: {output}")  # 调试用
            
            # 检测到进度条开始时更新状态
            if "|" in output and "[" in output and "]" in output:
                try:
                    # 提取百分比
                    percent_str = output.split("|")[0].strip().replace("%", "")
                    if percent_str:
                        percent = float(percent_str)
                        self.current_progress_bar.setValue(int(percent))
                        
                        # 如果是第一次看到进度条，更新状态文本
                        if self.progress_detail_label.text() == "正在解析PDF文件...":
                            self.progress_detail_label.setText("正在翻译PDF文件...")
                        
                        # 提取时间信息
                        time_info = output.split("[")[1].split("]")[0]
                        if "<" in time_info:
                            elapsed, remaining = time_info.split("<")
                            speed = output.split(",")[-1].strip()
                            self.progress_detail_label.setText(
                                f"正在翻译PDF文件...\n"
                                f"已用时间: {elapsed.strip()}, "
                                f"预计剩余: {remaining.strip()}, "
                                f"速度: {speed}"
                            )
                except Exception as e:
                    print(f"解析进度失败: {str(e)}")
                    
            # 检查文件完成
            if "100%" in output:
                self.current_progress_bar.setValue(100)
                self.current_file_index += 1
                self.total_progress_bar.setValue(self.current_file_index)
                
        except Exception as e:
            print(f"处理输出时发生异常: {str(e)}")

    def translation_finished(self, exit_code, exit_status):
        self.start_button.setEnabled(True)
        
        if exit_code == 0:
            self.current_progress_bar.setValue(100)
            self.total_progress_bar.setValue(len(self.pdf_files))
            self.progress_detail_label.setText("翻译完成！")
            
            # 发送系统通知
            try:
                notification.notify(
                    title="PDF翻译完成",
                    message=f"已完成 {len(self.pdf_files)} 个文件的翻译\n保存位置: {self.save_path}",
                    app_icon=None,  # 可以设置自定义图标
                    timeout=5  # 显示时间（秒）
                )
            except Exception as e:
                print(f"发送通知失败: {str(e)}")
            
            QMessageBox.information(self, "完成", "翻译任务已完成。")
        else:
            error_message = f"翻译任务失败，退出代码：{exit_code}\n"
            error_message += "请检查：\n1. 环境变量是否正确设置\n2. 网络连接是否正常\n3. PDF文件是否可访问"
            QMessageBox.critical(self, "错误", error_message)
            
            # 发送失败通知
            try:
                notification.notify(
                    title="PDF翻译失败",
                    message="请检查环境变量、网络连接和文件访问权限",
                    app_icon=None,
                    timeout=5
                )
            except Exception as e:
                print(f"发送通知失败: {str(e)}")
            
        self.current_progress_bar.setVisible(False)
        self.total_progress_bar.setVisible(False)
        self.progress_detail_label.setText("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())