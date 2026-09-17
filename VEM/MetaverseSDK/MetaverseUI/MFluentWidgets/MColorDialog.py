from qtpy.QtCore import QPoint, Qt, QEvent, QPropertyAnimation, QEasingCurve
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QDialog, QFrame, QHBoxLayout, QWidget, QPushButton, QLabel, QVBoxLayout, \
    QGraphicsDropShadowEffect, QApplication, QGraphicsOpacityEffect
from qfluentwidgets import SingleDirectionScrollArea, PrimaryPushButton, FluentStyleSheet
from qfluentwidgets.components.dialog_box.color_dialog import HuePanel, BrightnessSlider, HexColorLineEdit, \
    ColorLineEdit, OpacityLineEdit, ColorCard
from qtpy.QtCore import Signal


# 无遮罩颜色对话框
class NoMaskColorDialog(QDialog):
    """ Color dialog (no mask version)

    内部仍保留一个名为 centerWidget 的 QFrame 作为内容容器：
    官方 QSS 里 `#centerWidget` 负责白底与圆角边框，阴影也挂在它上面。
    """

    colorChanged = Signal(QColor)

    #: 阴影留白 调大到 60 可完整显示 blur=60 的阴影
    #: 若希望非模态时四周完全不挡点击 可设为 0 并改用较小 blur
    SHADOW_MARGIN = 40

    #: 内容区尺寸
    CONTENT_WIDTH = 488
    CONTENT_HEIGHT = 696      # enableAlpha=True 时额外 +40

    def __init__(self, color, title: str, parent=None, enableAlpha=False):
        """
        Parameters
        ----------
        color: `QColor` | `GlobalColor` | str
            initial color

        title: str
            the title of dialog

        parent: QWidget
            parent widget

        enableAlpha: bool
            whether to enable the alpha channel
        """
        super().__init__(parent=parent)
        self.enableAlpha = enableAlpha
        if not enableAlpha:
            color = QColor(color)
            color.setAlpha(255)

        # ---- 无遮罩窗口自身的初始化 ----
        self._isDraggable = True
        self._dragPos = QPoint()
        self._shadowMargin = self.SHADOW_MARGIN

        # 内容容器，所有子控件的父对象
        self.widget = QFrame(self, objectName='centerWidget')

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._hBoxLayout = QHBoxLayout(self)
        self._hBoxLayout.setSpacing(0)
        self._hBoxLayout.setContentsMargins(self._shadowMargin, self._shadowMargin,
                                            self._shadowMargin, self._shadowMargin)
        self._hBoxLayout.addWidget(self.widget)

        # ---- 取色器业务控件----
        self.oldColor = QColor(color)
        self.color = QColor(color)

        self.scrollArea = SingleDirectionScrollArea(self.widget)
        self.scrollWidget = QWidget(self.scrollArea)

        self.buttonGroup = QFrame(self.widget)
        self.yesButton = PrimaryPushButton("确认", self.buttonGroup)
        self.cancelButton = QPushButton("取消", self.buttonGroup)

        self.titleLabel = QLabel(title, self.scrollWidget)
        self.huePanel = HuePanel(color, self.scrollWidget)
        self.newColorCard = ColorCard(color, self.scrollWidget, enableAlpha)
        self.oldColorCard = ColorCard(color, self.scrollWidget, enableAlpha)
        self.brightSlider = BrightnessSlider(color, self.scrollWidget)

        self.editLabel = QLabel("编辑颜色", self.scrollWidget)
        self.redLabel = QLabel("红色", self.scrollWidget)
        self.blueLabel = QLabel("蓝色", self.scrollWidget)
        self.greenLabel = QLabel("绿色", self.scrollWidget)
        self.opacityLabel = QLabel("透明度", self.scrollWidget)
        self.hexLineEdit = HexColorLineEdit(color, self.scrollWidget, enableAlpha)
        self.redLineEdit = ColorLineEdit(self.color.red(), self.scrollWidget)
        self.greenLineEdit = ColorLineEdit(self.color.green(), self.scrollWidget)
        self.blueLineEdit = ColorLineEdit(self.color.blue(), self.scrollWidget)
        self.opacityLineEdit = OpacityLineEdit(self.color.alpha(), self.scrollWidget)

        self.vBoxLayout = QVBoxLayout(self.widget)

        self.__initWidget()

    def __initWidget(self):
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setViewportMargins(48, 24, 0, 24)
        self.scrollArea.setWidget(self.scrollWidget)

        # 固定尺寸：窗口不再由父窗口大小决定，必须自己给确定值
        extra = 40 * int(self.enableAlpha)
        self.widget.setFixedSize(self.CONTENT_WIDTH, self.CONTENT_HEIGHT + extra)
        self.scrollWidget.resize(440, 560 + extra)
        self.buttonGroup.setFixedSize(486, 81)
        self.yesButton.setFixedWidth(216)
        self.cancelButton.setFixedWidth(216)

        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 80))
        # 不再调用 setMaskColor —— 没有遮罩了

        self.__setQss()
        self.__initLayout()
        self.__initDrag()
        self.__connectSignalToSlot()

        self.adjustSize()      # 按内容 + 阴影留白算出窗口尺寸
        self.centerToParent()  # 居中到父窗口

    def __initDrag(self):
        """ 让标题栏区域可以拖动窗口 """
        self.scrollWidget.installEventFilter(self)
        self.titleLabel.installEventFilter(self)
        self.scrollWidget.setMouseTracking(True)

    def __initLayout(self):
        self.huePanel.move(0, 46)
        self.newColorCard.move(288, 46)
        self.oldColorCard.move(288, self.newColorCard.geometry().bottom() + 1)
        self.brightSlider.move(0, 324)

        self.editLabel.move(0, 385)
        self.redLineEdit.move(0, 426)
        self.greenLineEdit.move(0, 470)
        self.blueLineEdit.move(0, 515)
        self.redLabel.move(144, 434)
        self.greenLabel.move(144, 478)
        self.blueLabel.move(144, 524)
        self.hexLineEdit.move(196, 381)

        if self.enableAlpha:
            self.opacityLineEdit.move(0, 560)
            self.opacityLabel.move(144, 567)
        else:
            self.opacityLineEdit.hide()
            self.opacityLabel.hide()

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.scrollArea, 1)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)

        self.yesButton.move(24, 25)
        self.cancelButton.move(250, 25)

    def __setQss(self):
        self.editLabel.setObjectName('editLabel')
        self.titleLabel.setObjectName('titleLabel')
        self.yesButton.setObjectName('yesButton')
        self.cancelButton.setObjectName('cancelButton')
        self.buttonGroup.setObjectName('buttonGroup')
        FluentStyleSheet.COLOR_DIALOG.apply(self)
        self.titleLabel.adjustSize()
        self.editLabel.adjustSize()

    # ==================================================================
    #  窗口外观
    # ==================================================================
    def setShadowEffect(self, blurRadius=60, offset=(0, 10), color=QColor(0, 0, 0, 80)):
        """ add shadow to dialog """
        effect = QGraphicsDropShadowEffect(self.widget)
        effect.setBlurRadius(blurRadius)
        effect.setOffset(*offset)
        effect.setColor(color)
        self.widget.setGraphicsEffect(None)
        self.widget.setGraphicsEffect(effect)

    def setShadowMargin(self, margin: int):
        """ 阴影留白：内容四周保留多少像素（用于显示阴影、同时是窗口不可见边框） """
        self._shadowMargin = int(margin)
        self._hBoxLayout.setContentsMargins(self._shadowMargin, self._shadowMargin,
                                            self._shadowMargin, self._shadowMargin)
        self.adjustSize()

    def shadowMargin(self) -> int:
        return self._shadowMargin

    def setMaskColor(self, color: QColor):
        """ 兼容性空实现：无遮罩版本不需要此接口，调用它不会有任何效果 """
        return

    def isClosableOnMaskClicked(self):
        return False

    def setClosableOnMaskClicked(self, isClosable: bool):
        """ 兼容性空实现：没有遮罩，自然也不存在点遮罩关闭 """
        return

    def setDraggable(self, draggable: bool):
        self._isDraggable = draggable

    def isDraggable(self) -> bool:
        return self._isDraggable

    def centerToParent(self):
        """ 在父窗口（无父窗口时用屏幕）居中 """
        parent = self.parentWidget()
        if parent is not None:
            geo = parent.window().frameGeometry()
        else:
            geo = QApplication.primaryScreen().availableGeometry()
        center = geo.center()

        screen = QApplication.primaryScreen().availableGeometry()
        x = max(screen.x(), min(center.x() - self.width() // 2,
                                screen.right() - self.width()))
        y = max(screen.y(), min(center.y() - self.height() // 2,
                                screen.bottom() - self.height()))
        self.move(x, y)

    # ==================================================================
    #  拖动
    # ==================================================================
    def _startDrag(self, globalPos):
        self._dragPos = globalPos - self.frameGeometry().topLeft()

    def _doDrag(self, globalPos):
        if self._dragPos.isNull():
            return
        self.move(globalPos - self._dragPos)

    def _endDrag(self):
        self._dragPos = QPoint()

    def eventFilter(self, obj, e):
        """ 标题栏区域（huePanel 上方那条）按下并移动 = 拖动整个窗口 """
        if not self.isDraggable():
            return super().eventFilter(obj, e)

        if obj in (self.scrollWidget, self.titleLabel):
            # 只认标题栏：y 小于 huePanel 的顶边
            local = obj.mapTo(self.scrollWidget, e.pos()) \
                if hasattr(e, 'pos') else QPoint()
            inTitleBar = 0 <= local.y() < self.huePanel.y()

            if e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
                if inTitleBar:
                    self._startDrag(obj.mapToGlobal(e.pos()))
                    return True
            elif e.type() == QEvent.MouseMove and inTitleBar:
                self._doDrag(obj.mapToGlobal(e.pos()))
                return True
            elif e.type() == QEvent.MouseButtonRelease:
                self._endDrag()

        return super().eventFilter(obj, e)

    # ==================================================================
    #  淡入淡出
    # ==================================================================
    def showEvent(self, e):
        self.updateStyle()
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        ani = QPropertyAnimation(effect, b'opacity', self)
        ani.setStartValue(0)
        ani.setEndValue(1)
        ani.setDuration(200)
        ani.setEasingCurve(QEasingCurve.InSine)
        ani.finished.connect(lambda: self.setGraphicsEffect(None))
        ani.start()
        super(QDialog, self).showEvent(e)

    def done(self, code):
        self.widget.setGraphicsEffect(None)
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        ani = QPropertyAnimation(effect, b'opacity', self)
        ani.setStartValue(1)
        ani.setEndValue(0)
        ani.setDuration(100)
        ani.finished.connect(lambda: self._onDone(code))
        ani.start()

    def _onDone(self, code):
        self.setGraphicsEffect(None)
        QDialog.done(self, code)

    # ==================================================================
    #  取色逻辑（原 ColorDialog）
    # ==================================================================
    def setColor(self, color, movePicker=True):
        """ set color """
        self.color = QColor(color)
        self.brightSlider.setColor(color)
        self.newColorCard.setColor(color)
        self.hexLineEdit.setColor(color)
        self.redLineEdit.setText(str(color.red()))
        self.blueLineEdit.setText(str(color.blue()))
        self.greenLineEdit.setText(str(color.green()))
        if movePicker:
            self.huePanel.setColor(color)

    def __onHueChanged(self, color):
        """ hue changed slot """
        self.color.setHsv(
            color.hue(), color.saturation(), self.color.value(), self.color.alpha())
        self.setColor(self.color)

    def __onBrightnessChanged(self, color):
        """ brightness changed slot """
        self.color.setHsv(
            self.color.hue(), self.color.saturation(), color.value(), self.color.alpha())
        self.setColor(self.color, False)

    def __onRedChanged(self, red):
        """ red channel changed slot """
        self.color.setRed(int(red))
        self.setColor(self.color)

    def __onBlueChanged(self, blue):
        """ blue channel changed slot """
        self.color.setBlue(int(blue))
        self.setColor(self.color)

    def __onGreenChanged(self, green):
        """ green channel changed slot """
        self.color.setGreen(int(green))
        self.setColor(self.color)

    def __onOpacityChanged(self, opacity):
        """ opacity channel changed slot """
        self.color.setAlpha(int(int(opacity) / 100 * 255))
        self.setColor(self.color)

    def __onHexColorChanged(self, color):
        """ hex color changed slot """
        self.color.setNamedColor("#" + color)
        self.setColor(self.color)

    def __onYesButtonClicked(self):
        """ yes button clicked slot """
        self.accept()
        if self.color != self.oldColor:
            self.colorChanged.emit(self.color)

    def updateStyle(self):
        """ update style sheet """
        self.setStyle(QApplication.style())
        self.titleLabel.adjustSize()
        self.editLabel.adjustSize()
        self.redLabel.adjustSize()
        self.greenLabel.adjustSize()
        self.blueLabel.adjustSize()
        self.opacityLabel.adjustSize()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.cancelButton.clicked.connect(self.reject)
        self.yesButton.clicked.connect(self.__onYesButtonClicked)

        self.huePanel.colorChanged.connect(self.__onHueChanged)
        self.brightSlider.colorChanged.connect(self.__onBrightnessChanged)

        self.redLineEdit.valueChanged.connect(self.__onRedChanged)
        self.blueLineEdit.valueChanged.connect(self.__onBlueChanged)
        self.greenLineEdit.valueChanged.connect(self.__onGreenChanged)
        self.hexLineEdit.valueChanged.connect(self.__onHexColorChanged)
        self.opacityLineEdit.valueChanged.connect(self.__onOpacityChanged)