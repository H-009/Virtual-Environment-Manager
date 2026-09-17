from qtpy.QtWidgets import QWidget


class TransparentWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("QWidget{background: transparent}")  # 视图透明