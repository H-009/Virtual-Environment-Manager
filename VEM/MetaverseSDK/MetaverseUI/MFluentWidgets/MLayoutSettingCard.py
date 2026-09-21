from qtpy.QtCore import Qt,QUrl,Signal
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import SimpleCardWidget, IconWidget, BodyLabel, CaptionLabel, SwitchButton, HyperlinkButton, \
    HyperlinkLabel, PushButton, PrimaryPushButton
from MetaverseSDK.MetaverseUI.MFluentWidgets.MButton import DangerButton


# 布局式设置卡片
class LayoutSettingCard(SimpleCardWidget):
    def __init__(self,ico,title,content):
        super().__init__()

        self.hBoxLayout = QHBoxLayout()  # 水平布局
        self.hBoxLayout.setContentsMargins(20, 10, 10, 10)
        self.hBoxLayout.setSpacing(15)
        self.iconWidget = IconWidget(ico)  # 图标界面
        self.iconWidget.setFixedSize(24, 24)
        self.vBoxLayout = QVBoxLayout()  # 垂直布局
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(BodyLabel(title))  # 文字标签
        self.contentLabel = CaptionLabel(content)  # 字幕标签
        self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.vBoxLayout.addWidget(self.contentLabel)
        self.hBoxLayout.addWidget(self.iconWidget)  # 添加到布局
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.setLayout(self.hBoxLayout)  # 设置卡片布局
        self.setFixedHeight(70)

# 布局式开关按钮设置卡片
class LayoutSwitchButtonSettingCard(LayoutSettingCard):

    checkedChanged = Signal(bool)

    def __init__(self,ico,title,content):
        super().__init__(ico,title,content)

        self.switch = SwitchButton()
        self.switch.setFixedWidth(80)
        self.switch.checkedChanged.connect(self.onCheckedChanged)
        self.hBoxLayout.addWidget(self.switch)

    def onCheckedChanged(self, isChecked):
        self.checkedChanged.emit(isChecked)

    def setChecked(self,isChecked):
        self.switch.setChecked(isChecked)

# 布局式按钮设置卡片
class LayoutButtonSettingCard(LayoutSettingCard):

    clickedChanged = Signal(bool)

    def __init__(self, ico, title, content, text):
        super().__init__(ico, title, content)

        self.btn = PushButton(text)
        self.btn.setFixedWidth(120)
        self.btn.clicked.connect(self.onClickedChanged)
        self.hBoxLayout.addWidget(self.btn)

    def onClickedChanged(self,isChanged):
        self.clickedChanged.emit(isChanged)

# 布局式主题色按钮设置卡片
class LayoutPrimaryButtonSettingCard(LayoutSettingCard):

    clickedChanged = Signal(bool)

    def __init__(self, ico, title, content, text):
        super().__init__(ico, title, content)

        self.btn = PrimaryPushButton(text)
        self.btn.setFixedWidth(120)
        self.btn.clicked.connect(self.onClickedChanged)
        self.hBoxLayout.addWidget(self.btn)

    def onClickedChanged(self,isChanged):
        self.clickedChanged.emit(isChanged)

# 布局式超链接按钮设置卡片
class LayoutHyperlinkButtonSettingCard(LayoutSettingCard):
    def __init__(self, ico, title, content, text, url=""):
        super().__init__(ico, title, content)

        self.linkBtn = HyperlinkButton(url, text, self)
        self.linkBtn.setFixedWidth(120)
        self.linkBtn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hBoxLayout.addWidget(self.linkBtn)

# 布局式危险按钮设置卡片
class LayoutDangerButtonSettingCard(LayoutSettingCard):

    clickedChanged = Signal(bool)

    def __init__(self, ico, title, content, text):
        super().__init__(ico, title, content)

        self.btn = DangerButton(text)
        self.btn.setFixedWidth(120)
        self.btn.clicked.connect(self.onClickedChanged)
        self.hBoxLayout.addWidget(self.btn)

    def onClickedChanged(self,isChecked):
        self.clickedChanged.emit(isChecked)

# 布局式超链接标签设置卡片
class LayoutHyperlinkLabelSettingCard(LayoutSettingCard):

    clickedChanged = Signal(bool)

    def __init__(self, ico, title, content,):
        super().__init__(ico, title, content)

        self.contentLabel.hide()

        self.label = HyperlinkLabel(content)
        self.vBoxLayout.addWidget(self.label)

    def setUrl(self,url):
        self.label.setUrl(url)

    def setFileUrl(self,file):
        self.setUrl(QUrl.fromLocalFile(file))

    def setFolderUrl(self,folder):
        self.label.setUrl(QUrl.fromLocalFile(folder))

    def setUnderlineVisible(self,v):
        self.label.setUnderlineVisible(v)