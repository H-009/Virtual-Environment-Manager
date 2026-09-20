import hashlib

def hash_str(input_string, algorithm='sha256'):
    """将字符串转换为指定哈希值"""
    try:
        # 选择哈希算法
        hash_func = getattr(hashlib, algorithm)
        # 编码字符串
        encoded_string = input_string.encode('utf-8')
        # 计算哈希值
        hash_object = hash_func(encoded_string)
        # 返回十六进制字符串
        return hash_object.hexdigest()
    except AttributeError:
        raise ValueError(f"不支持的哈希算法: {algorithm}")