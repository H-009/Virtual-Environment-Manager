import base64

from qtpy.QtCore import QByteArray
from qtpy.QtGui import QPixmap, QIcon


# Base64图标池
class BaseIconPool:
    def __init__(self):
        self.pool = {}

    def load(self, name: str, base64_str: str):
        """加载图标到池中 load(ico,base64)"""
        if not name or not base64_str:
            return

        try:
            # 处理可能存在的 Data URI 前缀
            if base64_str.startswith('data:'):
                base64_str = base64_str.split(',', 1)

            # 解码
            image_data = base64.b64decode(base64_str)

            # 转换QByteArray
            byte_array = QByteArray(image_data)

            # 加载到 QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(byte_array)

            #转换为 QIcon 并存入池
            if not pixmap.isNull():
                self.pool[name] = QIcon(pixmap)

        except Exception as e:
            print(name,e)

    def get(self, name: str, default: QIcon = None) -> QIcon:
        """获取 QIcon 对象"""
        return self.pool.get(name, default)

# 单例
BIP = BaseIconPool()