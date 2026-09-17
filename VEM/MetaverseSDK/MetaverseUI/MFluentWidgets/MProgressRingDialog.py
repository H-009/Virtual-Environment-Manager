from qtpy.QtCore import Signal, Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, ProgressRing, FluentStyleSheet
from qfluentwidgets.components.dialog_box.dialog import Ui_MessageBox
from qframelesswindow import FramelessDialog


# 进度环对话框
class ProgressRingDialog(FramelessDialog, Ui_MessageBox):
    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str,max_num, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, title, self)
        self.max_num = max_num
        self.setModal(True)
        self.setResizeEnabled(False)
        self.resize(500, 400)
        self.titleBar.hide()

        self.buttonGroup.hide()
        self.titleLabel.hide()
        self.contentLabel.hide()

        v_layout = QVBoxLayout()
        v_layout.setSpacing(50)
        h = QHBoxLayout()
        label = TitleLabel(title)
        label.setFixedHeight(30)
        h.addWidget(label,alignment=Qt.AlignmentFlag.AlignHCenter)
        v_layout.addLayout(h)
        h2 = QHBoxLayout()
        self.spinner = ProgressRing()
        h2.addWidget(self.spinner)
        self.spinner.setFixedSize(150, 150)
        self.spinner.setMaximum(self.max_num)
        self.spinner.setFormat("0/"+str(self.max_num))
        self.spinner.setTextVisible(True)
        font = QFont("Microsoft YaHei", 13, QFont.Weight.Medium)
        self.spinner.setFont(font)
        v_layout.addLayout(h2)
        self.textLayout.addLayout(v_layout)

        FluentStyleSheet.DIALOG.apply(self)

    def set_num(self,num):
        self.spinner.setValue(num)
        self.spinner.setFormat(str(num)+"/"+str(self.max_num))

    def keyPressEvent(self, event):
        event.accept()  # 屏蔽按键
        return

# 字节进度环对话框
class ByteProgressRingDialog(FramelessDialog, Ui_MessageBox):
    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, title, self)
        self.setModal(True)
        self.setResizeEnabled(False)
        self.resize(500, 400)
        self.titleBar.hide()

        self.buttonGroup.deleteLater()
        self.titleLabel.hide()
        self.contentLabel.hide()

        v_layout = QVBoxLayout()
        v_layout.setSpacing(50)
        h = QHBoxLayout()
        label = TitleLabel(title)
        label.setFixedHeight(40)
        h.addWidget(label,alignment=Qt.AlignmentFlag.AlignHCenter)
        v_layout.addLayout(h)
        h2 = QHBoxLayout()
        self.spinner = ProgressRing()
        h2.addWidget(self.spinner)
        self.spinner.setFixedSize(150, 150)
        self.spinner.setTextVisible(True)
        self.spinner.setFormat("0MB/0MB")
        font = QFont("Microsoft YaHei", 13, QFont.Weight.Medium)
        self.spinner.setFont(font)
        v_layout.addLayout(h2)
        self.textLayout.addLayout(v_layout)

        FluentStyleSheet.DIALOG.apply(self)

    def set_num(self,num,max_num):
        self.spinner.setValue(num)
        self.spinner.setMaximum(max_num)
        self.spinner.setFormat(f"{num / (1024 * 1024):.1f}MB/{max_num / (1024 * 1024):.1f}MB")

    def keyPressEvent(self, event):
        event.accept()  # 屏蔽按键
        return