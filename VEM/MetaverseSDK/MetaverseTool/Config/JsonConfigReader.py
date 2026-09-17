import json
import os
from typing import Optional, Sequence, Any


class JsonConfigReader:
    """
    JSON配置阅读器
    一次性读取 JSON 文件，提供嵌套路径取值。
    用完调用 close() 或 del 释放内存（其实 dict 会被 GC，close 主要是语义上的）。
    """

    def __init__(self, file_path: str, default: Optional[dict] = None):
        """
        参数：
            file_path: JSON 文件路径
            default:   文件不存在 / JSON 损坏时的默认根 dict
        """
        if default is None:
            default = {}

        if not os.path.exists(file_path):
            self._data: dict = default.copy()
            self._loaded = False
        else:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                self._loaded = True
            except json.JSONDecodeError:
                self._data = default.copy()
                self._loaded = False

    def get(self, path: Sequence[str], default: Any = None) -> Any:
        """
        按路径取值。

        示例：
            cfg.get(["window", "size"], 400)
        """
        if not isinstance(path, Sequence) or not path:
            raise ValueError("path 必须是非空字符串序列，如 ['a', 'b']")

        node = self._data
        for key in path:
            if isinstance(node, dict) and key in node:
                node = node[key]
            else:
                return default

        return node

    @property
    def raw(self) -> dict:
        """返回完整内部 dict 的浅拷贝（防止外部误改）。"""
        return self._data.copy()

    @property
    def is_loaded(self) -> bool:
        """文件是否成功加载（而非 fallback 到 default）。"""
        return self._loaded

    def close(self) -> None:
        """释放内部数据。调用后不要再使用 get()。"""
        self._data.clear()
        self._data = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f"<JsonConfigReader loaded={self._loaded} keys={list(self._data.keys())}>"