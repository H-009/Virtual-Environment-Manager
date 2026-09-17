import math
import random
from qtpy.QtCore import QPropertyAnimation, Property, QRectF, Qt, QTimer, QPoint, QEasingCurve, \
    QSequentialAnimationGroup, QPointF
from qtpy.QtGui import QColor, QPainter, QPen, QConicalGradient, QBrush, QPolygonF, QLinearGradient, QPainterPath
from qtpy.QtWidgets import QProgressBar, QWidget
from qfluentwidgets import themeColor, isDarkTheme

# 不确定进度环



# 固定长度不确定进度环
class FixedLengthIndeterminateProgressRing(QProgressBar):
    """ Indeterminate progress ring (uniform rotation, fixed arc) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        # ── 外观参数 ──────────────────────────────
        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._rotationAngle = 0
        self._fixedSpanAngle = 90   # 固定弧长（度数）

        # ── 动画：匀速旋转 ────────────────────────
        self.rotationAni = QPropertyAnimation(self, b'rotationAngle', self)
        self.rotationAni.setDuration(1000)       # 一圈 1 秒
        self.rotationAni.setStartValue(0)
        self.rotationAni.setEndValue(360)
        self.rotationAni.setLoopCount(-1)

        self.setFixedSize(80, 80)

        if start:
            self.start()

    # ── property ──────────────────────────────────
    @Property(int)
    def rotationAngle(self):
        return self._rotationAngle

    @rotationAngle.setter
    def rotationAngle(self, angle: int):
        self._rotationAngle = angle
        self.update()

    # ── strokeWidth（保持与你原版一致的 pyqtProperty 用法）──
    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w: int):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    # ── 公开控制接口 ──────────────────────────────
    def start(self):
        """开始旋转"""
        self._rotationAngle = 0
        self.rotationAni.start()

    def stop(self):
        """停止并清空"""
        self.rotationAni.stop()
        self._rotationAngle = 0
        self.update()

    # ── 颜色接口（与你原版完全一致）────────────────
    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        """设置亮/暗主题的弧条颜色

        Parameters
        ----------
        light, dark: str | Qt.GlobalColor | QColor
        """
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        """设置亮/暗主题的背景圆颜色

        Parameters
        ----------
        light, dark: str | Qt.GlobalColor | QColor
        """
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    # ── 绘制 ──────────────────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cw = self._strokeWidth
        side = min(self.width(), self.height())
        w = side - cw
        rc = QRectF(cw / 2, (side - w) / 2, w, w)

        # 背景整圆
        bg_color = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        pen = QPen(bg_color, cw, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawArc(rc, 0, 360 * 16)

        # 前景弧：固定 90°，匀速旋转
        bar_color = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        pen.setColor(bar_color)
        painter.setPen(pen)

        start_angle = (-self._rotationAngle + 180) % 360
        painter.drawArc(rc, start_angle * 16, -self._fixedSpanAngle * 16)

# 多段弧不确定进度环
class MultipleArcsIndeterminateProgressRing(QProgressBar):
    """ Indeterminate dot-ring progress (rotating highlight) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._dotCount = 4
        self._dotRadius = 3
        self._trackRadius = 28
        self._rotationAngle = 0
        self._speed = 4

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        self.setFixedSize(80, 80)

        if start:
            self.start()

    @Property(int)
    def rotationAngle(self):
        return self._rotationAngle

    @rotationAngle.setter
    def rotationAngle(self, angle: int):
        self._rotationAngle = angle
        self.update()

    def start(self):
        self._rotationAngle = 0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self._rotationAngle = 0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def setDotCount(self, count: int):
        self._dotCount = max(2, count)
        self.update()

    def setDotRadius(self, r: int):
        self._dotRadius = max(1, r)
        self.update()

    def setTrackRadius(self, r: int):
        self._trackRadius = max(r, self._dotRadius + 2)
        self.update()

    def _tick(self):
        self._rotationAngle = (self._rotationAngle + self._speed) % 360
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # 背景
        bg_color = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg_color.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg_color)
            painter.drawEllipse(
                QPoint(int(cx), int(cy)),
                self._trackRadius + self._dotRadius,
                self._trackRadius + self._dotRadius,
            )

        # 前景点阵
        base_color = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        painter.translate(cx, cy)
        painter.rotate(self._rotationAngle)

        for i in range(self._dotCount):
            painter.save()
            painter.rotate(i * 360 / self._dotCount)

            # 该点在屏幕上的绝对角度 = 自身偏移 + 旋转角度
            point_angle = (i * 360 / self._dotCount + self._rotationAngle) % 360

            # 让"正上方"(270°) 为最亮位置，距离越远越暗
            # 用最短角差（处理 359° 和 1° 之间跨越 0° 的情况）
            diff = abs(point_angle - 270)
            if diff > 180:
                diff = 360 - diff
            # diff ∈ [0, 180]，归一化到 [0, 1]
            normalized = diff / 180.0

            # 非线性衰减，让亮斑更集中（可选：改成 linear 就是线性）
            import math
            fade = math.pow(normalized, 1.5)
            alpha = int(255 * (1.0 - fade))

            color = QColor(base_color)
            color.setAlpha(alpha)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                QPoint(self._trackRadius, 0),
                self._dotRadius,
                self._dotRadius,
            )
            painter.restore()

# 脉冲环不确定进度环
class PulseRingIndeterminateProgressRing(QProgressBar):
    """ 内外同时呼吸的脉冲环，最大尺寸不超边界 """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        # ── 外观参数 ──────────────────────────────
        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()

        self._strokeWidth = 6           # 基础线宽（最细时）
        self._maxWidthScale = 1.5       # 最粗时倍数
        self._baseRadius = 70           # 基础圆环半径（最细时 pen 中心到圆心）
        self._pulseValue = 0.0

        # ── 关键：按"最粗时刻"算控件尺寸，永远不超框 ──
        max_pen_width = self._strokeWidth * self._maxWidthScale
        # 最粗时 pen 外边缘到圆心的距离 = 基础半径 + 半宽增量
        max_outer_radius = self._baseRadius + max_pen_width / 2
        safety_margin = 2  # 安全边距，防抗锯齿溢出
        widget_size = int((max_outer_radius + safety_margin) * 2)

        self.setFixedSize(widget_size, widget_size)

        # ── 呼吸动画 ──────────────────────────────
        half_period = 1200

        self.breatheIn = QPropertyAnimation(self, b'pulseValue', self)
        self.breatheIn.setDuration(half_period)
        self.breatheIn.setStartValue(0.0)
        self.breatheIn.setEndValue(1.0)
        self.breatheIn.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.breatheOut = QPropertyAnimation(self, b'pulseValue', self)
        self.breatheOut.setDuration(half_period)
        self.breatheOut.setStartValue(1.0)
        self.breatheOut.setEndValue(0.0)
        self.breatheOut.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.breatheGroup = QSequentialAnimationGroup(self)
        self.breatheGroup.addAnimation(self.breatheIn)
        self.breatheGroup.addAnimation(self.breatheOut)
        self.breatheGroup.setLoopCount(-1)

        if start:
            self.start()

    # ── property ──────────────────────────────────
    @Property(float)
    def pulseValue(self):
        return self._pulseValue

    @pulseValue.setter
    def pulseValue(self, v: float):
        self._pulseValue = v
        self.update()

    # ── strokeWidth ───────────────────────────────
    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w: int):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    # ── 控制接口 ──────────────────────────────────
    def start(self):
        self._pulseValue = 0.0
        self.breatheGroup.start()

    def stop(self):
        self.breatheGroup.stop()
        self._pulseValue = 0.0
        self.update()

    # ── 颜色接口 ──────────────────────────────────
    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    # ── 绘制 ──────────────────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        # ── 动态线宽 ──────────────────────────────
        brightness = math.pow(self._pulseValue, 1.8)
        dynamic_width = self._strokeWidth * (1.0 + (self._maxWidthScale - 1.0) * brightness)

        # ── 居中矩形：pen 中心线轨迹 ──────────────
        # 圆心 = 控件中心
        # pen 中心线半径 = 基础半径（固定）
        # → 矩形左上角 = center - radius
        # → 矩形宽高   = radius * 2
        # pen 外边缘 = center ± radius，永远 ≤ widget_size/2
        cx = self.width() / 2
        cy = self.height() / 2

        # 矩形以 pen 中心线为基准（半径 = baseRadius）
        rc = QRectF(
            cx - self._baseRadius,
            cy - self._baseRadius,
            self._baseRadius * 2,
            self._baseRadius * 2,
        )

        # 验证：最粗时 pen 外边缘距离
        # max_edge = baseRadius + max_pen_width/2
        # widget 半边长 = widget_size/2 = max_outer_radius + safety_margin
        # → 永远有 safety_margin 的余量 ✓

        # ── 背景圆 ────────────────────────────────
        bg_color = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg_color.alpha() > 0:
            pen = QPen(bg_color, dynamic_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # ── 前景环 ────────────────────────────────
        base_color = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        alpha = int(255 * (0.25 + 0.75 * brightness))
        color = QColor(base_color)
        color.setAlpha(alpha)

        pen = QPen(color, dynamic_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rc, 0, 360 * 16)

# 彗星拖尾不确定进度环
class CometTailIndeterminateProgressRing(QProgressBar):
    """ Indeterminate comet-trail progress ring (iOS / visionOS style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        # ── 外观参数 ──────────────────────────────
        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 70        # pen 中心线半径
        self._tailAngle = 120        # 拖尾弧长度（度数），越小越短
        self._gradientAngle = 0      # 渐变起始角度（驱动旋转）

        # ── 旋转动画 ──────────────────────────────
        self.rotationAni = QPropertyAnimation(self, b'gradientAngle', self)
        self.rotationAni.setDuration(1000)
        self.rotationAni.setStartValue(0)
        self.rotationAni.setEndValue(360)
        self.rotationAni.setLoopCount(-1)
        # 匀速旋转，不用缓动

        # ── 控件尺寸（按最粗时刻算，不超框）──────
        outer_radius = self._ringRadius + self._strokeWidth / 2
        margin = 2
        widget_size = int((outer_radius + margin) * 2)
        self.setFixedSize(widget_size, widget_size)

        if start:
            self.start()

    # ── property ──────────────────────────────────
    @Property(int)
    def gradientAngle(self):
        return self._gradientAngle

    @gradientAngle.setter
    def gradientAngle(self, angle: int):
        self._gradientAngle = angle
        self.update()

    # ── strokeWidth ───────────────────────────────
    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w: int):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    # ── 控制接口 ──────────────────────────────────
    def start(self):
        self._gradientAngle = 0
        self.rotationAni.start()

    def stop(self):
        self.rotationAni.stop()
        self._gradientAngle = 0
        self.update()

    # ── 颜色接口 ──────────────────────────────────
    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    # ── 可调参数 ──────────────────────────────────
    def setTailAngle(self, angle: int):
        """设置拖尾弧长度（默认 120°）"""
        self._tailAngle = max(30, min(300, angle))
        self.update()

    # ── 绘制 ──────────────────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2
        cy = self.height() / 2

        # ── 背景整圆 ──────────────────────────────
        bg_color = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg_color.alpha() > 0:
            r = self._ringRadius
            rc = QRectF(cx - r, cy - r, r * 2, r * 2)
            pen = QPen(bg_color, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # ── 彗星拖尾：底层整圈渐变弧 ──────────────
        base_color = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        r, g, b = base_color.red(), base_color.green(), base_color.blue()

        start_angle = -self._gradientAngle + 180
        gradient = QConicalGradient(cx, cy, start_angle % 360)

        tail_ratio = self._tailAngle / 360.0

        gradient.setColorAt(0.0, base_color)
        gradient.setColorAt(tail_ratio * 0.5, base_color)
        gradient.setColorAt(tail_ratio * 0.85, QColor(r, g, b, 60))
        gradient.setColorAt(tail_ratio, QColor(r, g, b, 0))
        gradient.setColorAt(1.0, QColor(r, g, b, 0))

        pen = QPen(QBrush(gradient), self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)
        painter.drawArc(rc, 0, 360 * 16)

        # ── 顶层：头部高光圆角端点 ────────────────
        # 在弧的起始位置画一小段纯色弧，让 RoundCap 的圆角可见
        head_pen = QPen(base_color, self._strokeWidth)
        head_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(head_pen)
        # 只画 1° 的极小弧 → 两端 RoundCap 形成一个圆角亮点
        painter.drawArc(rc, start_angle * 16, -1 * 16)

# 段式弧不确定进度环
class SegmentedArcIndeterminateProgressRing(QProgressBar):
    """ 段式弧不确定进度环 (Win11 Fluent Design style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 70
        self._segmentCount = 3
        self._angle = 0
        self._speed = 4

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @Property(int)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, v):
        self._angle = v
        self.update()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._angle = 0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self._angle = 0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def _tick(self):
        self._angle = (self._angle + self._speed) % 360
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)

        # 背景
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # 段式弧
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        seg_span = 360 // self._segmentCount
        gap = 8  # 段间间隔度数

        for i in range(self._segmentCount):
            offset = (i * seg_span + self._angle) % 360
            # 透明度依次递减：第一段最亮
            alpha = int(255 * (1.0 - i / self._segmentCount * 0.7))
            c = QColor(base)
            c.setAlpha(alpha)
            pen = QPen(c, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, offset * 16, (seg_span - gap) * 16)

# 双环不确定进度环
class DualRingIndeterminateProgressRing(QProgressBar):
    """ 双环交织不确定进度环 (Samsung One UI style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 5
        self._outerRadius = 68
        self._innerRadius = 44
        self._outerAngle = 0
        self._innerAngle = 0
        self._outerSpeed = 4
        self._innerSpeed = -5  # 反向

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        outer = self._outerRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @Property(int)
    def outerAngle(self):
        return self._outerAngle

    @outerAngle.setter
    def outerAngle(self, v):
        self._outerAngle = v
        self.update()

    @Property(int)
    def innerAngle(self):
        return self._innerAngle

    @innerAngle.setter
    def innerAngle(self, v):
        self._innerAngle = v
        self.update()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._outerAngle = 0
        self._innerAngle = 0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self._outerAngle = 0
        self._innerAngle = 0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def _tick(self):
        self._outerAngle = (self._outerAngle + self._outerSpeed) % 360
        self._innerAngle = (self._innerAngle + self._innerSpeed) % 360
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()

        # 背景
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            for r in [self._outerRadius, self._innerRadius]:
                rc = QRectF(cx - r, cy - r, r * 2, r * 2)
                pen = QPen(bg, self._strokeWidth)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                painter.drawArc(rc, 0, 360 * 16)

        # 外环：顺时针
        c_outer = QColor(base)
        c_outer.setAlpha(220)
        rc_outer = QRectF(cx - self._outerRadius, cy - self._outerRadius,
                          self._outerRadius * 2, self._outerRadius * 2)
        pen = QPen(c_outer, self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rc_outer, (-self._outerAngle + 180) * 16, -90 * 16)

        # 内环：逆时针，略细
        c_inner = QColor(base)
        c_inner.setAlpha(160)
        pen_inner = QPen(c_inner, max(2, self._strokeWidth - 2))
        pen_inner.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_inner)
        rc_inner = QRectF(cx - self._innerRadius, cy - self._innerRadius,
                          self._innerRadius * 2, self._innerRadius * 2)
        painter.drawArc(rc_inner, (-self._innerAngle + 180) * 16, 90 * 16)

# 等距点阵波浪不确定进度环
class DotWaveIndeterminateProgressRing(QProgressBar):
    """ 等距点阵波浪不确定进度环 (Google Workspace style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._dotCount = 16
        self._dotRadius = 3.5
        self._trackRadius = 56
        self._phase = 0.0
        self._speed = 0.15

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        outer = self._trackRadius + self._dotRadius + 4
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @Property(float)
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, v):
        self._phase = v
        self.update()

    def start(self):
        self._phase = 0.0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self._phase = 0.0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def _tick(self):
        self._phase = (self._phase + self._speed) % (2 * math.pi)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()

        # 背景
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg)
            painter.drawEllipse(QPoint(int(cx), int(cy)),
                                self._trackRadius + self._dotRadius + 2,
                                self._trackRadius + self._dotRadius + 2)

        painter.translate(cx, cy)

        for i in range(self._dotCount):
            angle = i * 2 * math.pi / self._dotCount
            # 波浪：每个点根据相位偏移计算缩放和透明度
            wave = math.sin(angle + self._phase)
            # wave ∈ [-1, 1] → normalized ∈ [0, 1]
            normalized = (wave + 1) / 2

            scale = 0.5 + 0.7 * normalized
            alpha = int(60 + 195 * normalized)

            color = QColor(base)
            color.setAlpha(alpha)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)

            r = self._trackRadius
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            dr = self._dotRadius * scale
            painter.drawEllipse(QPoint(int(x), int(y)), int(dr), int(dr))

# 霓虹脉冲发光不确定进度环
class NeonGlowIndeterminateProgressRing(QProgressBar):
    """ 霓虹脉冲发光不确定进度环 (Cyberpunk style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 5
        self._ringRadius = 56
        self._pulseValue = 0.0
        self._glowLayers = 4  # 发光层数

        half_period = 1100

        self.breatheIn = QPropertyAnimation(self, b'pulseValue', self)
        self.breatheIn.setDuration(half_period)
        self.breatheIn.setStartValue(0.0)
        self.breatheIn.setEndValue(1.0)
        self.breatheIn.setEasingCurve(QEasingCurve.Type.InOutSine)

        self.breatheOut = QPropertyAnimation(self, b'pulseValue', self)
        self.breatheOut.setDuration(half_period)
        self.breatheOut.setStartValue(1.0)
        self.breatheOut.setEndValue(0.0)
        self.breatheOut.setEasingCurve(QEasingCurve.Type.InOutSine)

        self.breatheGroup = QSequentialAnimationGroup(self)
        self.breatheGroup.addAnimation(self.breatheIn)
        self.breatheGroup.addAnimation(self.breatheOut)
        self.breatheGroup.setLoopCount(-1)

        outer = self._ringRadius + self._strokeWidth * self._glowLayers + 4
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @Property(float)
    def pulseValue(self):
        return self._pulseValue

    @pulseValue.setter
    def pulseValue(self, v):
        self._pulseValue = v
        self.update()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._pulseValue = 0.0
        self.breatheGroup.start()

    def stop(self):
        self.breatheGroup.stop()
        self._pulseValue = 0.0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()

        # 背景
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)

        # 多层发光叠加（从外到内，alpha 逐层降低）
        for i in range(self._glowLayers):
            layer_alpha = int(255 * (0.15 + 0.10 * i) * (0.3 + 0.7 * self._pulseValue))
            c = QColor(base)
            c.setAlpha(max(0, layer_alpha))
            w = self._strokeWidth * (self._glowLayers - i)
            pen = QPen(c, w)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # 核心亮线
        core_alpha = int(255 * (0.6 + 0.4 * self._pulseValue))
        core_color = QColor(base)
        core_color.setAlpha(core_alpha)
        pen = QPen(core_color, self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rc, 0, 360 * 16)

# 粒子消散不确定进度环
class ParticleDissolveIndeterminateProgressRing(QProgressBar):
    """ 粒子消散进度环 (Figma / Framer style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._ringRadius = 56
        self._particleCount = 40
        self._particles = []          # [(angle, size, alpha, speed), ...]
        self._phase = 0

        self._init_particles()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        outer = self._ringRadius + 10
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    def _init_particles(self):
        self._particles = []
        for i in range(self._particleCount):
            angle = 360 * i / self._particleCount
            size = random.randint(2, 5)
            alpha = random.randint(80, 255)
            speed = random.uniform(0.3, 1.2)
            self._particles.append([angle, size, alpha, speed])

    @staticmethod
    def getStrokeWidth():
        return 4

    def setStrokeWidth(self, w):
        pass

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._init_particles()
        self._phase = 0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def _tick(self):
        self._phase += 1
        for p in self._particles:
            # 随机闪烁 + 轻微角度漂移
            if random.random() < 0.05:
                p[2] = random.randint(40, 255)
            p[0] = (p[0] + p[3]) % 360
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()

        # 背景
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg)
            painter.drawEllipse(QPoint(int(cx), int(cy)),
                                self._ringRadius + 6, self._ringRadius + 6)

        painter.translate(cx, cy)

        for angle, size, alpha, speed in self._particles:
            rad = math.radians(angle)
            x = self._ringRadius * math.cos(rad)
            y = self._ringRadius * math.sin(rad)

            c = QColor(base)
            c.setAlpha(alpha)
            painter.setBrush(c)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPoint(int(x), int(y)), size, size)

# 螺旋不确定进度环
class SpiralInIndeterminateProgressRing(QProgressBar):
    """ 螺旋收紧进度环 (Concept UI style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._maxRadius = 58
        self._turns = 3              # 螺旋圈数
        self._angle = 0
        self._speed = 2

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        size = self._maxRadius + 10
        self.setFixedSize(size * 2, size * 2)

        if start:
            self.start()

    @staticmethod
    def getStrokeWidth():
        return 2

    def setStrokeWidth(self, w):
        pass

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._angle = 0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def _tick(self):
        self._angle = (self._angle + self._speed) % 360
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()

        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            painter.fillRect(self.rect(), bg)

        painter.translate(cx, cy)

        # 画阿基米德螺旋
        points = []
        total_steps = 200
        for i in range(total_steps):
            t = i / total_steps
            radius = self._maxRadius * (1 - t)
            angle_rad = math.radians(self._angle + t * 360 * self._turns)
            x = radius * math.cos(angle_rad)
            y = radius * math.sin(angle_rad)
            points.append((x, y, radius))

        # 逐段绘制，alpha 随半径变化
        for i in range(len(points) - 1):
            _, _, r1 = points[i]
            x2, y2, r2 = points[i + 1]

            alpha = int(255 * (r1 / self._maxRadius))
            c = QColor(base)
            c.setAlpha(alpha)
            pen = QPen(c, 2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(int(points[i][0]), int(points[i][1]),
                             int(x2), int(y2))

# 玻璃拟态不确定进度环
class GlassmorphismIndeterminateProgressRing(QProgressBar):
    """ 玻璃拟态进度环 (visionOS / iOS 26 style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(255, 255, 255, 40)
        self.darkBackgroundColor = QColor(0, 0, 0, 60)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 8
        self._ringRadius = 64
        self._sweepAngle = 0

        self.rotationAni = QPropertyAnimation(self, b'sweepAngle', self)
        self.rotationAni.setDuration(3000)
        self.rotationAni.setStartValue(0)
        self.rotationAni.setEndValue(360)
        self.rotationAni.setLoopCount(-1)

        outer = self._ringRadius + self._strokeWidth / 2 + 4
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @Property(int)
    def sweepAngle(self):
        return self._sweepAngle

    @sweepAngle.setter
    def sweepAngle(self, v):
        self._sweepAngle = v
        self.update()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._sweepAngle = 0
        self.rotationAni.start()

    def stop(self):
        self.rotationAni.stop()
        self._sweepAngle = 0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # 磨砂玻璃底色
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg)
        rc_bg = QRectF(cx - self._ringRadius - 4, cy - self._ringRadius - 4,
                       (self._ringRadius + 4) * 2, (self._ringRadius + 4) * 2)
        painter.drawEllipse(rc_bg)

        # 彩虹流光渐变
        gradient = QConicalGradient(cx, cy, self._sweepAngle)

        colors = [
            ("#FF006E", 0.0),
            ("#8338EC", 0.15),
            ("#3A86FF", 0.35),
            ("#06FFB4", 0.55),
            ("#FFBE0B", 0.75),
            ("#FB5607", 0.90),
            ("#FF006E", 1.0),
        ]
        for color_hex, pos in colors:
            gradient.setColorAt(pos, QColor(color_hex))

        pen = QPen(QBrush(gradient), self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)
        painter.drawArc(rc, 0, 360 * 16)

# 折纸展开不确定进度环
class OrigamiFoldIndeterminateProgressRing(QProgressBar):
    """ 折纸展开进度环 (Concept animation style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._ringRadius = 52
        self._segmentCount = 12
        self._progress = 0.0
        self._direction = 1

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(30)

        outer = self._ringRadius + 10
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @staticmethod
    def getStrokeWidth():
        return 3

    def setStrokeWidth(self, w):
        pass

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._progress = 0.0
        self._direction = 1
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def _tick(self):
        self._progress += 0.015 * self._direction
        if self._progress >= 1.0:
            self._progress = 1.0
            self._direction = -1
        elif self._progress <= 0.0:
            self._progress = 0.0
            self._direction = 1
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()

        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg)
            painter.drawEllipse(QPoint(int(cx), int(cy)),
                                self._ringRadius + 6, self._ringRadius + 6)

        painter.translate(cx, cy)

        seg_angle = 360 / self._segmentCount
        active = int(self._segmentCount * self._progress)

        for i in range(self._segmentCount):
            angle_rad = math.radians(i * seg_angle - 90)
            next_angle_rad = math.radians((i + 1) * seg_angle - 90)

            inner = self._ringRadius - 8
            outer = self._ringRadius + 8

            x1 = inner * math.cos(angle_rad)
            y1 = inner * math.sin(angle_rad)
            x2 = outer * math.cos(angle_rad)
            y2 = outer * math.sin(angle_rad)
            x3 = outer * math.cos(next_angle_rad)
            y3 = outer * math.sin(next_angle_rad)
            x4 = inner * math.cos(next_angle_rad)
            y4 = inner * math.sin(next_angle_rad)

            polygon = QPolygonF([
                QPointF(x1, y1), QPointF(x2, y2),
                QPointF(x3, y3), QPointF(x4, y4)
            ])

            if i < active:
                alpha = int(255 * (0.4 + 0.6 * i / max(1, self._segmentCount - 1)))
                c = QColor(base)
                c.setAlpha(alpha)
                painter.setBrush(c)
                painter.setPen(QPen(c, 1))
            else:
                c = QColor(base)
                c.setAlpha(30)
                painter.setBrush(c)
                painter.setPen(Qt.PenStyle.NoPen)

            painter.drawPolygon(polygon)

# 棱镜折射不确定进度环
class PrismRefractionIndeterminateProgressRing(QProgressBar):
    """ 棱镜折射进度环 (光谱分光旋转风格) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 56
        self._bandCount = 6
        self._angle = 0

        self.rotationAni = QPropertyAnimation(self, b'angle', self)
        self.rotationAni.setDuration(2000)
        self.rotationAni.setStartValue(0)
        self.rotationAni.setEndValue(360)
        self.rotationAni.setLoopCount(-1)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @Property(int)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, v):
        self._angle = v
        self.update()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._angle = 0
        self.rotationAni.start()

    def stop(self):
        self.rotationAni.stop()
        self._angle = 0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        prism_colors = [
            "#FF006E", "#FB5607", "#FFBE0B",
            "#06FFB4", "#3A86FF", "#8338EC"
        ]

        total_span = 280  # 总弧长
        seg_span = total_span // self._bandCount
        gap = 2

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)

        for i in range(self._bandCount):
            color = QColor(prism_colors[i % len(prism_colors)])
            # 每段透明度微微错开，增加层次
            color.setAlpha(200 - i * 20)

            pen = QPen(color, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            offset = (i * seg_span + self._angle) % 360
            painter.drawArc(rc, offset * 16, (seg_span - gap) * 16)

# 蛇形不确定进度环
class SerpentineIndeterminateProgressRing(QProgressBar):
    """ 蛇形游走进度环 (Organic flowing style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 54
        self._time = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._time = 0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def _tick(self):
        self._time += 0.025
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()

        # 弧长呼吸：sin 波动 60°~180°
        span = 60 + int(60 * (1 + math.sin(self._time * 1.3)))

        # 旋转位置也在动
        start_angle = int(self._time * 80) % 360

        # 颜色也微微偏移饱和度
        hue_shift = int(20 * math.sin(self._time * 0.7))
        c = QColor(base)
        c = c.lighter(100 + hue_shift) if base.value() > 128 else c.lighter(100 + hue_shift * 2)
        c.setAlpha(230)

        pen = QPen(c, self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)
        painter.drawArc(rc, (-start_angle + 180) * 16, -span * 16)

# 星轨不确定进度环
class StarTrailIndeterminateProgressRing(QProgressBar):
    """ 星轨进度环 (Astronomical star-trail style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 4
        self._ringRadius = 54
        self._angle = 0
        self._starPositions = [0, 72, 144, 216, 288]  # 5颗星

        self.rotationAni = QPropertyAnimation(self, b'angle', self)
        self.rotationAni.setDuration(2200)
        self.rotationAni.setStartValue(0)
        self.rotationAni.setEndValue(360)
        self.rotationAni.setLoopCount(-1)

        outer = self._ringRadius + 14
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @Property(int)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, v):
        self._angle = v
        self.update()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._angle = 0
        self.rotationAni.start()

    def stop(self):
        self.rotationAni.stop()
        self._angle = 0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        r, g, b = base.red(), base.green(), base.blue()

        # 深色星空背景
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            painter.fillRect(self.rect(), bg)

        # 微弱的轨道线
        track_pen = QPen(QColor(r, g, b, 25), 1)
        painter.setPen(track_pen)
        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)
        painter.drawArc(rc, 0, 360 * 16)

        # 主弧（轨迹）
        trail_color = QColor(r, g, b, 120)
        pen = QPen(trail_color, self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        start = (-self._angle + 180) % 360
        painter.drawArc(rc, start * 16, -200 * 16)

        # 星点
        painter.translate(cx, cy)
        for i, sp in enumerate(self._starPositions):
            angle = (sp + self._angle * 0.7) % 360
            rad = math.radians(angle)
            x = self._ringRadius * math.cos(rad)
            y = self._ringRadius * math.sin(rad)

            # 星点大小闪烁
            twinkle = 0.6 + 0.4 * math.sin(self._angle * 0.05 + i)
            star_size = int(3 + 2 * twinkle)

            # 外发光
            glow = QColor(r, g, b, 60)
            painter.setBrush(glow)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPoint(int(x), int(y)), star_size + 3, star_size + 3)

            # 星点核心
            core = QColor(255, 255, 255) if isDarkTheme() else QColor(r, g, b)
            painter.setBrush(core)
            painter.drawEllipse(QPoint(int(x), int(y)), star_size, star_size)

# 磁滞回线不确定进度环
class HysteresisLoopIndeterminateProgressRing(QProgressBar):
    """ 磁滞回线进度环 (Oscilloscope / Scientific instrument style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 5
        self._ringRadius = 54
        self._phase = 0.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._phase = 0.0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def _tick(self):
        self._phase += 0.02
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        r, g, b = base.red(), base.green(), base.blue()

        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            painter.fillRect(self.rect(), bg)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)

        # 两条弧分别从 0° 和 180° 出发，在顶部相遇
        # 用 sin 做来回运动
        sweep1 = int(160 * (0.5 + 0.5 * math.sin(self._phase)))
        sweep2 = int(160 * (0.5 + 0.5 * math.sin(self._phase + math.pi)))

        pos1 = int(self._phase * 60) % 360
        pos2 = (pos1 + 180) % 360

        # 第一条弧：暖色调
        c1 = QColor(r, g, b)
        c1.setAlpha(220)
        pen1 = QPen(c1, self._strokeWidth)
        pen1.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen1)
        painter.drawArc(rc, (-pos1 + 180) * 16, -sweep1 * 16)

        # 第二条弧：略暗
        c2 = QColor(r, g, b)
        c2.setAlpha(120)
        pen2 = QPen(c2, self._strokeWidth - 1)
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen2)
        painter.drawArc(rc, (-pos2 + 180) * 16, sweep2 * 16)

# 像素扫描不确定进度环
class PixelScanIndeterminateProgressRing(QProgressBar):
    """ 像素扫描进度环 (Retro CRT / Terminal style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._ringRadius = 52
        self._blockCount = 36
        self._blocks = []          # alpha values
        self._headPos = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(35)

        outer = self._ringRadius + 14
        self.setFixedSize(int(outer * 2), int(outer * 2))

        self._init_blocks()

        if start:
            self.start()

    def _init_blocks(self):
        self._blocks = [0] * self._blockCount

    @staticmethod
    def getStrokeWidth():
        return 4

    def setStrokeWidth(self, w):
        pass

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._init_blocks()
        self._headPos = 0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def _tick(self):
        self._headPos = (self._headPos + 1) % self._blockCount
        self._blocks[self._headPos] = 255  # 扫描头最亮

        # 所有方块逐渐衰减
        for i in range(self._blockCount):
            if i != self._headPos:
                self._blocks[i] = max(0, self._blocks[i] - 18)

        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        r, g, b = base.red(), base.green(), base.blue()

        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            painter.fillRect(self.rect(), bg)

        block_angle = 360 / self._blockCount
        block_size = 6

        painter.translate(cx, cy)

        for i in range(self._blockCount):
            angle = i * block_angle - 90
            rad = math.radians(angle)
            x = self._ringRadius * math.cos(rad)
            y = self._ringRadius * math.sin(rad)

            alpha = self._blocks[i]
            if alpha > 0:
                # 扫描头额外加一个白色高光
                if i == self._headPos:
                    c = QColor(255, 255, 255) if isDarkTheme() else QColor(r, g, b)
                    c.setAlpha(alpha)
                    painter.setBrush(c)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRect(int(x - 3), int(y - 3), block_size, block_size)
                else:
                    c = QColor(r, g, b, alpha)
                    painter.setBrush(c)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRect(int(x - 2), int(y - 2), block_size - 2, block_size - 2)

# 双月环不确定进度环
class DoubleMoonIndeterminateProgressRing(QProgressBar):
    """ 双月环不确定进度环 (Crescent arc spinner) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 54
        self._gapAngle = 30           # 头尾缺口大小（度数）
        self._sweepAngle = 0          # 驱动旋转

        self.rotationAni = QPropertyAnimation(self, b'sweepAngle', self)
        self.rotationAni.setDuration(1800)
        self.rotationAni.setStartValue(0)
        self.rotationAni.setEndValue(360)
        self.rotationAni.setLoopCount(-1)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    # ── property ───────────────────────────────
    @Property(int)
    def sweepAngle(self):
        return self._sweepAngle

    @sweepAngle.setter
    def sweepAngle(self, v):
        self._sweepAngle = v
        self.update()

    # ── strokeWidth ────────────────────────────
    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    # ── 控制接口 ──────────────────────────────
    def start(self):
        self._sweepAngle = 0
        self.rotationAni.start()

    def stop(self):
        self.rotationAni.stop()
        self._sweepAngle = 0
        self.update()

    # ── 颜色接口 ──────────────────────────────
    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    # ── 可调参数 ──────────────────────────────
    def setGapAngle(self, angle: int):
        """设置头尾缺口大小（默认 30°）"""
        self._gapAngle = max(5, min(120, angle))
        self.update()

    # ── 绘制 ──────────────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # ── 背景 ──────────────────────────────
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # ── 锥形渐变弧（头亮尾暗）────────────
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        r, g, b = base.red(), base.green(), base.blue()

        # 渐变起始角 = 缺口位置 + 偏移，让亮头对准弧的起始端
        gradient = QConicalGradient(cx, cy, self._sweepAngle)

        # 弧从 0.0（头，实色）渐变到 (360-gap)/360（尾，暗）
        # 然后 gap 区域全透明
        solid_ratio = (360 - self._gapAngle) / 360.0

        gradient.setColorAt(0.0, base)                          # 头：实色
        gradient.setColorAt(solid_ratio * 0.5, QColor(r, g, b, 200))
        gradient.setColorAt(solid_ratio * 0.85, QColor(r, g, b, 80))
        gradient.setColorAt(solid_ratio, QColor(r, g, b, 0))   # 尾：全透
        gradient.setColorAt(1.0, QColor(r, g, b, 0))           # 缺口：全透

        pen = QPen(QBrush(gradient), self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)

        # 弧的起始角度 = sweepAngle（旋转）
        # 跨度 = 360 - gap（留缺口）
        start = (-self._sweepAngle + 180) % 360
        span = 360 - self._gapAngle
        painter.drawArc(rc, start * 16, -span * 16)

# 潮汐弧不确定进度环
class TideArcIndeterminateProgressRing(QProgressBar):
    """ 潮汐弧进度环 (Grow → Pause → Consume → Pause → Loop) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 64
        self._maxSpan = 360
        self._currentSpan = 0
        self._consumeOffset = 0
        self._holdDuration = 300    # 每段停顿时长（ms）

        # ── 阶段1：生长 ──────────────────────
        self.growAni = QPropertyAnimation(self, b'currentSpan', self)
        self.growAni.setDuration(1200)
        self.growAni.setStartValue(0)
        self.growAni.setEndValue(self._maxSpan)
        self.growAni.setEasingCurve(QEasingCurve.Type.OutCubic)

        # ── 停顿1：长到最大后等一下 ──────────
        self.hold1 = QPropertyAnimation(self, b'currentSpan', self)
        self.hold1.setDuration(self._holdDuration)
        self.hold1.setStartValue(self._maxSpan)
        self.hold1.setEndValue(self._maxSpan)  # 值不变 = 停顿

        # ── 阶段2：消耗 ──────────────────────
        self.consumeAni = QPropertyAnimation(self, b'consumeOffset', self)
        self.consumeAni.setDuration(1200)
        self.consumeAni.setStartValue(0)
        self.consumeAni.setEndValue(self._maxSpan)
        self.consumeAni.setEasingCurve(QEasingCurve.Type.InCubic)

        # ── 串联循环 ─────────────────────────
        self.seqGroup = QSequentialAnimationGroup(self)
        self.seqGroup.addAnimation(self.growAni)    # 生长
        self.seqGroup.addAnimation(self.hold1)      # 停顿
        self.seqGroup.addAnimation(self.consumeAni)  # 消耗
        self.seqGroup.setLoopCount(-1)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    # ── properties ─────────────────────────────
    @Property(int)
    def currentSpan(self):
        return self._currentSpan

    @currentSpan.setter
    def currentSpan(self, v):
        self._currentSpan = v
        self.update()

    @Property(int)
    def consumeOffset(self):
        return self._consumeOffset

    @consumeOffset.setter
    def consumeOffset(self, v):
        self._consumeOffset = v
        self.update()

    # ── strokeWidth ────────────────────────────
    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    # ── 控制接口 ──────────────────────────────
    def start(self):
        self._currentSpan = 0
        self._consumeOffset = 0
        self.seqGroup.start()

    def stop(self):
        self.seqGroup.stop()
        self._currentSpan = 0
        self._consumeOffset = 0
        self.update()

    # ── 颜色接口 ──────────────────────────────
    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    # ── 可调参数 ──────────────────────────────
    def setMaxSpan(self, angle: int):
        self._maxSpan = max(30, min(360, angle))
        self.growAni.setEndValue(self._maxSpan)
        self.consumeAni.setEndValue(self._maxSpan)
        self.hold1.setStartValue(self._maxSpan)
        self.hold1.setEndValue(self._maxSpan)

    def setHoldDuration(self, ms: int):
        """设置两段之间的停顿时长（默认 300ms）"""
        self._holdDuration = max(0, ms)
        self.hold1.setDuration(self._holdDuration)

    # ── 绘制 ──────────────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # ── 背景 ──────────────────────────────
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # ── 潮汐弧 ────────────────────────────
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        pen = QPen(base, self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)

        fixed_end = 90 - self._maxSpan

        current_ani = self.seqGroup.currentAnimation()

        if current_ani in (self.growAni, self.hold1):
            # 生长 + 停顿1：起点固定 90°
            start_angle = 90
            span = self._currentSpan
        else:
            # 消耗 + 停顿2：终点固定 fixed_end
            remaining = self._maxSpan - self._consumeOffset
            start_angle = fixed_end + remaining
            span = remaining

        painter.drawArc(rc, start_angle * 16, -span * 16)

# 波浪不确定进度环
class WaveIndeterminateProgressRing(QProgressBar):
    """ 波浪进度环 (Sea level rises/falls while wave travels left/right) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 54
        self._time = 0.0

        # ── 可调参数 ─────────────────────────
        self._waveSpeed = 0.025        # 浪速
        self._arcAmplitude = 140       # 弧长振幅（度数）
        self._centerSpan = 180         # 基准弧长（度数）
        self._travelRange = 60         # 起点/终点绕圈摆动的幅度（度数）

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    # ── strokeWidth ────────────────────────────
    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    # ── 控制接口 ──────────────────────────────
    def start(self):
        self._time = 0.0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    # ── 颜色接口 ──────────────────────────────
    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    # ── 可调参数 ──────────────────────────────
    def setWaveSpeed(self, speed: float):
        self._waveSpeed = speed

    def setArcAmplitude(self, deg: int):
        self._arcAmplitude = max(10, min(180, deg))

    def setTravelRange(self, deg: int):
        self._travelRange = max(0, min(180, deg))

    # ── tick ──────────────────────────────────
    def _tick(self):
        self._time += self._waveSpeed
        self.update()

    # ── 绘制 ──────────────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # ── 背景 ──────────────────────────────
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # ── 海洋波浪弧 ────────────────────────
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        pen = QPen(base, self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)

        t = self._time

        # 两个正弦波叠加
        #
        # 弧长 = 基准 + sin(t) * 振幅
        #   → 海面涨（弧长变大）→ 海面落（弧长变小）
        #
        # 中心位置 = cos(t) * 偏移范围
        #   → 浪向右推（中心右移）→ 浪向左回（中心左移）
        #
        # 起点 = 中心 - 弧长/2
        # 终点 = 中心 + 弧长/2

        span = self._centerSpan + int(self._arcAmplitude * math.sin(t))
        center_offset = int(self._travelRange * math.cos(t))

        # 起点角度（12 点钟 = 90°，减去偏移让起点绕圈）
        # 用 mod 360 确保在圆内
        start_angle = (90 - center_offset - span // 2) % 360

        painter.drawArc(rc, start_angle * 16, -span * 16)

# 平面海洋波浪不确定进度环
class OceanWaveIndeterminateProgressRing(QWidget):
    """ 圆形海洋波浪进度指示器 (Circular clip, tide rises/falls, waves travel L/R) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent)

        self._lightBgColor = QColor(0, 0, 0, 0)
        self._darkBgColor = QColor(255, 255, 255, 0)
        self._lightWaveColor = QColor()
        self._darkWaveColor = QColor()

        # ── 浪的参数 ──────────────────
        self._time = 0.0
        self._waveSpeed = 0.08
        self._waveAmplitude = 8       # 浪高（像素）
        self._waveLength = 80         # 波长
        self._tideAmplitude = 12      # 潮汐起伏幅度
        self._tideSpeed = 0.012
        self._fillEnabled = True
        self._diameter = 150          # 圆形直径

        self.setFixedSize(self._diameter, self._diameter)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        if start:
            self.start()

    # ── 控制接口 ──────────────────────
    def start(self):
        self._time = 0.0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    # ── 颜色接口 ──────────────────────
    def lightWaveColor(self):
        return self._lightWaveColor if self._lightWaveColor.isValid() else themeColor()

    def darkWaveColor(self):
        return self._darkWaveColor if self._darkWaveColor.isValid() else themeColor()

    def setCustomWaveColor(self, light, dark):
        self._lightWaveColor = QColor(light)
        self._darkWaveColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self._lightBgColor = QColor(light)
        self._darkBgColor = QColor(dark)
        self.update()

    # ── 可调参数 ──────────────────────
    def setWaveSpeed(self, v: float):
        self._waveSpeed = v

    def setWaveAmplitude(self, px: int):
        self._waveAmplitude = max(2, px)

    def setWaveLength(self, px: int):
        self._waveLength = max(20, px)

    def setTideAmplitude(self, px: int):
        self._tideAmplitude = max(0, px)

    def setDiameter(self, d: int):
        self._diameter = max(20, d)
        self.setFixedSize(self._diameter, self._diameter)

    def setFillEnabled(self, enabled: bool):
        self._fillEnabled = enabled
        self.update()

    # ── tick ──────────────────────────
    def _tick(self):
        self._time += 1
        self.update()

    # ── 绘制 ──────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        d = self._diameter
        w = d
        h = d
        cx = w / 2
        cy = h / 2
        radius = d / 2

        # ── 背景（圆形填充）──────────────
        bg = self._darkBgColor if isDarkTheme() else self._lightBgColor
        if bg.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg)
            painter.drawEllipse(QPointF(cx, cy), radius, radius)

        # ── 圆形裁切 ────────────────────
        clip_path = QPainterPath()
        clip_path.addEllipse(QPointF(cx, cy), radius, radius)
        painter.setClipPath(clip_path)

        # ── 海浪颜色 ────────────────────
        base = self._darkWaveColor if isDarkTheme() else self._lightWaveColor
        if not base.isValid():
            base = themeColor()
        r, g, b = base.red(), base.green(), base.blue()

        # 潮汐水位（圆形中心附近浮动）
        tide = self._tideAmplitude * math.sin(self._time * self._tideSpeed)
        tide = max(-d * 0.35, min(d * 0.35, tide))

        # 基准水面：圆形中心 + 潮汐偏移
        base_y = cy + tide

        phase = self._time * self._waveSpeed

        # ── 生成浪轮廓点 ────────────────
        points = []
        step = 2
        # 多画一些，超出圆形边界确保填满
        for x in range(-10, w + 10, step):
            y = base_y - self._waveAmplitude * math.sin(
                2 * math.pi * (x / self._waveLength) + phase
            )
            # 叠加高频小浪
            y -= self._waveAmplitude * 0.2 * math.sin(
                2 * math.pi * (x / (self._waveLength * 0.35)) + phase * 1.5
            )
            y = max(0, min(h, y))
            points.append(QPointF(x, y))

        if self._fillEnabled and len(points) >= 2:
            # ── 填充海水 ────────────────
            fill = list(points)
            fill.append(QPointF(w + 10, h + 10))   # 右下
            fill.append(QPointF(-10, h + 10))       # 左下
            fill.append(fill[0])

            # 渐变：上浅下深
            grad_top = max(0, base_y - self._waveAmplitude - 5)
            grad_bot = min(h, base_y + self._tideAmplitude + 10)
            if grad_bot <= grad_top:
                grad_bot = grad_top + 1

            gradient = QLinearGradient(0, grad_top, 0, grad_bot)
            gradient.setColorAt(0.0, QColor(r, g, b, 190))
            gradient.setColorAt(1.0, QColor(r, g, b, 50))

            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPolygon(QPolygonF(fill))

        # ── 浪峰描边 ────────────────────
        pen = QPen(QColor(r, g, b, 220), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])

        # ── 取消裁切，画圆形边框 ────────
        painter.setClipping(False)
        pen_border = QPen(QColor(r, g, b, 120), 1.5)
        painter.setPen(pen_border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), radius - 1, radius - 1)

# 新月弧不确定进度环
class CrescentArcIndeterminateProgressRing(QProgressBar):
    """ 新月弧不确定进度环 (Solid crescent arc spinner) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 54
        self._gapAngle = 30           # 缺口大小（度数）
        self._sweepAngle = 0          # 驱动旋转

        self.rotationAni = QPropertyAnimation(self, b'sweepAngle', self)
        self.rotationAni.setDuration(1200)
        self.rotationAni.setStartValue(0)
        self.rotationAni.setEndValue(360)
        self.rotationAni.setLoopCount(-1)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    # ── property ──────────────────────────────
    @Property(int)
    def sweepAngle(self):
        return self._sweepAngle

    @sweepAngle.setter
    def sweepAngle(self, v):
        self._sweepAngle = v
        self.update()

    # ── strokeWidth ───────────────────────────
    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    # ── 控制接口 ──────────────────────────────
    def start(self):
        self._sweepAngle = 0
        self.rotationAni.start()

    def stop(self):
        self.rotationAni.stop()
        self._sweepAngle = 0
        self.update()

    # ── 颜色接口 ──────────────────────────────
    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    # ── 可调参数 ──────────────────────────────
    def setGapAngle(self, angle: int):
        """设置缺口大小（默认 30°）"""
        self._gapAngle = max(5, min(120, angle))
        self.update()

    # ── 绘制 ──────────────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # ── 背景整圆 ────────────────────────
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # ── 纯色月环 ────────────────────────
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()

        pen = QPen(base, self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)

        # 弧跨度 = 整圈 - 缺口
        span = 360 - self._gapAngle

        # 起始角度 = sweepAngle 驱动，让缺口位置旋转
        # 缺口位置 = sweepAngle，弧从缺口后开始画
        start = (-self._sweepAngle + 180) % 360

        painter.drawArc(rc, start * 16, -span * 16)

# 双裂环不确定进度环
class DualGapIndeterminateProgressRing(QProgressBar):
    """ 双裂环不确定进度环 (Two gaps, random direction & angle each move) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 54
        self._gapAngle = 25

        # ── 缺口1 ──────────────────────
        self._gap1Angle = 0
        self._gap1Target = 0
        self._gap1Step = 0        # 每帧移动步长（带方向）
        self._gap1Active = False   # 是否正在移动

        # ── 缺口2 ──────────────────────
        self._gap2Angle = 180
        self._gap2Target = 180
        self._gap2Step = 0
        self._gap2Active = False

        self._moveSpeed = 2        # 基础步长（度数/帧）
        self._minMove = 30         # 最少移动角度
        self._maxMove = 150        # 最多移动角度
        self._minGapDist = 60      # 两缺口最小距离

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(30)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        # 初始各选一个移动
        self._pick_new_move(1)
        self._pick_new_move(2)

        if start:
            self.start()

    # ── strokeWidth ───────────────────────────
    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    # ── 控制接口 ──────────────────────────────
    def start(self):
        self._gap1Angle = 0
        self._gap2Angle = 180
        self._pick_new_move(1)
        self._pick_new_move(2)
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    # ── 颜色接口 ──────────────────────────────
    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    # ── 可调参数 ──────────────────────────────
    def setGapAngle(self, angle: int):
        self._gapAngle = max(5, min(120, angle))
        self.update()

    def setMoveSpeed(self, speed: int):
        self._moveSpeed = max(1, speed)

    # ── 内部方法 ──────────────────────────────
    def _pick_new_move(self, gap_id):
        """为指定缺口选新方向+新目标"""
        # 随机方向：+1 顺时针 / -1 逆时针
        direction = random.choice([-1, 1])

        # 随机移动距离
        move_deg = random.randint(self._minMove, self._maxMove)

        if gap_id == 1:
            self._gap1Target = (self._gap1Angle + direction * move_deg) % 360
            self._gap1Step = direction * self._moveSpeed
            self._gap1Active = True
        else:
            self._gap2Target = (self._gap2Angle + direction * move_deg) % 360
            self._gap2Step = direction * self._moveSpeed
            self._gap2Active = True

    def _tick(self):
        # ── 缺口1 移动 ────────────────
        if self._gap1Active:
            old = self._gap1Angle
            self._gap1Angle = (self._gap1Angle + self._gap1Step) % 360

            # 检查是否越过目标（考虑方向）
            if self._gap1Step > 0:
                # 顺时针：当前 >= 目标 即到达
                if old < self._gap1Target <= self._gap1Angle:
                    self._gap1Angle = self._gap1Target
                    self._gap1Active = False
                    self._pick_new_move(1)
            else:
                # 逆时针
                if self._gap1Angle <= self._gap1Target < old:
                    self._gap1Angle = self._gap1Target
                    self._gap1Active = False
                    self._pick_new_move(1)

        # ── 缺口2 移动 ────────────────
        if self._gap2Active:
            old = self._gap2Angle
            self._gap2Angle = (self._gap2Angle + self._gap2Step) % 360

            if self._gap2Step > 0:
                if old < self._gap2Target <= self._gap2Angle:
                    self._gap2Angle = self._gap2Target
                    self._gap2Active = False
                    self._pick_new_move(2)
            else:
                if self._gap2Angle <= self._gap2Target < old:
                    self._gap2Angle = self._gap2Target
                    self._gap2Active = False
                    self._pick_new_move(2)

        # ── 防重叠保护 ────────────────
        dist = min(
            abs(self._gap1Angle - self._gap2Angle),
            360 - abs(self._gap1Angle - self._gap2Angle)
        )
        if dist < self._minGapDist:
            # 把缺口2推开
            mid = (self._gap1Angle + 180) % 360
            self._gap2Angle = mid
            self._gap2Target = mid
            self._gap2Active = False
            self._pick_new_move(2)

        self.update()

    # ── 绘制 ──────────────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # ── 背景 ──────────────────────
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # ── 纯色弧 ────────────────────
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        pen = QPen(base, self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)

        gap = self._gapAngle

        # 两个缺口位置
        g1 = self._gap1Angle % 360
        g2 = self._gap2Angle % 360

        # 排序
        if g1 > g2:
            g1, g2 = g2, g1

        # 段A: g1+gap → g2
        segA_start = (g1 + gap) % 360
        segA_span = (g2 - g1 - gap) % 360

        # 段B: g2+gap → g1+360
        segB_start = (g2 + gap) % 360
        segB_span = (g1 + 360 - g2 - gap) % 360

        def safe_span(s):
            s = int(s)
            if s <= 1:
                return 0   # 不画
            if s >= 360:
                return 359
            return s

        segA_span = safe_span(segA_span)
        segB_span = safe_span(segB_span)

        if segA_span > 0:
            painter.drawArc(rc, (-segA_start + 180) * 16, -segA_span * 16)
        if segB_span > 0:
            painter.drawArc(rc, (-segB_start + 180) * 16, -segB_span * 16)

# 波纹扩散不确定进度环
class RippleIndeterminateProgressRing(QProgressBar):
    """波纹扩散进度环（Material Design style · 无限循环）"""

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        # ── 外观 ────────────────────────
        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()

        self._baseRadius = 24
        self._maxRadius = 48
        self._strokeWidth = 3

        # ── 波纹配置 ────────────────────
        self._rippleCount = 3
        self._duration = 1800        # ms
        self._interval = 30          # ms per frame
        self._delayBetween = 500     # ms

        # ── 波纹状态 ────────────────────
        # 每个 ripple: { elapsed, alpha, radius }
        self._ripples = []
        for i in range(self._rippleCount):
            self._ripples.append({
                'elapsed': -i * self._delayBetween,  # 负数 = 还没开始
                'radius': self._baseRadius,
                'alpha': 0
            })

        # ── 定时器 ──────────────────────
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(self._interval)

        size = self._maxRadius + self._strokeWidth + 6
        self.setFixedSize(size * 2, size * 2)

        if start:
            self.start()

    # ── property ────────────────────────────
    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    # ── 控制 ────────────────────────────────
    def start(self):
        for i, r in enumerate(self._ripples):
            r['elapsed'] = -i * self._delayBetween
            r['radius'] = self._baseRadius
            r['alpha'] = 0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    # ── 颜色 ────────────────────────────────
    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    # ── 核心：每帧更新 ──────────────────────
    def _tick(self):
        for r in self._ripples:
            r['elapsed'] += self._interval

            if r['elapsed'] < 0:
                # 还在 delay 阶段
                r['radius'] = self._baseRadius
                r['alpha'] = 0
                continue

            if r['elapsed'] >= self._duration:
                # ★ 生命周期结束 → 重置，自动开始下一轮
                r['elapsed'] = 0

            # progress: 0 → 1
            progress = r['elapsed'] / self._duration

            # ease-out cubic
            ease = 1.0 - (1.0 - progress) ** 3

            r['radius'] = self._baseRadius + (self._maxRadius - self._baseRadius) * ease
            r['alpha'] = max(0, int(255 * (1.0 - progress)))

        self.update()

    # ── 绘制 ────────────────────────────────
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # 背景
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            painter.fillRect(self.rect(), bg)

        # 波纹（从外到内画，小半径盖在大半径上面更好看）
        base_color = self.darkBarColor() if isDarkTheme() else self.lightBarColor()

        for r in reversed(self._ripples):
            if r['alpha'] <= 0:
                continue

            color = QColor(base_color)
            color.setAlpha(r['alpha'])
            pen = QPen(color, self._strokeWidth, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            rad = r['radius']
            rc = QRectF(cx - rad, cy - rad, rad * 2, rad * 2)
            painter.drawEllipse(rc)   # 用 drawEllipse 比 drawArc 360 更干净

# 胶囊轨道不确定进度环
class CapsuleTrackIndeterminateProgressRing(QProgressBar):
    """ 胶囊轨道进度环 (Linear / Vercel style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 60
        self._capsuleSpan = 30        # 胶囊弧长（度数）
        self._angle = 0

        self.rotationAni = QPropertyAnimation(self, b'angle', self)
        self.rotationAni.setDuration(1000)
        self.rotationAni.setStartValue(0)
        self.rotationAni.setEndValue(360)
        self.rotationAni.setLoopCount(-1)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @Property(int)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, v):
        self._angle = v
        self.update()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._angle = 0
        self.rotationAni.start()

    def stop(self):
        self.rotationAni.stop()
        self._angle = 0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # 背景
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # 胶囊弧
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        pen = QPen(base, self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)
        start = (-self._angle + 180) % 360
        painter.drawArc(rc, start * 16, -self._capsuleSpan * 16)

# 扫描渐变不确定进度环
class ConicSweepIndeterminateProgressRing(QProgressBar):
    """ 扫描渐变不确定进度环 (Apple HIG / SwiftUI style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 6
        self._ringRadius = 60
        self._sweepAngle = 0

        self.rotationAni = QPropertyAnimation(self, b'sweepAngle', self)
        self.rotationAni.setDuration(1800)
        self.rotationAni.setStartValue(0)
        self.rotationAni.setEndValue(360)
        self.rotationAni.setLoopCount(-1)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @Property(int)
    def sweepAngle(self):
        return self._sweepAngle

    @sweepAngle.setter
    def sweepAngle(self, v):
        self._sweepAngle = v
        self.update()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._sweepAngle = 0
        self.rotationAni.start()

    def stop(self):
        self.rotationAni.stop()
        self._sweepAngle = 0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        # 背景
        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            pen = QPen(bg, self._strokeWidth)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rc, 0, 360 * 16)

        # 锥形渐变：从主色 → 半透明 → 透明 → 主色
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()
        r, g, b = base.red(), base.green(), base.blue()

        gradient = QConicalGradient(cx, cy, self._sweepAngle)

        gradient.setColorAt(0.0, base)                     # 亮斑（头）
        gradient.setColorAt(0.15, QColor(r, g, b, 180))
        gradient.setColorAt(0.45, QColor(r, g, b, 60))
        gradient.setColorAt(0.75, QColor(r, g, b, 0))       # 全透
        gradient.setColorAt(1.0, base)                     # 回到亮斑

        pen = QPen(QBrush(gradient), self._strokeWidth)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)
        painter.drawArc(rc, 0, 360 * 16)

# 流体渐变不确定进度环
class FluidGradientIndeterminateProgressRing(QProgressBar):
    """ 流体渐变进度环 (Instagram / Apple Music style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._strokeWidth = 7
        self._ringRadius = 64
        self._fluidAngle = 0

        self.rotationAni = QPropertyAnimation(self, b'fluidAngle', self)
        self.rotationAni.setDuration(3000)
        self.rotationAni.setStartValue(0)
        self.rotationAni.setEndValue(360)
        self.rotationAni.setLoopCount(-1)

        outer = self._ringRadius + self._strokeWidth / 2 + 2
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    @Property(int)
    def fluidAngle(self):
        return self._fluidAngle

    @fluidAngle.setter
    def fluidAngle(self, v):
        self._fluidAngle = v
        self.update()

    def getStrokeWidth(self):
        return self._strokeWidth

    def setStrokeWidth(self, w):
        self._strokeWidth = w
        self.update()

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._fluidAngle = 0
        self.rotationAni.start()

    def stop(self):
        self.rotationAni.stop()
        self._fluidAngle = 0
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                        self._ringRadius * 2, self._ringRadius * 2)
            painter.setPen(QPen(bg, self._strokeWidth, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawArc(rc, 0, 360 * 16)

        # 流体多色渐变
        gradient = QConicalGradient(cx, cy, self._fluidAngle)

        stops = [
            (0.00, "#FF006E"),
            (0.13, "#C918D1"),
            (0.25, "#3A0CA3"),
            (0.38, "#4361EE"),
            (0.50, "#4CC9F0"),
            (0.63, "#2EC4B6"),
            (0.75, "#90BE6D"),
            (0.88, "#F9C74F"),
            (1.00, "#FF006E"),
        ]
        for pos, color_hex in stops:
            gradient.setColorAt(pos, QColor(color_hex))

        pen = QPen(QBrush(gradient),self._strokeWidth,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        rc = QRectF(cx - self._ringRadius, cy - self._ringRadius,
                    self._ringRadius * 2, self._ringRadius * 2)
        painter.drawArc(rc, 0, 360 * 16)

# 心电图脉冲不确定进度环
class ECGPulseIndeterminateProgressRing(QProgressBar):
    """ 心电图脉冲进度环 (watchOS style) """

    def __init__(self, parent=None, start=True):
        super().__init__(parent=parent)

        self.lightBackgroundColor = QColor(0, 0, 0, 0)
        self.darkBackgroundColor = QColor(255, 255, 255, 0)
        self._lightBarColor = QColor()
        self._darkBarColor = QColor()
        self._ringRadius = 52
        self._time = 0
        self._speed = 0.12

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.setInterval(16)

        outer = self._ringRadius + 14
        self.setFixedSize(int(outer * 2), int(outer * 2))

        if start:
            self.start()

    def getStrokeWidth(self):
        return 4

    def setStrokeWidth(self, w):
        pass

    strokeWidth = Property(int, getStrokeWidth, setStrokeWidth)

    def start(self):
        self._time = 0
        self._timer.start()

    def stop(self):
        self._timer.stop()
        self.update()

    def lightBarColor(self):
        return self._lightBarColor if self._lightBarColor.isValid() else themeColor()

    def darkBarColor(self):
        return self._darkBarColor if self._darkBarColor.isValid() else themeColor()

    def setCustomBarColor(self, light, dark):
        self._lightBarColor = QColor(light)
        self._darkBarColor = QColor(dark)
        self.update()

    def setCustomBackgroundColor(self, light, dark):
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def _tick(self):
        self._time += self._speed
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2
        base = self.darkBarColor() if isDarkTheme() else self.lightBarColor()

        bg = self.darkBackgroundColor if isDarkTheme() else self.lightBackgroundColor
        if bg.alpha() > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(bg)
            painter.drawEllipse(QPoint(int(cx), int(cy)),
                                self._ringRadius + 8, self._ringRadius + 8)

        painter.translate(cx, cy)

        # 生成 ECG 波形路径
        steps = 120
        for i in range(steps):
            t = i / steps * 2 * math.pi
            # 基础圆 + ECG 波形调制
            ecg = math.sin(t * 3 + self._time) * 6 * math.exp(-((t - self._time * 0.5) % (2*math.pi))**2 * 4)
            radius = self._ringRadius + ecg

            angle = t
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            # 颜色随波形强度变化
            intensity = abs(ecg) / 6.0
            alpha = int(100 + 155 * intensity)
            c = QColor(base)
            c.setAlpha(alpha)

            pen = QPen(c, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)

            if i > 0:
                painter.drawLine(int(self._last_x), int(self._last_y), int(x), int(y))
            self._last_x, self._last_y = x, y