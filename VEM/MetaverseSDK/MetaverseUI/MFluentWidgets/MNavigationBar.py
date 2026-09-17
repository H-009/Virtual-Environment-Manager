from qfluentwidgets import BreadcrumbBar, setFont


# 面包屑导航栏
class BreadcrumbNavigationBar(BreadcrumbBar):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSpacing(15)
        setFont(self, 24)