from qtpy.QtCore import Signal, Qt, QTimer
from qtpy.QtWidgets import QLabel, QVBoxLayout, QSizePolicy, QHBoxLayout, QFileDialog
from qfluentwidgets import BodyLabel, SingleDirectionScrollArea, SimpleCardWidget, FluentStyleSheet, LineEdit, TextEdit,\
    ToolButton, FluentIcon, Dialog
from qfluentwidgets.components.dialog_box.dialog import Ui_MessageBox
from qframelesswindow import FramelessDialog

# 对话框



# 快速命令对话框
class QuickCommandDialog(FramelessDialog, Ui_MessageBox):
    """ Dialog box """

    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(500, 400)
        self.titleBar.hide()

        self.textLayout.setSpacing(5)

        self.yesButton.setText("应用")
        self.cancelButton.setText("取消")

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')

        self.description_label = BodyLabel()
        self.textLayout.addWidget(self.description_label)

        self.older_label = BodyLabel()
        self.textLayout.addWidget(self.older_label)

        self.scrollArea = SingleDirectionScrollArea(orient=Qt.Orientation.Vertical)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scrollArea_card_layout = QVBoxLayout()

        self.scrollArea_card = SimpleCardWidget()
        self.scrollArea_card.setLayout(self.scrollArea_card_layout)
        self.scrollArea_card.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.MinimumExpanding
        )

        self.scrollArea.setWidget(self.scrollArea_card)
        self.scrollArea.enableTransparentBackground() # 滚动区域全面透明
        self.textLayout.addWidget(self.scrollArea)

        FluentStyleSheet.DIALOG.apply(self)

    def setTitleBarVisible(self, isVisible: bool):
        self.windowTitleLabel.setVisible(isVisible)

# 通知对话框
class NotificationDialog(FramelessDialog, Ui_MessageBox):

    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(240, 192)
        self.titleBar.hide()

        # 确定通知
        self.yesButton.setText("明白👌")
        # 隐藏取消按钮
        self.cancelButton.hide()

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

# 行对话框
class LineDialog(FramelessDialog, Ui_MessageBox):

    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(500, 200)
        self.titleBar.hide()

        self.line = LineEdit()
        self.line.setMinimumWidth(120)
        self.textLayout.addWidget(self.line)

        self.yesButton.setText("确定")
        self.cancelButton.setText("取消")

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

# 文本编辑对话框
class TextEditDialog(FramelessDialog, Ui_MessageBox):

    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(500, 200)
        self.titleBar.hide()

        self.line = TextEdit()
        self.line.setMinimumWidth(120)
        self.line.setMinimumHeight(200)
        self.textLayout.addWidget(self.line)

        self.yesButton.setText("确定")
        self.cancelButton.setText("取消")

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

# 工作目录选择行对话框
class WorkingDirectorySelectLineDialog(FramelessDialog, Ui_MessageBox):

    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str, content: str,text="", parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(500, 200)
        self.titleBar.hide()

        self.line = LineEdit()
        self.line.setText(text)
        self.line.setMinimumWidth(120)
        self.textLayout.addWidget(self.line)

        layout = QHBoxLayout()
        self.line_dir = LineEdit()
        self.line_dir.setMinimumWidth(120)
        self.line_dir.setText("C:\\")
        layout.addWidget(self.line_dir)
        button = ToolButton(FluentIcon.FOLDER)  # 图标按钮
        button.clicked.connect(self.open_window)
        layout.addWidget(button)

        self.textLayout.addLayout(layout)

        self.yesButton.setText("确定")
        self.cancelButton.setText("取消")

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

    def open_window(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "选择 工作目录",
            "C:/"
        )
        if path != '':
            self.line_dir.setText(path)

# 行字典对话框
class LineDictDialog(FramelessDialog, Ui_MessageBox):
    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(500, 200)
        self.titleBar.hide()

        self.line = LineEdit()
        self.line.setMinimumWidth(120)
        self.textLayout.addWidget(self.line)

        dict_layout = QHBoxLayout()
        self.texteditL = TextEdit()
        self.texteditL.setMinimumWidth(60)
        dict_layout.addWidget(self.texteditL)
        self.texteditR = TextEdit()
        self.texteditR.setMinimumWidth(60)
        dict_layout.addWidget(self.texteditR)
        self.textLayout.addLayout(dict_layout)

        self.yesButton.setText("确定")
        self.cancelButton.setText("取消")

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignmentFlag.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

# 危险倒计时对话框
class DangerCountdownDialog(Dialog):
    def __init__(
        self,
        title: str,
        content: str,
        parent=None,
        countdown_seconds: int = 5,
        text: str = "确认",
    ):
        super().__init__(title, content, parent)

        self.countdown_seconds = countdown_seconds
        self.remaining = countdown_seconds
        self.text = text

        self.yesButton.setText(f"{text}({countdown_seconds}s)")
        self.yesButton.setEnabled(False)
        self.yesButton.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c42b2f;
            }
            QPushButton:pressed {
                background-color: #a82428;
            }
            QPushButton:disabled {
                background-color: #8a1c20;
                color: #cccccc;
            }
        """)

        self.cancelButton.setText("取消")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

    def update_countdown(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.timer.stop()
            self.yesButton.setEnabled(True)
            self.yesButton.setText(self.text)
        else:
            self.yesButton.setText(f"{self.text}({self.remaining}s)")