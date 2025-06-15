import gradio as gr  # 导入gradio库用于创建GUI

from config import Config  # 导入配置管理模块
from github_client import GitHubClient  # 导入用于GitHub API操作的客户端
from report_generator import ReportGenerator  # 导入报告生成器模块
from llm import LLM  # 导入可能用于处理语言模型的LLM类
from subscription_manager import SubscriptionManager  # 导入订阅管理器
from logger import LOG  # 导入日志记录器

# 创建各个组件的实例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    # 定义一个函数，用于导出和生成指定时间范围内项目的进展报告
    raw_file_path = github_client.export_progress_by_date_range(repo, days)  # 导出原始数据文件路径
    report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)  # 生成并获取报告内容及文件路径

    return [report, report_file_path]  # 返回报告内容和报告文件路径

# Define a function to clear the inputs.
def clear_inputs(projs, slider_value):
    cleared_projs = []  # Clear the project list
    cleared_slider_value = 1  # Reset the slider value
    return [cleared_projs, cleared_slider_value]

def add_item(new_item):
    if new_item:  # 确保输入不为空
        subscription_manager.add_subscription(new_item)  # 添加新订阅到管理器
        # 更新本地项目列表
        LOG.info(f"Adding new item: {new_item}")  # 记录添加操作
        added_item_list = subscription_manager.list_subscriptions()
        # item_list.append(new_item)
        LOG.info(f"After Adding new item: {added_item_list}")  # 记录添加操作
        return gr.update(value=""), gr.update(choices=added_item_list)
    return gr.update(), gr.update()

def delete_item(selected_item):
    if selected_item in subscription_manager.list_subscriptions():
        removed_items = subscription_manager.remove_subscription(selected_item)  # 从管理器中删除选定的订阅
        # 从本地项目列表中删除选定的项目
        LOG.info(f"Removing item: {selected_item}")  # 记录删除操作
        LOG.info(f"After Removing item: {removed_items}")  # 记录删除操作
        return gr.update(value=subscription_manager.list_subscriptions()[0]), gr.update(choices=removed_items)
    return gr.update(), gr.update()

# 创建Gradio界面
# demo = gr.Interface(
#     fn=export_progress_by_date_range,  # 指定界面调用的函数
#     title="GitHubSentinel",  # 设置界面标题
#     inputs=[
#         gr.Dropdown(
#             subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目"
#         ),  # 下拉菜单选择订阅的GitHub项目
#         gr.Slider(value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"),
#         # 滑动条选择报告的时间范围
#     ],
#     outputs=[gr.Markdown(), gr.File(label="下载报告")],  # 输出格式：Markdown文本和文件下载
# )

# Create the Gradio interface.
with gr.Blocks(fill_height=True, fill_width=True) as demo:
    with gr.Tab("Favorites"):
        with gr.Column():
            # 输入框
            item_input = gr.Textbox(label="输入新项目")
            # 添加按钮
            add_btn = gr.Button("添加")
        with gr.Column():
            # 下拉选择框
            item_dropdown = gr.Dropdown(label="选择要删除的项目", choices=subscription_manager.list_subscriptions())
            # 删除按钮
            del_btn = gr.Button("删除")
        # 列表展示区域
        list_display = gr.List(subscription_manager.list_subscriptions(), label="当前列表")

    # 绑定按钮事件
    add_btn.click(
        fn=add_item,
        inputs=item_input,
        outputs=[item_input, item_dropdown]
    ).then(
        lambda: gr.List(subscription_manager.list_subscriptions()),
        outputs=list_display
    )
    
    del_btn.click(
        fn=delete_item,
        inputs=item_dropdown,
        outputs=item_dropdown
    ).then(
        lambda: gr.List(subscription_manager.list_subscriptions()),
        outputs=list_display
    )

    with gr.Tab("Report"):
        with gr.Row():
            with gr.Column(scale=1, min_width=300, variant="panel"):
                proj_dropdown = gr.Dropdown(
                    subscription_manager.list_subscriptions(), label="订阅列表", info="已订阅GitHub项目", allow_custom_value=True
                )  # Dropdown to select subscribed GitHub projects
                slider = gr.Slider(
                    value=2, minimum=1, maximum=7, step=1, label="报告周期", info="生成项目过去一段时间进展，单位：天"
                )  # Slider to select the report time range
                with gr.Row():
                    clear_button = gr.Button("Clear")
                    submit_button = gr.Button("Submit")
            with gr.Column(scale=2, min_width=300, show_progress=True, variant="panel"):
                markdown = gr.Markdown(value="", container=True, show_copy_button=True)  # Markdown to display the report content
                file_path = gr.File(label="下载报告")  # File component to download the report

        # Bind the clear button to the clear_inputs function.
        clear_button.click(
            fn=clear_inputs, 
            inputs=[proj_dropdown, slider], 
            outputs=[proj_dropdown, slider]
        )

        # Bind the submit button to the export_progress_by_date_range function.
        submit_button.click(
            fn=export_progress_by_date_range, 
            inputs=[proj_dropdown, slider], 
            outputs=[markdown, file_path]
        )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")  # 启动界面并设置为公共可访问
    # 可选带有用户认证的启动方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("django", "1234"))