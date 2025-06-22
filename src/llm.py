import json
import requests
from logger import LOG  # 导入日志模块

class LLM:

    def __init__(self, config):
        """
        初始化 LLM 类，根据配置选择使用的模型（OpenAI 或 Ollama）。
        
        :param config: 配置对象，包含所有的模型配置参数。
        """
        self.config = config
        self.model = config.llm_model_type.lower()  # 获取模型类型并转换为小写
        if self.model == "openai":
            from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
            self.client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从环境变量中获取OpenAI API密钥
                base_url="https://api.deepseek.com/v1"  # OpenAI API的基础URL 
            )  # 创建OpenAI客户端实例
        elif self.model == "ollama":
            self.api_url = config.ollama_api_url  # 设置Ollama API的URL
        else:
            raise ValueError(f"Unsupported model type: {self.model}")  # 如果模型类型不支持，抛出错误
        
        # 从TXT文件加载系统提示信息ork/chapter05
        with open("prompts/report_prompt.txt", "r", encoding='utf-8') as file:
            self.system_prompt = file.read()
        with open("prompts/hacker_news_prompt.txt", "r", encoding='utf-8') as file:
            self.hacker_news_prompt = file.read()

    def generate_daily_report(self, markdown_content, dry_run=False):
        """
        生成每日报告，根据配置选择不同的模型来处理请求。
        
        :param markdown_content: 用户提供的Markdown内容。
        :param dry_run: 如果为True，提示信息将保存到文件而不实际调用模型。
        :return: 生成的报告内容或"DRY RUN"字符串。
        """
        # 准备消息列表，包含系统提示和用户内容
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": markdown_content},
        ]

        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+") as f:
                json.dump(messages, f, indent=4, ensure_ascii=False)  # 将消息保存为JSON格式
            LOG.debug("Prompt已保存到 daily_progress/prompt.txt")
            return "DRY RUN"

        # 根据选择的模型调用相应的生成报告方法
        if self.model == "openai":
            return self._generate_report_openai(messages)
        elif self.model == "ollama":
            return self._generate_report_ollama(messages)
        else:
            raise ValueError(f"Unsupported model type: {self.model}")

    def _generate_report_openai(self, messages):
        """
        使用 OpenAI GPT 模型生成报告。
        
        :param messages: 包含系统提示和用户内容的消息列表。
        :return: 生成的报告内容。
        """
        LOG.info("使用 OpenAI GPT 模型开始生成报告。")
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model_name,  # 使用配置中的OpenAI模型名称
                messages=messages
            )
            LOG.debug("GPT response: {}", response)
            return response.choices[0].message.content  # 返回生成的报告内容
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise

    def generate_hacker_news_daily_report(self, markdown_content, dry_run=False):
        # 使用从TXT文件加载的提示信息
        messages = [
            {"role": "system", "content": self.hacker_news_prompt},
            {"role": "user", "content": markdown_content},
        ]

        if dry_run:
            # 如果启用了dry_run模式，将不会调用模型，而是将提示信息保存到文件中
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("hacker_news/prompt.txt", "w+") as f:
                # 格式化JSON字符串的保存
                json.dump(messages, f, indent=4, ensure_ascii=False)
            LOG.debug("Prompt已保存到 hacker_news/prompt.txt")

            return "DRY RUN"

        # 日志记录开始生成报告
        LOG.info("使用 GPT 模型开始生成报告。")
        
                # 根据选择的模型调用相应的生成报告方法
        if self.model == "openai":
            return self._generate_report_openai(messages)
        elif self.model == "ollama":
            return self._generate_report_ollama(messages)
        else:
            raise ValueError(f"Unsupported model type: {self.model}")

    def _generate_report_ollama(self, messages):
        """
        使用 Ollama LLaMA 模型生成报告。
        
        :param messages: 包含系统提示和用户内容的消息列表。
        :return: 生成的报告内容。
        """
        LOG.info("使用 Ollama 托管模型服务开始生成报告。")
        try:
            payload = {
                "model": "deepseek-chat", # self.config.ollama_model_name,  # 使用配置中的Ollama模型名称
                "messages": messages,
                "stream": False
            }
            headers = {
                "Content-Type": "application/json",
                "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjRiMzc3N2RlLTM5ZGYtNDcxZi05N2M0LTZhZjEyMDgxODM4MCJ9.tNj6jbxrC8VV6XrKcQ60230s9y5_1OW73Q_Dfg1fsmc"
            }
            response = requests.post(self.api_url, json=payload, headers=headers)  # 发送POST请求到Ollama API
            response_data = response.json()
            # 调试输出查看完整的响应结构
            LOG.debug("Ollama response: {}", response_data)
            
            # 直接从响应数据中获取 content
            message_content = response_data.get("choices")[0].get("message", {}).get("content", None)
            if message_content:
                return message_content  # 返回生成的报告内容
            else:
                LOG.error("无法从响应中提取报告内容。")
                raise ValueError("Invalid response structure from Ollama API")
        except Exception as e:
            LOG.error(f"生成报告时发生错误：{e}")
            raise


if __name__ == '__main__':
    from config import Config  # 导入配置管理类
    config = Config()
    llm = LLM(config)

    markdown_content="""
# Progress for 2025-06-21 16:26:04)

## 1. Samsung Embeds IronSource Spyware App on Phones Across WANA
   Link: https://smex.org/open-letter-to-samsung-end-forced-israeli-app-installations-in-the-wana-region/

## 2. Sega mistakenly reveals sales numbers of popular games
   Link: https://www.gematsu.com/2025/06/sega-mistakenly-reveals-sales-numbers-for-like-a-dragon-infinite-wealth-persona-3-reload-shin-megami-tensei-v-and-more

## 3. AbsenceBench: Language models can't tell what's missing
   Link: https://arxiv.org/abs/2506.11440

## 4. Phoenix.new – Remote AI Runtime for Phoenix
   Link: https://fly.io/blog/phoenix-new-the-remote-ai-runtime/

## 5. Harper – an open-source alternative to Grammarly
   Link: https://writewithharper.com

## 6. Augmented Vertex Block Descent (AVBD)
   Link: https://graphics.cs.utah.edu/research/projects/avbd/

## 7. Chromium Switching from Ninja to Siso
   Link: https://groups.google.com/a/chromium.org/g/chromium-dev/c/v-WOvWUtOpg

## 8. Tiny Undervalued Hardware Companions (2024)
   Link: https://vermaden.wordpress.com/2024/03/21/tiny-undervalued-hardware-companions/

## 9. YouTube's new anti-adblock measures
   Link: https://iter.ca/post/yt-adblock/

## 10. Learn You Galois Fields for Great Good (00)
   Link: https://xorvoid.com/galois_fields_for_great_good_00.html

## 11. Mathematicians Hunting Prime Numbers Discover Infinite New Pattern
   Link: https://www.scientificamerican.com/article/mathematicians-hunting-prime-numbers-discover-infinite-new-pattern-for/

## 12. Show HN: A color name API that maps hex to the closest human-readable name
   Link: https://meodai.github.io/color-name-api/

## 13. Wiki Radio: The thrilling sound of random Wikipedia
   Link: https://www.monkeon.co.uk/wikiradio/

## 14. Visualizing environmental costs of war in Hayao Miyazaki's Nausicaä
   Link: https://jgeekstudies.org/2025/06/20/wilted-lands-and-wounded-worlds-visualizing-environmental-costs-of-war-in-hayao-miyazakis-nausicaa-of-the-valley-of-the-wind/

## 15. Show HN: Nxtscape – an open-source agentic browser
   Link: https://github.com/nxtscape/nxtscape

## 16. AMD's Freshly-Baked MI350: An Interview with the Chief Architect
   Link: https://chipsandcheese.com/p/amds-freshly-baked-mi350-an-interview

## 17. People instantly decide whether to trust a product based on design
   Link: https://www.andrewcoyle.com/blog/beauty-is-objective

## 18. College baseball, venture capital, and the long maybe
   Link: https://bcantrill.dtrace.org/2025/06/15/college-baseball-venture-capital-and-the-long-maybe/

## 19. Unexpected security footguns in Go's parsers
   Link: https://blog.trailofbits.com/2025/06/17/unexpected-security-footguns-in-gos-parsers/

## 20. Oklo, the Earth's Two-billion-year-old only Known Natural Nuclear Reactor (2018)
   Link: https://www.iaea.org/newscenter/news/meet-oklo-the-earths-two-billion-year-old-only-known-natural-nuclear-reactor

## 21. Show HN: Inspect and extract files from MSI installers directly in your browser
   Link: https://pymsi.readthedocs.io/en/latest/msi_viewer.html

## 22. Tuxracer.js play Tux Racer in the browser
   Link: https://github.com/ebbejan/tux-racer-js

## 23. Verified dynamic programming with Σ-types in Lean
   Link: https://tannerduve.github.io/blog/memoization-sigma/

## 24. Alpha Centauri
   Link: https://www.filfre.net/2025/06/alpha-centauri/

## 25. Smartphones: Parts of Our Minds? Or Parasites?
   Link: https://www.tandfonline.com/doi/full/10.1080/00048402.2025.2504070

## 26. A brief, incomplete, and mostly wrong history of robotics
   Link: https://generalrobots.substack.com/p/a-brief-incomplete-and-mostly-wrong

## 27. Cracovians: The Twisted Twins of Matrices
   Link: https://marcinciura.wordpress.com/2025/06/20/cracovians-the-twisted-twins-of-matrices/

## 28. Plastic bag bans and fees reduce harmful bag litter on shorelines
   Link: https://www.science.org/doi/10.1126/science.adp9274

## 29. A Python-first data lakehouse
   Link: https://www.bauplanlabs.com/blog/everything-as-python

## 30. Every Google &udm=? in the world (2024)
   Link: https://serpapi.com/blog/every-google-udm-in-the-world/
"""

    report = llm.generate_hacker_news_daily_report(markdown_content)
    print(report)

