# src/report_generator.py

import os
from datetime import date, timedelta
from logger import LOG  # 导入日志模块，用于记录日志信息

from llm import LLM  # 从llm模块导入LLM类，可能用于语言模型相关操作

class ReportGenerator:
    def __init__(self, llm):
        self.llm = llm  # 初始化时接受一个LLM实例，用于后续生成报告

    def generate_daily_report(self, markdown_file_path):
        # 读取Markdown文件并使用LLM生成日报
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        report = self.llm.generate_daily_report(markdown_content)  # 调用LLM生成报告

        report_file_path = os.path.splitext(markdown_file_path)[0] + "_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)  # 写入生成的报告

        LOG.info(f"GitHub 项目报告已保存到 {report_file_path}")

        return report, report_file_path

    def generate_report_by_date_range(self, markdown_file_path, days):
        # 生成特定日期范围的报告，流程与日报生成类似
        with open(markdown_file_path, 'r') as file:
            markdown_content = file.read()

        report = self.llm.generate_daily_report(markdown_content)

        report_file_path = os.path.splitext(markdown_file_path)[0] + f"_report.md"
        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)
        
        LOG.info(f"GitHub 项目报告已保存到 {report_file_path}")

        return report, report_file_path

    def export_hacker_news_daily_progress(self):

        # 构建仓库的日志文件目录
        latest_news_dir = os.path.join('hacker_news', f"{date.today()}")
        os.makedirs(latest_news_dir, exist_ok=True)  # 如果目录不存在则创建
        LOG.info(f"before: ----- {latest_news_dir}")
        report_file_path = latest_news_dir + "_report.md"

        news_content = ""
        # 遍历指定目录下的所有文件和子目录
        for root, dirs, files in os.walk(latest_news_dir):
            for file in files:
                # 获取文件的完整路径
                file_path = os.path.join(root, file)
                # LOG.info(f"file: ----- {file_path}")
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        news_content += f.read() + "\n"  # 添加换行符分隔不同文件内容
                except (UnicodeDecodeError, PermissionError) as e:
                    LOG.error(f"无法读取文件 {file_path}: {e}")

        LOG.info(f"content: ----- {news_content}")

        report = self.llm.generate_hacker_news_daily_report(news_content)  # 调用LLM生成报告

        with open(report_file_path, 'w+') as report_file:
            report_file.write(report)

        return report, report_file_path

if __name__ == "__main__":
    llm = LLM() 
    report_generater = ReportGenerator(llm)
    report_generater.export_hacker_news_daily_progress()
