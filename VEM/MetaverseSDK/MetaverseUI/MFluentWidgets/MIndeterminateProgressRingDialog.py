from qtpy.QtCore import Signal, Qt
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import FluentStyleSheet, TitleLabel, IndeterminateProgressRing
from qfluentwidgets.components.dialog_box.dialog import Ui_MessageBox
from qframelesswindow import FramelessDialog

from MetaverseSDK.MetaverseUI.MFluentWidgets.MIndeterminateProgressRing import FixedLengthIndeterminateProgressRing, \
    CometTailIndeterminateProgressRing, MultipleArcsIndeterminateProgressRing, SegmentedArcIndeterminateProgressRing


# 不确定进度环对话框

# 不确定进度环对话框
class IndeterminateProgressRingDialog(FramelessDialog, Ui_MessageBox):
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
        self.label = TitleLabel(title)
        self.label.setFixedHeight(40)
        h.addWidget(self.label,alignment=Qt.AlignmentFlag.AlignHCenter)
        v_layout.addLayout(h)
        h2 = QHBoxLayout()
        spinner = IndeterminateProgressRing()
        h2.addWidget(spinner)
        spinner.setFixedSize(150, 150)
        v_layout.addLayout(h2)
        self.textLayout.addLayout(v_layout)

        FluentStyleSheet.DIALOG.apply(self)

    def keyPressEvent(self, event):
        event.accept()  # 屏蔽按键
        return

# 固定长度不确定进度环对话框
class FixedLengthIndeterminateProgressRingDialog(FramelessDialog, Ui_MessageBox):
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
        self.label = TitleLabel(title)
        self.label.setFixedHeight(40)
        h.addWidget(self.label,alignment=Qt.AlignmentFlag.AlignHCenter)
        v_layout.addLayout(h)
        h2 = QHBoxLayout()
        spinner = FixedLengthIndeterminateProgressRing()
        h2.addWidget(spinner)
        spinner.setFixedSize(150, 150)

        #spinner.setStrokeWidth()
        v_layout.addLayout(h2)
        #v_layout.addLayout(h_layout)
        self.textLayout.addLayout(v_layout)

        FluentStyleSheet.DIALOG.apply(self)

    def keyPressEvent(self, event):
        event.accept()  # 屏蔽按键
        return

# 彗星拖尾不确定进度环对话框
class CometTailIndeterminateProgressRingDialog(FramelessDialog, Ui_MessageBox):
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
        self.label = TitleLabel(title)
        self.label.setFixedHeight(40)
        h.addWidget(self.label,alignment=Qt.AlignmentFlag.AlignHCenter)
        v_layout.addLayout(h)
        h2 = QHBoxLayout()
        spinner = CometTailIndeterminateProgressRing()
        h2.addWidget(spinner)
        spinner.setFixedSize(150, 150)

        v_layout.addLayout(h2)
        self.textLayout.addLayout(v_layout)

        FluentStyleSheet.DIALOG.apply(self)

    def keyPressEvent(self, event):
        event.accept()  # 屏蔽按键
        return

# 多段弧不确定进度环对话框
class MultipleArcsIndeterminateProgressRingDialog(FramelessDialog, Ui_MessageBox):
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
        self.label = TitleLabel(title)
        self.label.setFixedHeight(40)
        h.addWidget(self.label,alignment=Qt.AlignmentFlag.AlignHCenter)
        v_layout.addLayout(h)
        h2 = QHBoxLayout()
        spinner = MultipleArcsIndeterminateProgressRing()
        h2.addWidget(spinner)
        spinner.setFixedSize(150, 150)

        v_layout.addLayout(h2)
        self.textLayout.addLayout(v_layout)

        FluentStyleSheet.DIALOG.apply(self)

    def keyPressEvent(self, event):
        event.accept()  # 屏蔽按键
        return

# 段式弧不确定进度环对话框
class SegmentedArcIndeterminateProgressRingDialog(FramelessDialog, Ui_MessageBox):
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
        self.label = TitleLabel(title)
        self.label.setFixedHeight(40)
        h.addWidget(self.label,alignment=Qt.AlignmentFlag.AlignHCenter)
        v_layout.addLayout(h)
        h2 = QHBoxLayout()
        spinner = SegmentedArcIndeterminateProgressRing()
        h2.addWidget(spinner)
        spinner.setFixedSize(150, 150)

        v_layout.addLayout(h2)
        self.textLayout.addLayout(v_layout)

        FluentStyleSheet.DIALOG.apply(self)

    def keyPressEvent(self, event):
        event.accept()  # 屏蔽按键
        return