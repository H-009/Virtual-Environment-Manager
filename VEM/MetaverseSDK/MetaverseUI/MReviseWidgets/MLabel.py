from typing import Optional
from qtpy.QtWidgets import QWidget
from qfluentwidgets import BodyLabel as ReviseBodyLabel,CaptionLabel as ReviseCaptionLabel,\
    SubtitleLabel as ReviseSubtitleLabel,TitleLabel as ReviseTitleLabel


# 修订后的正文标签
class BodyLabel(ReviseBodyLabel):
    """去除 'QWidget | QWidget | None' 但实际为 'str' 警告"""
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        if text:
            self.setText(text)

# 修订后的描述标签
class CaptionLabel(ReviseCaptionLabel):
    """去除 'QWidget | QWidget | None' 但实际为 'str' 警告"""
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        if text:
            self.setText(text)

# 修订后的字幕标签
class SubtitleLabel(ReviseSubtitleLabel):
    """去除 'QWidget | QWidget | None' 但实际为 'str' 警告"""
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        if text:
            self.setText(text)

# 修订后的标题标签
class TitleLabel(ReviseTitleLabel):
    """去除 'QWidget | QWidget | None' 但实际为 'str' 警告"""
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)

        if text:
            self.setText(text)