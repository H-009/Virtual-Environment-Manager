import json
import os
from typing import Sequence, Any, Optional, Union


def update_json_key(file_path: str, key: str, value, default: dict = None):
    """
    支持嵌套键（如 "window.size"）
    """

    if default is None:
        default = {}

    if not os.path.exists(file_path):
        content = default.copy()
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except json.JSONDecodeError:
            content = default.copy()

    # 解析嵌套键
    keys = key.split(".")
    d = content
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

    return content

def update_json_key_v2(file_path: str, path: Sequence[str], value: Any, default: Optional[dict] = None) -> dict:
    """
    更新 JSON 文件中指定路径的值（列表路径，无 dot）。

    示例：
        update_json_key("config.json", ["window", "size"], 800)

    参数：
        file_path: JSON 文件路径
        path:      键路径，如 ["a", "b", "c"]
        value:     要写入的值
        default:   文件不存在或损坏时的默认根对象

    返回：
        更新后的完整 JSON dict
    """
    if default is None:
        default = {}

    if not isinstance(path, Sequence) or not path:
        raise ValueError("path 必须是非空字符串序列，如 ['a', 'b']")

    # 读取或初始化
    if not os.path.exists(file_path):
        content = default.copy()
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except json.JSONDecodeError:
            content = default.copy()

    # 遍历路径
    node = content
    for i, key in enumerate(path[:-1]):
        if not isinstance(node, dict):
            raise TypeError(
                f"路径 {path[:i]} 不是 dict，无法继续深入"
            )
        node = node.setdefault(key, {})

    # 设置最终值
    last_key = path[-1]
    if not isinstance(node, dict):
        raise TypeError(
            f"路径 {path[:-1]} 不是 dict，无法设置键 '{last_key}'"
        )
    node[last_key] = value

    # 写回
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

    return content

def get_json_key(file_path: str, key: str, default=None):
    """
    支持嵌套键（如 "window.size"）
    返回指定键的值，如果文件不存在或键不存在，则返回default。
    """
    if not os.path.exists(file_path):
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
    except json.JSONDecodeError:
        return default

    keys = key.split(".")
    d = content
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d

def get_json_key_v2(file_path: str,path: Sequence[str],default: Any = None) -> Any:
    """
    读取 JSON 文件中指定路径的值（列表路径，无 dot）。

    示例：
        get_json_key_v2("config.json", ["python", "env_name"])
        get_json_key_v2("config.json", ["window", "size"], 400)

    参数：
        file_path: JSON 文件路径
        path:      键路径，如 ["a", "b", "c"]
        default:   文件不存在 / 路径不存在时的返回值

    返回：
        路径对应的值，或 default
    """
    if not isinstance(path, Sequence) or not path:
        raise ValueError("path 必须是非空字符串序列，如 ['a', 'b']")

    # 文件不存在或 JSON 损坏 → 直接返 default
    if not os.path.exists(file_path):
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
    except json.JSONDecodeError:
        return default

    # 逐层往下走
    node = content
    for key in path:
        if isinstance(node, dict) and key in node:
            node = node[key]
        else:
            return default

    return node

def append_json_key(file_path: str, key: str, value, default: dict = None):
    """
    在 JSON 中指定 key（必须是 list）追加一个值
    支持嵌套键，如 "a.b.c"
    """
    if default is None:
        default = {}

    if not os.path.exists(file_path):
        content = default.copy()
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except json.JSONDecodeError:
            content = default.copy()

    keys = key.split(".")
    d = content

    # 逐层进入
    for k in keys[:-1]:
        d = d.setdefault(k, {})

    last_key = keys[-1]

    # 如果不存在，初始化为空列表
    if last_key not in d or not isinstance(d[last_key], list):
        d[last_key] = []

    d[last_key].append(value)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

    return content

def append_json_key_v2(file_path: str,path: Sequence[str],value: Any,default: Optional[dict] = None,) -> Any:
    """
    在 JSON 中指定 key（必须是 list）追加一个值
    使用列表路径，如 ["a", "b", "c"]

    示例：
        append_json_key("data.json", ["logs", "errors"], "oops")
        append_json_key("data.json", ["a", "b"], 1, default={})
    """
    if not isinstance(path, Sequence) or not path:
        raise ValueError("path 必须是非空字符串序列，如 ['a', 'b']")

    if default is None:
        default = {}

    # 读文件
    if not os.path.exists(file_path):
        content = default.copy()
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except json.JSONDecodeError:
            content = default.copy()

    # 逐层进入
    node = content
    for key in path[:-1]:
        if isinstance(node, dict):
            node = node.setdefault(key, {})
        else:
            # 路径中间不是 dict，直接覆盖为新结构
            node.clear()
            node.update({})
            node = node.setdefault(key, {})

    last_key = path[-1]

    # 确保是 list
    if last_key not in node or not isinstance(node[last_key], list):
        node[last_key] = []

    node[last_key].append(value)

    # 写回
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

    return content

def delete_json_key(file_path: str, key: str) -> bool:
    """
    支持嵌套键（如 "window.size"）
    删除指定键。返回 True 表示删除成功，False 表示文件不存在 / 键不存在 / JSON 解析失败。
    """
    if not os.path.exists(file_path):
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
    except json.JSONDecodeError:
        return False

    keys = key.split(".")
    d = content

    # 遍历到倒数第二层，拿到父容器
    for k in keys[:-1]:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return False  # 中间某层路径不存在

    last_key = keys[-1]
    if not isinstance(d, dict) or last_key not in d:
        return False  # 目标键本身不存在

    del d[last_key]

    # 写回文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

    return True

def delete_json_key_v2(file_path: str,path: Sequence[str],default: Optional[dict] = None) -> dict:
    """
    删除 JSON 文件中指定路径的键。

    示例：
        delete_json_key_v2("config.json", ["python", "env_name"])

    返回：
        更新后的完整 JSON dict（若文件/键不存在则原样返回或返回 default）
    """
    if default is None:
        default = {}

    if not isinstance(path, Sequence) or not path:
        raise ValueError("path 必须是非空字符串序列")

    # 读取
    if not os.path.exists(file_path):
        return default.copy()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
    except json.JSONDecodeError:
        return default.copy()

    # 遍历到倒数第二层
    node = content
    for i, key in enumerate(path[:-1]):
        if not isinstance(node, dict) or key not in node:
            return content   # 路径不存在，原样返回
        node = node[key]

    last_key = path[-1]
    if isinstance(node, dict) and last_key in node:
        del node[last_key]

    # 写回
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

    return content

def modify_json_list_item_v2(file_path: str,path: Sequence[str],index: int,value: Any,default: Optional[dict] = None,) -> Any:
    """
    修改 JSON 中 list 里指定索引的项

    路径必须是 list，如 ["a", "b"]
    index 为要修改的列表下标（支持负索引）

    示例：
        modify_json_list_item("data.json", ["logs", "errors"], 0, "fixed")
        modify_json_list_item("data.json", ["a", "b"], -1, 999)

    异常：
        IndexError: 索引越界
        TypeError:  路径最终不是 list
        ValueError: path 非法
    """
    if not isinstance(path, Sequence) or not path:
        raise ValueError("path 必须是非空字符串序列，如 ['a', 'b']")
    if index is None:
        raise ValueError("index 必须指定")

    if default is None:
        default = {}

    # 读
    if not os.path.exists(file_path):
        content = default.copy()
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except json.JSONDecodeError:
            content = default.copy()

    # 走到父节点
    node = content
    for key in path[:-1]:
        if isinstance(node, dict):
            node = node.setdefault(key, {})
        else:
            raise TypeError(f"路径中间节点不是 dict: {key}")

    last_key = path[-1]

    if last_key not in node:
        raise KeyError(f"键不存在: {last_key}")

    target = node[last_key]

    if not isinstance(target, list):
        raise TypeError(f"路径终点不是 list: {last_key}")

    # 索引检查
    if not -len(target) <= index < len(target):
        raise IndexError(f"index {index} 越界 (size={len(target)})")

    target[index] = value

    # 写回
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

    return content

def delete_json_list_item_v2(file_path: str,path: Sequence[str],index: int,default: Optional[dict] = None,) -> Any:
    """
    删除 JSON 中 list 指定索引的项（支持负索引）

    示例：
        delete_json_list_item_v2("data.json", ["logs", "errors"], 0)
        delete_json_list_item_v2("data.json", ["a", "b"], -1)

    异常：
        IndexError: 索引越界（由 list.pop 抛出）
        TypeError:  路径终点不是 list
        KeyError:   键不存在
        ValueError: path 非法
    """
    if not isinstance(path, Sequence) or not path:
        raise ValueError("path 必须是非空字符串序列，如 ['a', 'b']")

    if default is None:
        default = {}

    # 读
    if not os.path.exists(file_path):
        content = default.copy()
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except json.JSONDecodeError:
            content = default.copy()

    # 走到父节点
    node = content
    for key in path[:-1]:
        if isinstance(node, dict):
            node = node.setdefault(key, {})
        else:
            raise TypeError(f"路径中间节点不是 dict: {key}")

    last_key = path[-1]

    if last_key not in node:
        raise KeyError(f"键不存在: {last_key}")

    target = node[last_key]

    if not isinstance(target, list):
        raise TypeError(f"路径终点不是 list: {last_key}")

    # 删除（pop 会自动校验 index）
    removed = target.pop(index)

    # 写回
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

    return content

def get_json_list_item_v2(file_path: str,path: Sequence[str],index: int,default: Any = None,) -> Any:
    """
    读取 JSON 中 list 指定索引的项（支持负索引）
    不修改文件

    示例：
        get_json_list_item_v2("data.json", ["logs", "errors"], 0)
        get_json_list_item_v2("data.json", ["a", "b"], -1, default="N/A")

    返回：
        索引对应的元素，或 default

    异常：
        TypeError: 路径终点不是 list
        ValueError: path 非法
        FileNotFoundError / JSONDecodeError 不会抛，会走 default
    """
    if not isinstance(path, Sequence) or not path:
        raise ValueError("path 必须是非空字符串序列，如 ['a', 'b']")

    if not os.path.exists(file_path):
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
    except json.JSONDecodeError:
        return default

    # 走到父节点
    node = content
    for key in path[:-1]:
        if isinstance(node, dict) and key in node:
            node = node[key]
        else:
            return default

    last_key = path[-1]

    if not isinstance(node, dict) or last_key not in node:
        return default

    target = node[last_key]
    if not isinstance(target, list):
        raise TypeError(f"路径终点不是 list: {last_key}")

    if not -len(target) <= index < len(target):
        return default

    return target[index]

def json_equal(a: Any, b: Any) -> bool:
    """
    判断两个 JSON 数据是否一致：
    - 字典：key 顺序无关，值必须完全一致
    - 列表：顺序敏感（完全一致）
    - 支持嵌套
    """
    # 类型不同直接判 False
    if type(a) != type(b):
        return False

    # 字典：key 顺序无关，递归比较值
    if isinstance(a, dict):
        if a.keys() != b.keys():
            return False
        return all(json_equal(a[k], b[k]) for k in a)

    # 列表：顺序敏感
    if isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(json_equal(a[i], b[i]) for i in range(len(a)))

    # 基本类型：值必须完全相等
    return a == b

def read_json(file_path: str, default: Any = None) -> Any:
    """
    直接读取 JSON 文件，返回整个 JSON 数据。

    示例：
        data = read_json_file("config.json")
        data = read_json_file("not_exist.json", {})

    参数：
        file_path: JSON 文件路径
        default:   文件不存在或解析失败时的返回值

    返回：
        解析后的 JSON 数据（dict / list），或 default
    """
    if not isinstance(file_path, str) or not file_path:
        return default

    if not os.path.exists(file_path):
        return default

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default