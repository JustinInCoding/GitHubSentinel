import smtplib
import markdown2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger import LOG

class Notifier:
    def __init__(self, email_settings):
        self.email_settings = email_settings
    
    def notify(self, repo, report):
        if self.email_settings:
            self.send_email(repo, report)
        else:
            LOG.warning("邮件设置未配置正确，无法发送通知")
    
    def send_email(self, repo, report):
        LOG.info("准备发送邮件")
        msg = MIMEMultipart()
        msg['From'] = self.email_settings['from']
        msg['To'] = self.email_settings['to']
        msg['Subject'] = f"[GitHubSentinel]{repo} 进展简报"
        
        # 将Markdown内容转换为HTML
        html_report = markdown2.markdown(report)

        msg.attach(MIMEText(html_report, 'html'))
        try:
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                LOG.debug("登录SMTP服务器")
                server.login(msg['From'], self.email_settings['password'])
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                LOG.info("邮件发送成功！")
        except Exception as e:
            LOG.error(f"发送邮件失败：{str(e)}")

    def notify_hacker_news_latest(self, report):
        if self.email_settings:
            self.send_hacker_news_report_email(report)
        else:
            LOG.warning("邮件设置未配置正确，无法发送通知")

    def send_hacker_news_report_email(self, report):
        LOG.info("准备发送邮件")
        msg = MIMEMultipart()
        msg['From'] = self.email_settings['from']
        msg['To'] = self.email_settings['to']
        msg['Subject'] = f"[Hacker News] 今日最热"
        
        # 将Markdown内容转换为HTML
        html_report = markdown2.markdown(report)

        msg.attach(MIMEText(html_report, 'html'))
        try:
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                LOG.debug("登录SMTP服务器")
                server.login(msg['From'], self.email_settings['password'])
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                LOG.info("邮件发送成功！")
        except Exception as e:
            LOG.error(f"发送邮件失败：{str(e)}")

if __name__ == '__main__':
    from config import Config
    config = Config()
    notifier = Notifier(config.email)

#     test_repo = "DjangoPeng/openai-quickstart"
#     test_report = """
# # DjangoPeng/openai-quickstart 项目进展

# ## 时间周期：2024-08-24

# ## 新增功能
# - Assistants API 代码与文档

# ## 主要改进
# - 适配 LangChain 新版本

# ## 修复问题
# - 关闭了一些未解决的问题。

# """
#     notifier.notify(test_repo, test_report)

    test_report = """
## Hacker News 最新热度报告（2025年6月21日）

### 1. AbsenceBench: 语言模型无法识别缺失信息（4次重复）
标题：语言模型的认知局限性研究
描述：arXiv论文指出当前语言模型存在"缺失信息盲区"，当关键信息被省略时，模型仍会自信地生成错误答案。研究团队构建了包含1.2万条刻意省略信息的测试集，GPT-4等主流模型准确率不足30%（论文链接）。

### 2. Phoenix.new AI运行时（4次重复）
标题：Fly.io推出Phoenix框架专用AI运行时
描述：该服务允许开发者在Phoenix Web框架中无缝集成AI功能，支持自动扩缩容和GPU加速。实测显示处理AI推理请求的延迟降低60%，现已在Fly.io平台开放测试（博客链接）。

### 3. Harper语法检查工具（4次重复）
标题：开源的Grammarly替代品
描述：Harper提供实时语法修正、风格建议等功能，支持Markdown和LaTeX。与Grammarly相比突出隐私保护，所有处理在本地完成。测试版已支持VS Code等编辑器（官网链接）。

### 4. AMD MI350架构解析（3次重复）
标题：AMD首席架构师深度访谈
描述：新一代MI350 GPU采用3D堆叠技术，晶体管密度提升40%。特别优化了矩阵运算单元，在Llama-70B推理任务中较上代快2.3倍。预计2025Q4量产（访谈链接）。

### 5. YouTube反广告拦截措施（3次重复）
标题：平台与用户的技术对抗升级
描述：YouTube最新检测机制导致部分广告拦截器失效，用户报告视频加载延迟增加35%。官方回应称这是维持服务的必要措施（技术分析链接）。

### 6. 维基百科随机广播（3次重复）
标题：用听觉探索知识图谱
描述：Wiki Radio算法将维基条目转化为语音流，每小时随机组合6种语言的内容。后台使用GPT-4生成内容摘要，已收录超过200万条词条（体验链接）。

### 7. 宫崎骏《风之谷》战争生态学（3次重复）
标题：动画中的环境警示预言
描述：研究指出该作品精准预测了生物武器导致的生态链崩溃。对比切尔诺贝利禁区现状，发现与片中"腐海"生态系统有79%相似性（论文链接）。

### 8. Nxtscape智能浏览器（3次重复）
标题：开源自动化浏览工具
描述：支持通过自然语言指令自动完成表单填写、数据抓取等任务。采用React+WebAssembly架构，扩展系统允许注入Python脚本（GitHub链接）。

### 9. MSI安装包浏览器工具（3次重复）
标题：Web端MSI文件解析方案
描述：基于PyMSI库开发，可直接在浏览器中查看MSI安装包的内部文件结构和注册表修改。相比传统工具加载速度快4倍（文档链接）。

### 10. 20亿年前天然核反应堆（3次重复）
标题：加蓬奥克洛铀矿的物理奇迹
描述：IAEA报告详细分析了该铀矿中自然形成的17处核裂变区，其运行机制为现代核废料处理提供了新思路（完整报告链接）。
"""
    notifier.notify_hacker_news_latest(test_report)
