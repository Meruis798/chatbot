# _*_ coding : utf-8 _*_
# created by wanjin at 2025/3/31
import streamlit as st
import requests
from PIL import Image
import io

def upload_image(uploaded_file, api_url="https://u494575-8903-e70e978c.westx.seetacloud.com:8443/query-image/"):
    """上传图片到 /query-image/ 端点，获取查重结果"""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        files = {'file': (uploaded_file.name, bytes_data, 'image/jpeg')}
        headers = {'accept': 'application/json'}
        try:
            response = requests.post(url=api_url, headers=headers, files=files)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    return None


def get_matched_image(uploaded_file, api_url="https://u494575-8903-e70e978c.westx.seetacloud.com:8443/match-images/"):
    """上传图片到 /match-images/ 端点，获取匹配图像"""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        files = {'file': (uploaded_file.name, bytes_data, 'image/jpeg')}
        try:
            response = requests.post(url=api_url, files=files)
            if response.status_code == 200:
                return response.content  # 返回图像的二进制数据
            else:
                return {"error": f"请求失败，状态码：{response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    return None


def main():
    st.title("图片查重系统")

    # 文件上传组件
    uploaded_file = st.file_uploader("选择要查重的图片", type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        # 创建两列布局
        col1, col2 = st.columns(2)

        # 左侧显示上传的图片
        with col1:
            st.subheader("上传的图片")
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)

        # 查重按钮
        if st.button("开始查重"):
            with st.spinner('正在查重中...'):
                # 重置文件指针
                uploaded_file.seek(0)

                # 调用 /query-image/ 获取查重结果
                query_result = upload_image(uploaded_file)
                # 调用 /match-images/ 获取匹配图像
                matched_image_data = get_matched_image(uploaded_file)

                # 右侧显示查重结果和匹配图像
                with col2:

                    st.subheader("查重结果")
                    if query_result and "error" not in query_result:
                        st.json(query_result)
                    else:
                        st.error("查重失败：" + str(query_result.get("error", "未知错误")))

                    st.subheader("匹配图像")
                    if matched_image_data and isinstance(matched_image_data, bytes):
                        matched_image = Image.open(io.BytesIO(matched_image_data))
                        st.image(matched_image, use_container_width=True)
                    else:
                        st.error("获取匹配图像失败：" + str(matched_image_data.get("error", "未知错误")))


if __name__ == "__main__":
    main()
