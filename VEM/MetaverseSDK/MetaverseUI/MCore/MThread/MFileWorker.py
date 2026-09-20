import shutil
from qtpy.QtCore import Signal, QThread


# 删除文件夹
class DeleteFolder(QThread):
    """
    删除文件夹
    """
    finished = Signal()
    error = Signal(str)

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path

    def run(self):
        try:
            shutil.rmtree(self.path)
        except FileNotFoundError:
            self.error.emit("删除失败 环境目录不存在")
        except PermissionError:
            self.error.emit("删除失败 权限不足")
        except OSError as a:
            self.error.emit(a)
        except Exception as e:
            self.error.emit(f"发生错误 {e}")
        # 没有触发异常
        else:
            self.finished.emit()