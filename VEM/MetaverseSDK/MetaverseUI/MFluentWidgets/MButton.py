from qtpy.QtGui import QPainter, QColor
from qtpy.QtCore import Qt, QRectF
from qfluentwidgets import PushButton


# 危险按钮
class DangerButton(PushButton):
    def __init__(self, text: str = "", parent=None):
        PushButton.__init__(self, parent)
        self.setText(text)
        self._radius = 6

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHints(QPainter.Antialiasing)

        if not self.isEnabled():
            c = QColor("#8a1c20")
            fg = QColor("#bbbbbb")
        elif self.isDown():
            c = QColor("#a82428")
            fg = QColor("white")
        elif self.underMouse():
            c = QColor("#c42b2f")
            fg = QColor("white")
        else:
            c = QColor("#d13438")
            fg = QColor("white")

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(c)
        p.drawRoundedRect(QRectF(self.rect()).adjusted(0.5,0.5,-0.5,-0.5), self._radius, self._radius)

        p.setPen(fg)
        p.setFont(self.font())
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())