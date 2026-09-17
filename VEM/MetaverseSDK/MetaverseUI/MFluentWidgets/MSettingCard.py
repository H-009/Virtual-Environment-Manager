from qtpy.QtCore import Signal, QPropertyAnimation, Property, Qt
from qtpy.QtGui import QPainter, QColor
from qtpy.QtWidgets import QLabel
from qfluentwidgets import SettingCard, FluentIcon, isDarkTheme, SwitchButton, PushButton, ComboBox


# 字幕设置卡片
class SubtitleSettingCard(SettingCard):
    """更大布局的设置卡片"""

    def __init__(self, icon, title, content=None, parent=None):
        super().__init__(icon, title, content, parent)

        self.setIconSize(24, 24)
        self.hBoxLayout.setContentsMargins(20, 15, 20, 15)

        self.titleLabel.setFixedHeight(20)
        self.contentLabel.setFixedHeight(16)

    def addWidget(self,widget):
        self.hBoxLayout.addWidget(widget)

    def setTitleHeight(self,h):
        self.titleLabel.setFixedHeight(h)

    def setContentHeight(self,h):
        self.contentLabel.setFixedHeight(h)

# 动画跳转设置卡片
class AnimationJumpSettingCard(SubtitleSettingCard):
    """带右箭头的跳转卡片，支持 hover / pressed 三态高亮（带动画）"""

    clicked = Signal()

    def __init__(self, icon, title, content=None, parent=None,time=80):
        super().__init__(icon, title, content, parent)

        self.chevron_icon = QLabel(self)
        self.chevron_icon.setFixedSize(15, 15)
        self.chevron_icon.setPixmap(FluentIcon.CHEVRON_RIGHT.icon().pixmap(15, 15))
        self.addWidget(self.chevron_icon)

        # 动画相关
        self._bg_alpha = 0.0
        self._anim = QPropertyAnimation(self, b"bg_alpha", self)
        self._anim.setDuration(time)

    # ---------- 属性动画 ----------
    def get_bg_alpha(self):
        return self._bg_alpha

    def set_bg_alpha(self, v):
        self._bg_alpha = v
        self.update()

    bg_alpha_changed = Signal(float)
    bg_alpha = Property(
        float,
        get_bg_alpha,
        set_bg_alpha,
        notify=bg_alpha_changed
    )

    def _animate_to(self, target):
        self._anim.stop()
        self._anim.setStartValue(self._bg_alpha)
        self._anim.setEndValue(target)
        self._anim.start()

    # ---------- 状态事件（驱动动画）----------
    def enterEvent(self, e):
        if self.isEnabled():
            self._animate_to(1.0)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._animate_to(0.0)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if self.isEnabled() and e.button() == Qt.MouseButton.LeftButton:
            self._animate_to(1.6)
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if self.isEnabled() and e.button() == Qt.MouseButton.LeftButton:
            self._animate_to(1.0)
            self.clicked.emit()
        super().mouseReleaseEvent(e)

    # ---------- 绘制 ----------
    def paintEvent(self, event):
        super().paintEvent(event)
        if self._bg_alpha <= 0.01:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if isDarkTheme():
            base = QColor(255, 255, 255)
            max_a = 22
        else:
            base = QColor(0, 0, 0)
            max_a = 16

        alpha = int(max_a * min(self._bg_alpha, 1.6) / 1.6)
        base.setAlpha(alpha)
        painter.setBrush(base)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)

# 跳转设置卡片
class JumpSettingCard(SubtitleSettingCard):
    """带右箭头的跳转卡片，支持 hover / pressed 三态高亮（不带动画，即时生效）"""

    clicked = Signal()

    def __init__(self, icon, title, content=None, parent=None):
        super().__init__(icon, title, content, parent)

        self.chevron_icon = QLabel(self)
        self.chevron_icon.setFixedSize(15, 15)
        self.chevron_icon.setPixmap(FluentIcon.CHEVRON_RIGHT.icon().pixmap(15, 15))
        self.addWidget(self.chevron_icon)

        # 三态对应的 alpha 档位（0=普通, 1=hover, 2=pressed）
        self._state = 0  # 0/1/2

    # ---------- 状态事件（直接赋值，无动画）----------
    def enterEvent(self, e):
        if self.isEnabled():
            self._state = 1
            self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._state = 0
        self.update()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if self.isEnabled() and e.button() == Qt.MouseButton.LeftButton:
            self._state = 2
            self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if self.isEnabled() and e.button() == Qt.MouseButton.LeftButton:
            self._state = 1
            self.clicked.emit()
        super().mouseReleaseEvent(e)

    # ---------- 绘制 ----------
    def paintEvent(self, event):
        super().paintEvent(event)
        if self._state == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if isDarkTheme():
            base = QColor(255, 255, 255)
            max_a = 22
        else:
            base = QColor(0, 0, 0)
            max_a = 16

        # 按下更深，悬停较浅
        alpha = int(max_a * (1.6 if self._state == 2 else 1.0) / 1.6)
        base.setAlpha(alpha)
        painter.setBrush(base)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)

# 简单跳转设置卡片
class SimpleJumpSettingCard(SubtitleSettingCard):
    """带右箭头的跳转卡片，支持 hover / pressed 三态高亮（不带动画，即时生效）"""

    clicked = Signal()

    def __init__(self, icon, title, content=None, parent=None):
        super().__init__(icon, title, content, parent)

        self.contentLabel.hide()
        self.hBoxLayout.setContentsMargins(20, 25, 20, 25)

        self.chevron_icon = QLabel(self)
        self.chevron_icon.setFixedSize(15, 15)
        self.chevron_icon.setPixmap(FluentIcon.CHEVRON_RIGHT.icon().pixmap(15, 15))
        self.addWidget(self.chevron_icon)

        # 三态对应的 alpha 档位（0=普通, 1=hover, 2=pressed）
        self._state = 0  # 0/1/2

    # ---------- 状态事件（直接赋值，无动画）----------
    def enterEvent(self, e):
        if self.isEnabled():
            self._state = 1
            self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._state = 0
        self.update()
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if self.isEnabled() and e.button() == Qt.MouseButton.LeftButton:
            self._state = 2
            self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if self.isEnabled() and e.button() == Qt.MouseButton.LeftButton:
            self._state = 1
            self.clicked.emit()
        super().mouseReleaseEvent(e)

    # ---------- 绘制 ----------
    def paintEvent(self, event):
        super().paintEvent(event)
        if self._state == 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if isDarkTheme():
            base = QColor(255, 255, 255)
            max_a = 22
        else:
            base = QColor(0, 0, 0)
            max_a = 16

        # 按下更深，悬停较浅
        alpha = int(max_a * (1.6 if self._state == 2 else 1.0) / 1.6)
        base.setAlpha(alpha)
        painter.setBrush(base)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)

# 开关按钮设置卡
class SwitchButtonSettingCard(SubtitleSettingCard):

    checkedChanged = Signal(bool)

    def __init__(self, icon, title, content=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.switch = SwitchButton()
        self.addWidget(self.switch)

        self.switch.checkedChanged.connect(self.onCheckedChanged)

    def onCheckedChanged(self, isChecked):
        self.checkedChanged.emit(isChecked)

    def isChecked(self):
        return self.switch.isChecked()

    def setChecked(self, isChecked):
        self.switch.setChecked(isChecked)

    def toggleChecked(self):
        self.switch.setChecked(not self.switch.isChecked())

# 按钮设置卡
class ButtonSettingCard(SubtitleSettingCard):

    clicked = Signal()

    def __init__(self, icon, title, content=None, text=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.button = PushButton(text)
        self.button.setMinimumWidth(120)
        self.addWidget(self.button)

        self.button.clicked.connect(self.onClicked)

    def onClicked(self):
        self.clicked.emit()

    def setText(self,text):
        self.button.setText(text)

    def getText(self):
        return self.button.text()

# 组合框设置卡
class ComboBoxSettingCard(SubtitleSettingCard):

    currentIndexChanged = Signal(int)
    currentTextChanged = Signal(str)

    def __init__(self, icon, title, content=None, parent=None):
        super().__init__(icon, title, content, parent)
        self.comboBox = ComboBox()
        self.comboBox.setMinimumWidth(120)
        self.addWidget(self.comboBox)

        self.comboBox.currentIndexChanged.connect(self.onIndexChanged)
        self.comboBox.currentTextChanged.connect(self.onTextChanged)

    def onIndexChanged(self,index):
        self.currentIndexChanged.emit(index)

    def onTextChanged(self,text):
        self.currentTextChanged.emit(text)

    def setCurrentIndex(self, index):
        self.comboBox.setCurrentIndex(index)

    def setCurrentText(self, text):
        self.comboBox.setCurrentText(text)

    def getCurrentIndex(self):
        return self.comboBox.currentIndex()

    def getCurrentText(self):
        return self.comboBox.currentText()

    def addItems(self, items):
        self.comboBox.addItems(items)

