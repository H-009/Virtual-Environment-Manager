import os
import zipfile
from qtpy.QtCore import QThread, Signal


# 解压线程
class UnzipWorker(QThread):
    """
    解压线程
    progress: current, total
    finished: 解压完成
    error: 出错
    """
    progress = Signal(int, int)
    finished = Signal()
    error = Signal(str)

    def __init__(self, zip_path: str, extract_to: str):
        super().__init__()
        self.zip_path = zip_path
        self.extract_to = extract_to

    def run(self):
        try:
            if not os.path.exists(self.extract_to):
                os.makedirs(self.extract_to,exist_ok=True)

            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                members = zip_ref.namelist()
                total = len(members)

                for i, member in enumerate(members, start=1):
                    zip_ref.extract(member, self.extract_to)
                    self.progress.emit(i, total)

            self.finished.emit()

        except zipfile.BadZipFile:
            self.error.emit("文件损坏或不是有效的zip文件")
        except PermissionError as a:
            self.error.emit("文件被占用")
            print(a)
        except Exception as e:
            self.error.emit(str(e))

# 快速解压线程
class UnzipWorkerByte(QThread):
    """
    快速解压 1MB缓冲
    实时字节解压进度
    """
    progress = Signal(int, int)   # current_bytes, total_bytes
    finished = Signal()
    error = Signal(str)

    def __init__(self, zip_path, extract_to):
        super().__init__()
        self.zip_path = zip_path
        self.extract_to = extract_to

    def run(self):
        try:
            os.makedirs(self.extract_to, exist_ok=True)

            with zipfile.ZipFile(self.zip_path, 'r') as zf:
                total_bytes = sum(info.file_size for info in zf.infolist())
                current_bytes = 0

                for info in zf.infolist():
                    # 目录跳过
                    if info.is_dir():
                        continue

                    src = zf.open(info)
                    dst_path = os.path.join(self.extract_to, info.filename)

                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

                    with open(dst_path, 'wb') as dst:
                        while True:
                            chunk = src.read(1024 * 1024)  # 1MB 缓冲
                            if not chunk:
                                break
                            dst.write(chunk)
                            current_bytes += len(chunk)
                            self.progress.emit(current_bytes, total_bytes)

            self.finished.emit()

        except zipfile.BadZipFile:
            self.error.emit("文件损坏或不是有效的 zip 文件")
        except PermissionError:
            self.error.emit("文件被占用或无权限")
        except Exception as e:
            self.error.emit(str(e))