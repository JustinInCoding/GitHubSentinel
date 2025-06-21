# src/hacker_news_client.py

import requests  # 导入requests库用于HTTP请求
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta  # 导入日期处理模块
import os  # 导入os模块用于文件和目录操作
from logger import LOG  # 导入日志模块

class HackerNewsClient:

    def fetch_hackernews_top_stories(self):
        url = 'https://news.ycombinator.com/'
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找包含新闻的所有 <tr> 标签
        stories = soup.find_all('tr', class_='athing')

        top_stories = []
        for story in stories:
            title_tag = story.find('span', class_='titleline').find('a')
            if title_tag:
                title = title_tag.text
                link = title_tag['href']
                top_stories.append({'title': title, 'link': link})

        return top_stories

    def export_latest_hack_news(self):
        # 获取当前时间
        now = datetime.now()

        formatted_day = now.strftime("%Y-%m-%d")
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")

        report_dir = os.path.join('hacker_news', f'{formatted_day}')
        
        updates = self.fetch_hackernews_top_stories()
        
        os.makedirs(report_dir, exist_ok=True)  # 确保目录存在
        
        file_path = os.path.join(report_dir, f'{formatted_time}.md')  # 构建文件路径. 
        
        with open(file_path, 'w') as file:
            file.write(f"# Progress for {formatted_time})\n\n")
            for idx, story in enumerate(updates, start=1):
                file.write(f"## {idx}. {story['title']}\n")
                file.write(f"   Link: {story['link']}\n\n")
        
        LOG.info(f"[hacker news]最新资讯文件生成： {file_path}")  # 记录日志
        return file_path

    # def export_daily_progress(self, repo):
    #     LOG.debug(f"[准备导出项目进度]：{repo}")
    #     today = datetime.now().date().isoformat()  # 获取今天的日期
    #     updates = self.fetch_updates(repo, since=today)  # 获取今天的更新数据
        
    #     repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))  # 构建存储路径
    #     os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
    #     file_path = os.path.join(repo_dir, f'{today}.md')  # 构建文件路径
    #     with open(file_path, 'w') as file:
    #         file.write(f"# Daily Progress for {repo} ({today})\n\n")
    #         file.write("\n## Issues Closed Today\n")
    #         for issue in updates['issues']:  # 写入今天关闭的问题
    #             file.write(f"- {issue['title']} #{issue['number']}\n")
        
    #     LOG.info(f"[{repo}]项目每日进展文件生成： {file_path}")  # 记录日志
    #     return file_path

    # def export_progress_by_date_range(self, repo, days):
    #     today = date.today()  # 获取当前日期
    #     since = today - timedelta(days=days)  # 计算开始日期
        
    #     updates = self.fetch_updates(repo, since=since.isoformat(), until=today.isoformat())  # 获取指定日期范围内的更新
        
    #     repo_dir = os.path.join('daily_progress', repo.replace("/", "_"))  # 构建目录路径
    #     os.makedirs(repo_dir, exist_ok=True)  # 确保目录存在
        
    #     # 更新文件名以包含日期范围
    #     date_str = f"{since}_to_{today}"
    #     file_path = os.path.join(repo_dir, f'{date_str}.md')  # 构建文件路径
        
    #     with open(file_path, 'w') as file:
    #         file.write(f"# Progress for {repo} ({since} to {today})\n\n")
    #         file.write(f"\n## Issues Closed in the Last {days} Days\n")
    #         for issue in updates['issues']:  # 写入在指定日期内关闭的问题
    #             file.write(f"- {issue['title']} #{issue['number']}\n")
        
    #     LOG.info(f"[{repo}]项目最新进展文件生成： {file_path}")  # 记录日志
    #     return file_path

if __name__ == "__main__":
    hack_news_client = HackerNewsClient()
    # stories = hack_news_client.fetch_hackernews_top_stories()
    # if stories:
    #     for idx, story in enumerate(stories, start=1):
    #         print(f"{idx}. {story['title']}")
    #         print(f"   Link: {story['link']}")
    # else:
    #     print("No stories found.")
    hack_news_client.export_latest_hack_news()
