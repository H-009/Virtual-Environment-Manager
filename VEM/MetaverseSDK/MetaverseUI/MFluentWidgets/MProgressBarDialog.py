from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import TitleLabel, ProgressBar, BodyLabel, FluentStyleSheet
from qfluentwidgets.components.dialog_box.dialog import Ui_MessageBox
from qframelesswindow import FramelessDialog

# 进度条对话框



# 进度条对话框
class ProgressBarDialog(FramelessDialog, Ui_MessageBox):
    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, title, self)
        self.setModal(True)
        self.setResizeEnabled(False)
        self.resize(500, 200)
        self.titleBar.hide()

        self.buttonGroup.deleteLater()
        self.titleLabel.hide()
        self.contentLabel.hide()

        v_layout = QVBoxLayout()
        v_layout.setSpacing(50)
        h = QHBoxLayout()
        self.label = TitleLabel(title)
        self.label.setFixedHeight(40)
        h.addWidget(self.label,alignment=Qt.AlignmentFlag.AlignHCenter)
        v_layout.addLayout(h)
        h2 = QHBoxLayout()
        self.progress_bar = ProgressBar()
        self.progress_bar.setMaximum(100)
        h2.addWidget(self.progress_bar)

        v_layout.addLayout(h2)
        self.textLayout.addLayout(v_layout)
        self.label_R = BodyLabel()
        self.label_R.setFixedHeight(30)
        self.textLayout.addWidget(self.label_R,alignment=Qt.AlignmentFlag.AlignHCenter)

        FluentStyleSheet.DIALOG.apply(self)

    def keyPressEvent(self, event):
        event.accept()  # 屏蔽按键
        return