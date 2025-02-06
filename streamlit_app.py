import requests
import streamlit as st
import json
import re
import os


# 发送 POST 请求
def send_post_request(url, prompt, headers=None):
    try:
        # 发送 POST 请求，将 prompt 作为查询参数
        params = {"prompt": prompt}
        response = requests.post(url, params=params, headers=headers)
        # 检查请求是否成功（状态码为 200）
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
            return None
    except requests.RequestException as e:
        st.error(f"请求出现异常: {str(e)}")
        return None


# 高亮显示关键词
def highlight_keywords(text):
    # 使用正则表达式将关键词替换为带有 HTML 红色样式的文本
    highlighted_text = re.sub(r'(逐步分析|治疗建议|结论)', r'<span style="color:red">\1</span>', text)
    return highlighted_text


# 保存所有返回的 response 到一个 JSON 文件
def save_all_responses_to_json(all_responses, directory="responses", filename="all_responses.json"):
    # 确保目标目录存在
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 保存文件的路径
    file_path = os.path.join(directory, filename)

    # 将所有响应保存为 JSON 文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(all_responses, f, ensure_ascii=False, indent=4)


# 批处理功能：处理多个 prompt
def process_batch(prompts, url, directory="responses"):
    # 显示进度条
    progress_bar = st.progress(0)
    total_prompts = len(prompts)

    # 用来存储所有响应的列表
    all_responses = []

    # 逐个处理每个 prompt
    for i, prompt in enumerate(prompts):
        st.write(f"正在处理第 {i + 1} 个请求: {prompt}")

        # 更新进度条
        progress_bar.progress((i + 1) / total_prompts)

        result = send_post_request(url, prompt)
        if result:
            # 获取 response 内容
            response_content = result.get("response", None)
            if response_content:
                # 添加响应到列表中
                all_responses.append({
                    "prompt": prompt,
                    "response": response_content
                })
                # 高亮显示关键词
                highlighted_content = highlight_keywords(response_content)
                st.markdown(highlighted_content, unsafe_allow_html=True)
            else:
                st.warning(f"第 {i + 1} 个请求的 response 中没有所需内容。")
        else:
            st.warning(f"第 {i + 1} 个请求处理失败。")

    # 完成处理后，隐藏进度条
    progress_bar.empty()

    # 保存所有响应到 JSON 文件
    save_all_responses_to_json(all_responses, directory, "all_responses.json")

    st.success("批处理完成！所有响应已保存到一个 JSON 文件中。")


# 处理单个 prompt 的功能
def process_single_prompt(prompt, url):
    result = send_post_request(url, prompt)
    if result:
        response_content = result.get("response", None)
        if response_content:
            # 高亮显示关键词
            highlighted_content = highlight_keywords(response_content)
            st.markdown(highlighted_content, unsafe_allow_html=True)
        else:
            st.warning("响应中没有包含所需内容。")
    else:
        st.warning("请求失败，未能获得响应。")


# Streamlit 主函数
def main():
    st.title("💬肝癌治疗助手")

    # 使用 st.session_state 存储服务器地址
    if 'server_url' not in st.session_state:
        st.session_state.server_url = "https://u494575-9ca8-5c732349.nmb1.seetacloud.com:8443/generate"  # 修改为 FastAPI 服务的地址

    # 选择批处理或单个测试
    option = st.radio("请选择操作模式", ("批处理", "单个测试"))

    if option == "批处理":
        # 上传 JSON 文件，包含多个 prompt
        uploaded_file = st.file_uploader("上传包含多个 Prompt 的 JSON 文件", type="json")

        if uploaded_file is not None:
            # 读取 JSON 文件中的 prompt 数据
            prompts = json.load(uploaded_file)

            if isinstance(prompts, list):  # 确保文件中的数据是一个列表
                # 执行批处理
                if st.button("开始批处理"):
                    process_batch(prompts, st.session_state.server_url)
            else:
                st.error("上传的文件格式不正确，应该是包含多个 prompt 的 JSON 列表。")
    else:
        # 单个测试模式：输入单个 prompt
        if 'prompt' not in st.session_state:
            st.session_state.prompt = ""

        prompt = st.text_area("输入病情", value=st.session_state.prompt)

        # 创建两列，按钮放在同一行
        col1, col2 = st.columns([3, 1])  # 第一列宽度较大，第二列较小

        # 在第一列放置 "测试单个 Prompt" 按钮
        with col1:
            if st.button("请求助手"):
                if prompt:
                    st.session_state.prompt = prompt  # 保存当前的输入
                    process_single_prompt(prompt, st.session_state.server_url)
                else:
                    st.error("请输入一个 病情 后再测试。")

        # 在第二列放置 "清空 Prompt" 按钮
        with col2:
            if st.button("清空 病情"):
                st.session_state.prompt = ""  # 清空输入框内容

# 入口
if __name__ == "__main__":
    main()

