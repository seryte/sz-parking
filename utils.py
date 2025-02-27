import base64

# parse_base64 解析base64，car_no和phone_no都通过base64编码，需要解析出原文本
def parse_base64(base64_str) -> str:
    """
    解析base64字符串，返回原始字符串。
    参数:
    base64_str (str): base64字符串。
    返回:
    str: 解析后的原始字符串。
    """
    return base64.b64decode(base64_str).decode()

def encode_base64(value):
    """Helper function to encode strings with Base64."""
    return base64.b64encode(value.encode()).decode()

# split_task_id #分割开的task_id
def split_task_id(input_string):
    parts = input_string.split('+', 1)
    if len(parts) == 1:
        return parts[0], ""
    else:
        return parts[0], parts[1]