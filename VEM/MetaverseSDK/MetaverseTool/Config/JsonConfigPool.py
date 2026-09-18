import json
import os


# Json配置池
class JsonConfigPool:
    def __init__(self):
        self.pool = {}

    def load(self, path: str):
        """Json载入池 load("data.json")"""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
        self.pool[path] = data

    def unload(self, path: str):
        """Json卸载池 unload("data.json")"""
        self.pool.pop(path, None)

    def clear(self):
        """清空池 clear()"""
        self.pool.clear()

    def all(self):
        """获取格式化后的整个池 all()"""
        return json.dumps(self.pool, indent=4, ensure_ascii=False, sort_keys=True)

    def older(self):
        """获取原始池 older()"""
        return self.pool

    def get(self, file_path: str, path: str, default = None):
        """获取Json get("data.json",["key","value"],None)"""
        if not path:
            return default
        node = self.pool.get(file_path, {})
        for key in path:
            if isinstance(node, dict):
                node = node.get(key)
            else:
                return default
        return node if node is not None else default

    def update(self, file_path: str, path: str, value):
        """更新Json值 update("data.json",["key","value"],new_value)"""
        if not path:
            return
        node = self.pool.setdefault(file_path, {})
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node[path[-1]] = value

    def rename(self, file_path: str, path: str, new_key: str):
        """重命名Json键 rename("data.json",["old_key"],"new_key")"""
        if not path:
            return
        node = self.pool.setdefault(file_path, {})
        for key in path[:-1]:
            node = node.setdefault(key, {})
        old_key = path[-1]
        if old_key in node:
            node[new_key] = node.pop(old_key)

    def append(self, file_path: str, path: list, value):
        """
        向list追加元素 add("data.json", ["tags"], "python")
        """
        if not path:
            return

        node = self.pool.setdefault(file_path, {})
        for key in path[:-1]:
            node = node.setdefault(key, {})

        last_key = path[-1]

        if last_key not in node:
            node[last_key] = []

        if not isinstance(node[last_key], list):
            raise TypeError(f"{last_key} 不是 list，无法 add")

        node[last_key].append(value)

    def insert(self, file_path: str, path: list, index: int, value):
        """
        向list指定位置插入元素 insert("data.json", ["tags"], index, "python")
        """
        if not path:
            return

        node = self.pool.setdefault(file_path, {})
        for key in path[:-1]:
            node = node.setdefault(key, {})

        last_key = path[-1]

        if last_key not in node:
            node[last_key] = []

        if not isinstance(node[last_key], list):
            raise TypeError(f"{last_key} 不是 list，无法 insert")

        node[last_key].insert(index, value)

    def extend(self, file_path: str, path: list, values: list):
        """
        向list批量添加 extend("data.json", ["tags"], ["a", "b", "c"])
        """
        if not path:
            return

        node = self.pool.setdefault(file_path, {})
        for key in path[:-1]:
            node = node.setdefault(key, {})

        last_key = path[-1]

        if last_key not in node:
            node[last_key] = []

        if not isinstance(node[last_key], list):
            raise TypeError(f"{last_key} 不是 list，无法 extend")

        node[last_key].extend(values)

    def modify(self, file_path: str, path: list, index: int, value):
        """
        修改list指定位置的元素 modify("config.json", ["pin"], row, new_value)
        """
        if not path:
            return

        node = self.pool.setdefault(file_path, {})
        for key in path[:-1]:
            node = node.setdefault(key, {})

        last_key = path[-1]

        if last_key not in node:
            raise KeyError(f"{last_key} 不存在")

        if not isinstance(node[last_key], list):
            raise TypeError(f"{last_key} 不是 list")

        if index < 0 or index >= len(node[last_key]):
            raise IndexError(f"{last_key} index out of range")

        node[last_key][index] = value

    def remove(self, file_path: str, path: list, index: int):
        """
        删除list指定位置的元素 remove("config.json", ["pin"], 2)
        """
        if not path:
            raise ValueError("path 不能为空")

        node = self.pool.get(file_path)
        if not isinstance(node, dict):
            raise KeyError(f"文件节点不存在: {file_path}")

        for key in path[:-1]:
            node = node.get(key)
            if not isinstance(node, dict):
                raise KeyError(f"路径中间层不是 dict: {key}")

        last_key = path[-1]
        lst = node.get(last_key) if isinstance(node, dict) else None

        if not isinstance(lst, list):
            raise TypeError(f"{'.'.join(path)} 不是 list")

        if index < -len(lst) or index >= len(lst):
            raise IndexError(f"list index out of range: {index}")

        lst.pop(index)

    def delete(self, file_path: str, path: str):
        """删除Json键 delete("data.json",["key"])"""
        if not path:
            return
        node = self.pool.setdefault(file_path, {})
        for key in path[:-1]:
            node = node.setdefault(key, {})
        node.pop(path[-1], None)

    def save(self, path: str = None):
        """保存池到硬盘 存全部 save() / 单个 save(path)"""
        # 确定保存的路径列表
        if path:
            paths = [path]
        else:
            # 统一处理
            paths = list(self.pool.keys())

        for p in paths:
            if p not in self.pool:
                continue

            # 规范化路径
            normalized_path = os.path.normpath(p)

            # 获取目录部分
            dir_name = os.path.dirname(normalized_path)

            # 尝试创建目录
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            # 写入文件
            with open(normalized_path, "w", encoding="utf-8") as f:
                json.dump(self.pool[p], f, indent=2, ensure_ascii=False)

# 单例
JCP = JsonConfigPool()