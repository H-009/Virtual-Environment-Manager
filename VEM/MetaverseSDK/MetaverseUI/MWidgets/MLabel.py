import os
from qtpy.QtCore import Signal, Qt, QUrl, QRectF
from qtpy.QtGui import QDesktopServices, QPainterPath, QPainter
from qtpy.QtWidgets import QLabel


# 超链接文件标签
class HyperlinkFileLabel(QLabel):
    """
    超链接标签：
    1. 支持自定义颜色
    2. 鼠标悬停时显示下划线，移开时隐藏
    3. 点击时使用系统默认应用打开指定文件
    4. 支持动态设置文本颜色
    """

    # 定义一个信号，方便外部监听点击事件
    linkClicked = Signal(str)

    def __init__(self, text="链接", file_path="", color="#62b3eb", parent=None):
        super().__init__(text, parent)

        # 属性初始化
        self._file_path = file_path
        self._normal_color = color
        self._hover_color = color  # 悬停时的颜色，通常可以加深或保持一致
        self._is_hovered = False  # 跟踪鼠标状态，用于刷新样式

        # 基础样式设置
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # 鼠标变成手型
        self.setTextFormat(Qt.TextFormat.RichText)  # 启用富文本
        self.setOpenExternalLinks(False)  # 禁用自动打开，由我们手动控制

        # 应用初始样式
        self._apply_style()

    def set_file_path(self, path):
        """设置要打开的文件路径"""
        self._file_path = path

    def set_text_color(self, color):
        """
        设置文本颜色

        :param color: 正常状态下的颜色 (str, e.g., "#0078D4" or "blue")
        """
        self._normal_color = color
        self._hover_color = color

        # 重新应用样式以反映颜色变化
        self._apply_style()

    def _apply_style(self):
        """根据当前鼠标状态和颜色设置应用样式"""
        underline = "underline" if self._is_hovered else "none"

        # 注意：QLabel 的 QSS 对伪状态支持有时不稳定，
        # 这里我们主要依靠 enterEvent/leaveEvent 强制刷新，
        # 但保留 QSS 结构作为基础。
        self.setStyleSheet(f"""
                color: {self._normal_color};
                text-decoration: {underline};
                background-color: transparent;
                border: none;
        """)

    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        self._is_hovered = True
        # 强制刷新样式以确保下划线出现且颜色正确
        self.setStyleSheet(f"""
                color: {self._hover_color};
                text-decoration: underline;
        """)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        self._is_hovered = False
        # 恢复无下划线样式和正常颜色
        self.setStyleSheet(f"""
                color: {self._normal_color};
                text-decoration: none;
        """)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._file_path and os.path.exists(self._file_path):
                # 发射信号
                self.linkClicked.emit(self._file_path)
                # 执行打开操作
                QDesktopServices.openUrl(QUrl.fromLocalFile(self._file_path))
            else:
                print(f"文件不存在或路径未设置: {self._file_path}")
        super().mousePressEvent(event)

# 圆角标签
class RoundedLabel(QLabel):
    def __init__(self, radius=12, parent=None):
        super().__init__(parent)
        self._radius = radius

    def setRadius(self, radius):
        self._radius = radius

    def paintEvent(self, event):
        if self.pixmap() and not self.pixmap().isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            # 用圆角矩形路径做裁剪
            path = QPainterPath()
            rect = QRectF(self.rect())
            path.addRoundedRect(rect, self._radius, self._radius)

            painter.setClipPath(path)
            painter.drawPixmap(0, 0, self.width(), self.height(), self.pixmap())
        else:
            super().paintEvent(event)

# 图像标签
class ImageLabel(QLabel):
    def __init__(self, pixmap, w, h, scaled=True, parent=None):
        super().__init__(parent)

        self.setScaledContents(scaled)

        self.setPixmap(pixmap)

        self.setFixedSize(w,h)

# 圆角图像标签
class RoundedImageLabel(RoundedLabel):
    def __init__(self,pixmap, w, h, scaled=True, radius=12, parent=None):
        super().__init__(radius,parent)

        self.setScaledContents(scaled)

        self.setPixmap(pixmap)

        self.setFixedSize(w,h)