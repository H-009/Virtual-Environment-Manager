from qtpy.QtWidgets import QVBoxLayout
from qfluentwidgets import SmoothScrollArea
from MetaverseSDK.MetaverseUI.MWidgets.MWidget import TransparentWidget


# 透明平滑滚动区域
class TransparentSmoothScrollArea(SmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWidgetResizable(True)  # 内部控件可调整大小
        self.setStyleSheet("QScrollArea{background: transparent; border: none}")  # 滚动区域透明

# 透明平滑滚动区域部件
class TransparentSmoothScrollAreaWidget(TransparentSmoothScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.view = TransparentWidget()
        self.setWidget(self.view) # 设置视图

        self.layout = QVBoxLayout(self.view) # 视图布局

    def addWidget(self,widget):
        self.layout.addWidget(widget)

    def addItem(self,item):
        self.layout.addItem(item)

