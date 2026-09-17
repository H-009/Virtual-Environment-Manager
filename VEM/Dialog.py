from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from qfluentwidgets import IconWidget, BodyLabel, FluentStyleSheet, TextEdit
from qfluentwidgets.components.dialog_box.dialog import Ui_MessageBox
from qframelesswindow import FramelessDialog


# Python详情对话框
class DetailsPythonDialog(FramelessDialog, Ui_MessageBox):

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, svg,t1,t2,t3,s1,s2,parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, "", self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(340, 192)
        self.titleBar.hide()
        self.contentLabel.hide()
        self.titleLabel.hide()

        self.hlayout = QHBoxLayout()
        svg = IconWidget(svg)
        svg.setFixedSize(100,100)
        self.hlayout.addWidget(svg)
        self.vlayout = QVBoxLayout()
        self.hlayout.addLayout(self.vlayout)

        self.vlayout.addWidget(BodyLabel(t1))
        self.vlayout.addWidget(BodyLabel(t2))
        self.vlayout.addWidget(BodyLabel(t3))
        self.vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.textLayout.addLayout(self.hlayout)

        self.textLayout.addWidget(BodyLabel(s1))
        self.textLayout.addWidget(BodyLabel(s2))

        self.yesButton.setText("确定")
        self.cancelButton.hide()

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

# Emb详情对话框
class DetailsEmbDialog(FramelessDialog, Ui_MessageBox):

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, svg,t1,t2,t3,s1,s2,s3,parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, "", self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(340, 192)
        self.titleBar.hide()
        self.contentLabel.hide()
        self.titleLabel.hide()

        self.hlayout = QHBoxLayout()
        svg = IconWidget(svg)
        svg.setFixedSize(100,100)
        self.hlayout.addWidget(svg)
        self.vlayout = QVBoxLayout()
        self.hlayout.addLayout(self.vlayout)

        self.vlayout.addWidget(BodyLabel(t1))
        self.vlayout.addWidget(BodyLabel(t2))
        self.vlayout.addWidget(BodyLabel(t3))
        self.vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.textLayout.addLayout(self.hlayout)

        self.textLayout.addWidget(BodyLabel(s1))
        self.textLayout.addWidget(BodyLabel(s2))
        self.textLayout.addWidget(BodyLabel(s3))

        self.yesButton.setText("确定")
        self.cancelButton.hide()

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

# Venv详情对话框
class DetailsVenvDialog(FramelessDialog, Ui_MessageBox):

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, svg,t1,t2,t3,s1,s2,s3,s4,s5,parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, "", self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(340, 192)
        self.titleBar.hide()
        self.contentLabel.hide()
        self.titleLabel.hide()

        self.hlayout = QHBoxLayout()
        svg = IconWidget(svg)
        svg.setFixedSize(100,100)
        self.hlayout.addWidget(svg)
        self.vlayout = QVBoxLayout()
        self.hlayout.addLayout(self.vlayout)

        self.vlayout.addWidget(BodyLabel(t1))
        self.vlayout.addWidget(BodyLabel(t2))
        self.vlayout.addWidget(BodyLabel(t3))
        self.vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.textLayout.addLayout(self.hlayout)

        self.textLayout.addWidget(BodyLabel(s1))
        self.textLayout.addWidget(BodyLabel(s2))
        self.textLayout.addWidget(BodyLabel(s3))
        self.textLayout.addWidget(BodyLabel(s4))
        self.textLayout.addWidget(BodyLabel(s5))

        self.yesButton.setText("确定")
        self.cancelButton.hide()

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

# 配置文件详情对话框
class DetailsConfigDialog(FramelessDialog, Ui_MessageBox):

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, svg,t1,t2,t3,parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, "", self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(340, 192)
        self.titleBar.hide()
        self.contentLabel.hide()
        self.titleLabel.hide()

        self.hlayout = QHBoxLayout()
        svg = IconWidget(svg)
        svg.setFixedSize(100,100)
        self.hlayout.addWidget(svg)
        self.vlayout = QVBoxLayout()
        self.hlayout.addLayout(self.vlayout)

        self.vlayout.addWidget(BodyLabel(t1))
        self.vlayout.addWidget(BodyLabel(t2))
        self.vlayout.addWidget(BodyLabel(t3))
        self.vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.textLayout.addLayout(self.hlayout)

        self.textedit = TextEdit()
        self.textedit.setMinimumWidth(200)
        self.textedit.setMinimumHeight(150)
        self.textedit.setReadOnly(True)
        self.textLayout.addWidget(self.textedit)

        self.yesButton.setText("确定")
        self.cancelButton.hide()

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

# 预设脚本详情对话框
class DetailsPresetScriptsDialog(FramelessDialog, Ui_MessageBox):

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, svg,t1,t2,t3,t4,t5,parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, "", self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(340, 192)
        self.titleBar.hide()
        self.contentLabel.hide()
        self.titleLabel.hide()

        self.hlayout = QHBoxLayout()
        svg = IconWidget(svg)
        svg.setFixedSize(100,100)
        self.hlayout.addWidget(svg)
        self.vlayout = QVBoxLayout()
        self.hlayout.addLayout(self.vlayout)

        self.vlayout.addWidget(BodyLabel(t1))
        self.vlayout.addWidget(BodyLabel(t2))
        self.vlayout.addWidget(BodyLabel(t3))
        self.vlayout.addWidget(BodyLabel(t4))
        self.vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.textLayout.addLayout(self.hlayout)

        self.textLayout.addWidget(BodyLabel(t5))
        self.textedit = TextEdit()
        self.textedit.setMinimumWidth(200)
        self.textedit.setMinimumHeight(150)
        self.textedit.setReadOnly(True)
        self.textLayout.addWidget(self.textedit)

        self.yesButton.setText("确定")
        self.cancelButton.hide()

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())

# 图钉详情对话框
class DetailsPinDialog(FramelessDialog, Ui_MessageBox):

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, svg,t1,t2,parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, "", self)

        self.windowTitleLabel = QLabel(title, self)

        self.setResizeEnabled(False)
        self.resize(340, 192)
        self.titleBar.hide()
        self.contentLabel.hide()
        self.titleLabel.hide()

        self.hlayout = QHBoxLayout()
        svg = IconWidget(svg)
        svg.setFixedSize(100,100)
        self.hlayout.addWidget(svg)
        self.vlayout = QVBoxLayout()
        self.hlayout.addLayout(self.vlayout)

        self.vlayout.addWidget(BodyLabel(t1))
        self.vlayout.addWidget(BodyLabel(t2))
        self.vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.textLayout.addLayout(self.hlayout)

        self.yesButton.setText("确定")
        self.cancelButton.hide()

        self.vBoxLayout.insertWidget(0, self.windowTitleLabel, 0, Qt.AlignTop)
        self.windowTitleLabel.setObjectName('windowTitleLabel')
        FluentStyleSheet.DIALOG.apply(self)
        self.setFixedSize(self.size())