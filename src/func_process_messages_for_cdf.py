import base64
import zipfile
import io
import os
import re
import json
import cloudpss
import time

from func_cloudpss_config import func_inject_cloudpss_config


def __find_download_link_message(messages):
    """
    在消息数组中查找包含下载链接的消息
    
    参数:
    messages: 消息数组，每个元素是字典
    
    返回:
    包含下载链接的消息内容字符串，如果未找到则返回None
    """
    for i, message in enumerate(messages):
        try:
            # 检查消息结构是否包含 data->content
            if isinstance(message, dict) and 'data' in message:
                data = message['data']
                if isinstance(data, dict) and 'content' in data:
                    content = data['content']
                    
                    # 检查内容是否是字符串且包含下载链接
                    if isinstance(content, str) and content.startswith("<a download='cf.zip' href='data:application/zip;base64,"):
                        print(f"在消息索引 {i} 中找到下载链接")
                        return content
        except (TypeError, KeyError):
            continue
    
    print("未找到包含下载链接的消息")
    return None

def __extract_data_uri_from_html(html_content):
    """
    从HTML内容中提取完整的data URI
    
    参数:
    html_content: 包含<a>标签的HTML内容
    
    返回:
    完整的data URI字符串
    """
    # 使用正则表达式提取href属性的值
    pattern = r"href=['\"](data:application/zip;base64,[^'\"]+)['\"]"
    match = re.search(pattern, html_content)
    
    if match:
        return match.group(1)
    
    # 如果正则失败，尝试简单分割方法
    if "href='" in html_content:
        start = html_content.find("href='") + len("href='")
        end = html_content.find("'", start)
        return html_content[start:end]
    elif 'href="' in html_content:
        start = html_content.find('href="') + len('href="')
        end = html_content.find('"', start)
        return html_content[start:end]
    
    raise ValueError("无法从HTML内容中提取data URI")

def __extract_area_files_from_data_uri(data_uri, area_name):
    """从data URI中解析zip并在内存中读取指定分区的cf与cf.map内容。"""
    match = re.search(r"base64,(.*)$", data_uri)
    if not match:
        raise ValueError("无效的data URI格式，未找到Base64数据")

    base64_str = match.group(1)
    clean_base64 = re.sub(r"[^a-zA-Z0-9+/=]", "", base64_str)

    try:
        zip_bytes = base64.b64decode(clean_base64)
    except Exception as exc:
        raise ValueError("ZIP文件解码失败，请检查data URI格式") from exc

    target_cf = f"{area_name}.cf"
    target_map = f"{area_name}.cf.map"

    with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
        name_map = {os.path.basename(name): name for name in zip_ref.namelist()}

        if target_cf not in name_map:
            raise FileNotFoundError(f"{target_cf} 不在压缩包中")
        if target_map not in name_map:
            raise FileNotFoundError(f"{target_map} 不在压缩包中")

        cf_content = zip_ref.read(name_map[target_cf]).decode('utf-8')
        map_content = zip_ref.read(name_map[target_map]).decode('utf-8')

    return {
        "area_name": area_name,
        "cf": cf_content,
        "cf_map": map_content,
    }


def func_process_messages_for_cdf(messages, output_dir, area_name):
    """
    处理消息数组以提取CDF文件
    
    参数:
    messages: 消息数组
    output_dir: 输出目录/zip名称（保留参数，不落地写文件）
    area_name: 分区名，例如 area1
    
    返回:
    字典，包含内存中的cf和cf.map文本
    """
    # 1. 查找包含下载链接的消息
    html_content = __find_download_link_message(messages)
    if html_content is None:
        raise ValueError("消息数组中未找到下载链接")
    
    # 2. 从HTML内容中提取data URI
    data_uri = __extract_data_uri_from_html(html_content)
    print(f"提取的data URI长度: {len(data_uri)}")
    
    # 3. 从data URI读取分区文件内容（纯内存）
    return __extract_area_files_from_data_uri(data_uri, area_name)

# 使用示例
if __name__ == "__main__":
    # 示例消息数组 (实际使用时替换为您的真实数据)
    # # generate cdf file
    project_name = "IEEE39"
    area_name = "area1"
    server_name, token, user_name = func_inject_cloudpss_config()
    cloudpss.setToken(f'{token}')
    os.environ['CLOUDPSS_API_URL'] = f'{server_name}'
    model = cloudpss.Model.fetch(f'model/{user_name}/{project_name}')
    config = model.configs[0]
    job = model.jobs[0]
    
    runner = model.run(job,config) # 运行计算方案
    while not runner.status(): 
        logs = runner.result.getLogs() # 获得运行日志
        for log in logs: 
            print(log)
        time.sleep(1)

    messages = runner.result.db.message
    
    # 输出目录
    output_directory = "cf.zip"
    
    try:
        # 处理消息数组并提取CDF文件
        cdf_files = func_process_messages_for_cdf(
            messages,
            output_directory,
            area_name=area_name
        )
        print(f"成功读取分区文件: {cdf_files['area_name']}.cf / {cdf_files['area_name']}.cf.map")
        
        # 现在可以使用之前的方法处理CDF文件获取导纳矩阵
        # Ybus = get_ybus_from_cdf(cdf_path)
        
    except Exception as e:
        print(f"处理失败: {str(e)}")
