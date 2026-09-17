from qtpy.QtCore import Qt
from qfluentwidgets import TreeWidget

# 树形控件



# 禁用箭头树形控件
class ArrowsProhibitedTreeWidget(TreeWidget):
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Down, Qt.Key.Key_Up,Qt.Key.Key_Left,Qt.Key.Key_Right):
            # 不调用父类 → 禁止方向键选择
            # 但其他键仍可用 Home End PgUp PgDn
            return
        super().keyPressEvent(event)

# 禁用全部键树形控件
class AllKeyProhibitedTreeWidget(TreeWidget):
    # 禁用全部键
    def keyPressEvent(self, event):
        event.accept()  # 标记事件已处理，不再传播或执行默认行为
        return
