import json
import os


def read_json(json_path):
    """读取Json"""
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except Exception as a:
        print(a)

def auto_create_json_file(path, data=None):
    """
    自动创建json和父目录路径
    """
    try:
        # 获取文件夹路径
        folder_path = os.path.dirname(path)
        # 自动创建文件夹
        if folder_path and not os.path.exists(folder_path):
            os.makedirs(folder_path)
        # 默认空字典
        if data is None:
            data = {}
        # 写入JSON文件内容
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"创建JSON文件失败: {e}")
        return False

def modify_json(json_path, key, new_value):
    """
    最简单的JSON修改函数
    接受json路径、键、修改后的值，修改键的值

    Args:
        json_path: JSON文件路径
        key: 要修改的键
        new_value: 新的值
    """
    try:
        # 1. 读取JSON文件
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 2. 修改指定键的值
        data[key] = new_value

        # 3. 保存回文件
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return True

    except FileNotFoundError:
        print(f"文件不存在: {json_path}")
    except json.JSONDecodeError:
        print(f"JSON格式错误: {json_path}")
    except Exception as e:
        print(f"修改失败: {e}")