from PyQt5.QtCore import QParallelAnimationGroup, QEasingCurve, QAbstractAnimation, QPropertyAnimation
from PyQt5.QtWidgets import QSizePolicy
from qfluentwidgets import SimpleCardWidget


# 水平折叠卡片
class HorizontalFoldCard(SimpleCardWidget):
    def __init__(self, open_width: int = 200, duration: int = 260, parent=None, ):
        super().__init__(parent)
        self._open_width = open_width
        self._closed_width = 0
        self._expanded = False
        self._animating = False

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setMinimumWidth(self._closed_width)
        self.setMaximumWidth(self._closed_width)

        # —— 私有动画组（对外不可见）——
        self._group = QParallelAnimationGroup()
        self._a_min = QPropertyAnimation(self, b"minimumWidth")
        self._a_max = QPropertyAnimation(self, b"maximumWidth")
        for a in (self._a_min, self._a_max):
            a.setDuration(duration)
            a.setEasingCurve(QEasingCurve.OutCubic)
            self._group.addAnimation(a)

        self._group.finished.connect(self._on_anim_done)

    # ---------------- 动画回调 ----------------
    def _on_anim_done(self):
        self._animating = False
        # 收起完成时，顺手把内部交互锁一下更稳（可选）
        self._expanded = (self.minimumWidth() > 0)

    def _run(self, end_w: int, duration=None, curve=None, on_finished=None):
        if self._group.state() == QAbstractAnimation.Running:
            self._group.stop()

        self._animating = True
        dur = duration if duration is not None else self._a_min.duration()
        crv = curve or QEasingCurve.OutCubic
        start = self.minimumWidth()

        for a in (self._a_min, self._a_max):
            a.setDuration(dur)
            a.setEasingCurve(crv)
            a.setStartValue(start)
            a.setEndValue(end_w)

        if on_finished:
            try:
                self._group.finished.disconnect()
            except TypeError:
                pass
            self._group.finished.connect(on_finished)

        self._group.start()

    # ---------------- 对外 API ----------------
    def expand(self, **kw):
        """展开到 open_width"""
        self._expanded = True
        self._run(self._open_width, **kw)

    def collapse(self, **kw):
        """收起到 0"""
        self._expanded = False
        self._run(self._closed_width, **kw)

    def toggle(self, open_width: int = None, **kw):
        """翻转；可临时改宽度。返回目标状态 True/False"""
        if open_width is not None:
            self._open_width = open_width
        if self._expanded:
            self.collapse(**kw)
            return False
        else:
            self.expand(**kw)
            return True

    # 兼容旧习惯：animate(200) 也行
    def animate(self, width: int, **kw):
        self._expanded = width > 0
        self._run(width, **kw)

    # ---------------- 属性 ----------------
    @property
    def is_expanded(self):
        return self._expanded

    @property
    def is_animating(self):
        return self._animating

    def setExpanded(self, on: bool, **kw):
        self.toggle() if on == self._expanded and False else (self.expand(**kw) if on else self.collapse(**kw))
        self._expanded = on
        return on