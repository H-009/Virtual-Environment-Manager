from qfluentwidgets import isDarkTheme
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor, QPainter
from qtpy.QtWidgets import QToolButton
from qtpy.QtCore import Signal
from MetaverseSDK.MetaverseUI.MFluentWidgets.MColorDialog import NoMaskColorDialog


# 无遮罩颜色选择器按钮
class NoMaskColorPickerButton(QToolButton):

    colorChanged = Signal(QColor)

    def __init__(self, color: QColor, title: str, parent=None, enableAlpha=False):
        super().__init__(parent=parent)
        self.title = title
        self.enableAlpha = enableAlpha
        self.setFixedSize(96, 32)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setColor(color)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self.__showColorDialog)

    def __showColorDialog(self):
        w = NoMaskColorDialog(self.color, "选择"+self.title, self.window(), self.enableAlpha)
        w.colorChanged.connect(self.__onColorChanged)
        w.exec()

    def __onColorChanged(self, color):
        self.setColor(color)
        self.colorChanged.emit(color)

    def setColor(self, color):
        self.color = QColor(color)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        pc = QColor(255, 255, 255, 10) if isDarkTheme() else QColor(234, 234, 234)
        painter.setPen(pc)

        color = QColor(self.color)
        if not self.enableAlpha:
            color.setAlpha(255)

        painter.setBrush(color)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 5, 5)