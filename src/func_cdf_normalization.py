import os


def __normalize_cdf_content(cdf_content):
    """对CDF文本做归一化：如果首行是TAPE则移除。"""
    lines = cdf_content.splitlines(keepends=True)
    if not lines:
        return cdf_content
    if lines[0].strip() == 'TAPE':
        return ''.join(lines[1:])
    return cdf_content

# 创建临时文件写入新内容
def func_cdf_normalization(filename=None, cdf_content=None):
    """
    兼容两种归一化模式：
    1) 传入 filename：原地改写文件
    2) 传入 cdf_content：返回归一化后的文本
    """
    if cdf_content is not None:
        return __normalize_cdf_content(cdf_content)

    if not filename:
        raise ValueError("filename 和 cdf_content 至少传入一个")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} does not exist.")

    with open(filename, 'r', encoding='utf-8') as infile:
        normalized = __normalize_cdf_content(infile.read())

    temp_filename = f"{filename}.tmp"
    with open(temp_filename, 'w', encoding='utf-8') as outfile:
        outfile.write(normalized)

    os.replace(temp_filename, filename)
