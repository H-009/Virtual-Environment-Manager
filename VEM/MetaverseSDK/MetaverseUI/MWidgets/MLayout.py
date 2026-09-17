from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout

# 水平布局
class HLayout(QHBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置上下左右空间
        self.setContentsMargins(0, 0, 0, 0)
        # 设置间隔
        self.setSpacing(0)

# 垂直布局
class VLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置上下左右空间
        self.setContentsMargins(0, 0, 0, 0)
        # 设置间隔
        self.setSpacing(0)