from ctypes import wintypes
from typing import Union

from qtpy.QtWidgets import QWidget, QHBoxLayout
from qtpy.QtGui import QIcon

from qfluentwidgets import NavigationItemPosition, FluentIconBase, NavigationTreeWidget, NavigationInterface, qrouter
from qfluentwidgets.window.fluent_window import FluentWindowBase, FluentTitleBar
from win32con import WM_SYSCOMMAND, SC_MINIMIZE


# 极简流畅窗口
class LiteFluentWindow(FluentWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitleBar(FluentTitleBar(self))
        self.titleBar.setContentsMargins(10, 0, 0, 0)

        self.navigationInterface = NavigationInterface(self, showReturnButton=True)
        self.navigationInterface.hide()

        self.widgetLayout = QHBoxLayout()

        self.hBoxLayout.addLayout(self.widgetLayout)
        self.hBoxLayout.setStretchFactor(self.widgetLayout, 1)

        self.widgetLayout.addWidget(self.stackedWidget)
        self.widgetLayout.setContentsMargins(0, 48, 0, 0)

        self.titleBar.raise_()

    def addSubInterface(self, interface: QWidget, icon: Union[FluentIconBase, QIcon, str], text: str,
                        position=NavigationItemPosition.TOP, parent=None, isTransparent=False) -> NavigationTreeWidget:
        if not interface.objectName():
            raise ValueError("The object name of `interface` can't be empty string.")

        parentRouteKey = parent
        if parent and isinstance(parent, QWidget):
            parentRouteKey = parent.objectName()
            if not parentRouteKey:
                raise ValueError("The object name of `parent` can't be empty string.")

        interface.setProperty("isStackedTransparent", isTransparent)
        self.stackedWidget.addWidget(interface)

        routeKey = interface.objectName()
        item = self.navigationInterface.addItem(
            routeKey=routeKey,
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parentRouteKey
        )

        if self.stackedWidget.count() == 1:
            self.stackedWidget.currentChanged.connect(self._onCurrentInterfaceChanged)
            self.navigationInterface.setCurrentItem(routeKey)
            qrouter.setDefaultRouteKey(self.stackedWidget, routeKey)

        self._updateStackedBackground()

        return item

    def removeInterface(self, interface, isDelete=False):
        self.navigationInterface.removeWidget(interface.objectName())
        self.stackedWidget.removeWidget(interface)
        interface.hide()

        if isDelete:
            interface.deleteLater()

    def resizeEvent(self, e):
        self.titleBar.move(0, 0)
        self.titleBar.resize(self.width(), self.titleBar.height())

# 无边框流畅窗口
class BorderlessFluentWindow(FluentWindowBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.titleBar.hide()

        self.navigationInterface = NavigationInterface(self, showReturnButton=True)
        self.navigationInterface.hide()

        self.widgetLayout = QHBoxLayout()

        self.hBoxLayout.addLayout(self.widgetLayout)

        self.widgetLayout.addWidget(self.stackedWidget)

    def addSubInterface(self, interface: QWidget, icon: Union[FluentIconBase, QIcon, str], text: str,
                        position=NavigationItemPosition.TOP, parent=None, isTransparent=False) -> NavigationTreeWidget:
        if not interface.objectName():
            raise ValueError("The object name of `interface` can't be empty string.")

        parentRouteKey = parent
        if parent and isinstance(parent, QWidget):
            parentRouteKey = parent.objectName()
            if not parentRouteKey:
                raise ValueError("The object name of `parent` can't be empty string.")

        interface.setProperty("isStackedTransparent", isTransparent)
        self.stackedWidget.addWidget(interface)

        routeKey = interface.objectName()
        item = self.navigationInterface.addItem(
            routeKey=routeKey,
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            position=position,
            tooltip=text,
            parentRouteKey=parentRouteKey
        )

        if self.stackedWidget.count() == 1:
            self.stackedWidget.currentChanged.connect(self._onCurrentInterfaceChanged)
            self.navigationInterface.setCurrentItem(routeKey)
            qrouter.setDefaultRouteKey(self.stackedWidget, routeKey)

        self._updateStackedBackground()

        return item

    def removeInterface(self, interface, isDelete=False):
        self.navigationInterface.removeWidget(interface.objectName())
        self.stackedWidget.removeWidget(interface)
        interface.hide()

        if isDelete:
            interface.deleteLater()

# 固定无边框流畅窗口
class FixedBorderlessFluentWindow(BorderlessFluentWindow):
    def nativeEvent(self, eventType, message):
        # 仅处理 Windows 消息
        if eventType == "windows_generic_MSG":
            # 解析消息结构
            msg = wintypes.MSG.from_address(message.__int__())

            # 拦截系统命令消息
            if msg.message == WM_SYSCOMMAND:
                # 检查是否是点击最小化按钮或任务栏最小化
                if (msg.wParam & 0xFFF0) == SC_MINIMIZE:
                    return True, 0

        # 其他消息交给默认处理
        return super().nativeEvent(eventType, message)