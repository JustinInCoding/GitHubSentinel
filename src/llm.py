# src/llm.py

import os
from openai import OpenAI

class LLM:
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1",  # DeepSeek API 的基地址
        )

    def generate_daily_report(self, markdown_content, dry_run=False):
        prompt = f"{markdown_content}"
        if dry_run:
            with open("daily_progress/prompt.txt", "w+") as f:
                f.write(prompt)
            return "DRY RUN"

        print("Before call deepseek")
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你需要将用户输入项目的最新进展，根据功能合并同类项，形成一份简报，至少包含：1）新增功能；2）主要改进；3）修复问题；请注意，简报需要简洁明了，便于阅读和理解。"},
                {"role": "user", "content": prompt}
            ]
        )
        print("After call deepseek")
        print(response)
        return response.choices[0].message.content
