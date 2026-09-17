from qtpy.QtWidgets import QHeaderView
from qfluentwidgets import TableWidget


# 圆角表格列表控件
class RoundedTableListWidget(TableWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setWordWrap(False)  # 不自动换行
        self.setSelectRightClickedRow(True)  # 右击选中
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # 行随控件大小实时跟随内容
        self.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)  # 整张表不可编辑

        # 启用边框并设置圆角
        self.setBorderVisible(True)
        self.setBorderRadius(8)
