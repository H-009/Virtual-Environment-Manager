import shutil
import time
from pathlib import Path

import requests
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
from typing import List, Tuple, Dict

import tool




class EmbBatchProcessing(QThread):
    """
    EMB批处理
    """
    finished = pyqtSignal()
    error = pyqtSignal(str)
    emb_dir = pyqtSignal(str)
    update_title = pyqtSignal(str)

    def __init__(self, emb_batch_set,file_path_pth,url,pip):
        super().__init__()
        self.file_path_pth = file_path_pth
        self.emb_batch_set = emb_batch_set
        self.url = url
        self.pip = pip
        # 中断标记
        self.interrupt_marker = True

    def run(self):
        try:
            if "解锁第三方库" in self.emb_batch_set:  # 如果在批处理列表中
                self.UnlockPTH()  # 解锁PTH
            if "创建启动脚本" in self.emb_batch_set:
                self.CreateBat()  # 创建启动脚本
            if "自动获取pip并安装" in self.emb_batch_set and "使用外部CMD创建" not in self.emb_batch_set and "CMD创建后保持打开" not in self.emb_batch_set:
                self.AutoGetPIPInstall()  # 自动获取pip并安装
            if "自动获取pip并安装" in self.emb_batch_set and "使用外部CMD创建" in self.emb_batch_set and "CMD创建后保持打开" not in self.emb_batch_set:
                self.AutoGetPIPInstallCMD()  # 自动获取pip并安装 打开cmd
            if "自动获取pip并安装" in self.emb_batch_set and "使用外部CMD创建" in self.emb_batch_set and "CMD创建后保持打开" in self.emb_batch_set:
                self.AutoGetPIPInstallOpenCMD()  # 自动获取pip并安装 打开cmd 保持打开
            if "自定义获取pip" in self.emb_batch_set and "使用外部CMD创建" not in self.emb_batch_set and "CMD创建后保持打开" not in self.emb_batch_set:
                self.GetPIP()  # 获取pip
            if "自定义获取pip" in self.emb_batch_set and "使用外部CMD创建" in self.emb_batch_set and "CMD创建后保持打开" not in self.emb_batch_set:
                self.GetPIP(True)  # 获取pip 打开cmd
            if "自定义获取pip" in self.emb_batch_set and "使用外部CMD创建" in self.emb_batch_set and "CMD创建后保持打开" in self.emb_batch_set:
                self.GetPIPOpen()  # 获取pip 打开cmd 保持打开
            if "自定义安装pip" in self.emb_batch_set and "使用外部CMD创建" not in self.emb_batch_set and "CMD创建后保持打开" not in self.emb_batch_set:
                self.InstallPIP()  # 安装pip
            if "自定义安装pip" in self.emb_batch_set and "使用外部CMD创建" in self.emb_batch_set and "CMD创建后保持打开" not in self.emb_batch_set:
                self.InstallPIP(True)  # 安装pip 打开cmd
            if "自定义安装pip" in self.emb_batch_set and "使用外部CMD创建" in self.emb_batch_set and "CMD创建后保持打开" in self.emb_batch_set:
                self.InstallPIPOpen()  # 安装pip 打开cmd 保持打开

            if self.interrupt_marker:
                self.finished.emit()

        except Exception as e:
            self.error.emit(f"发生错误 {e}")

    def UnlockPTH(self):
        """解锁PTH"""
        old_keyword = "import site"
        new_line = "import site"

        pth_file = next(Path(self.file_path_pth).glob("*._pth")) # 查找_pth 只有一个_pth

        with open(pth_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(pth_file, "w", encoding="utf-8") as f:
            for line in lines:
                if old_keyword in line:
                    f.write(new_line + "\n")
                else:
                    f.write(line)

    def CreateBat(self):
        """创建启动脚本"""
        # 分割路径
        p = Path(self.file_path_pth)

        env_dir = p.name  # 最后路径
        bat_dir = p.parent  # 剩下路径


        if str(bat_dir).endswith("/") or str(bat_dir).endswith("\\"):  # 以/\结尾
            path = f"{bat_dir}python.bat"
        else:
            path = f"{bat_dir}\python.bat"

        bat = Path(path)

        content = rf"""@echo off
        
echo VEM虚拟环境管理器-便携式环境启动脚本
echo v1.5.9.Bate
echo.

set "CURDIR=%~dp0"
set "ENVDIR={env_dir}\"
set "PYTHON_EXE=%CURDIR%%ENVDIR%python.exe"

echo 当前目录: %CURDIR%
echo 环境文件夹: %ENVDIR%
echo 解释器路径: %PYTHON_EXE%

if not exist "%ENVDIR%" (
    echo.
    echo 环境文件夹丢失
    echo 期望路径: %CURDIR%%ENVDIR%
    echo.
    pause
)
 
if exist "%PYTHON_EXE%" (
    echo.
    if exist "%CURDIR%%ENVDIR%\Scripts" (
        set "PATH=%CURDIR%%ENVDIR%;%CURDIR%%ENVDIR%\Scripts;%PATH%"
        echo PATH: %CURDIR%%ENVDIR% 加入当前会话环境
        echo PATH: %CURDIR%%ENVDIR%Scripts 加入当前会话环境
    ) else (
        set "PATH=%CURDIR%%ENVDIR%;%PATH%"
        echo 环境目录: %CURDIR%%ENVDIR% 加入当前会话环境
    )
    echo 当前会话环境优先级已设为最高
    echo.
    echo 环境已启动
    echo.
    cd /d %CURDIR%%ENVDIR%
    cmd \k
) else (
    echo.
    echo python 解释器丢失
    echo 期望路径: %PYTHON_EXE%
    echo.
    pause
)"""

        bat.write_text(content, encoding="gbk")
        self.emb_dir.emit(path)

    def AutoGetPIPInstall(self):
        """自动获取并安装pip"""
        pip_path = tool.extract_curl_path(self.url)

        self.update_title.emit("正在下载get-pip.py...")
        put = tool.run_command(self.url) # 下载get-pip.py
        # 如果返回值不为1 则返回报错
        if put != 1:
            self.error.emit(f"发生错误 {put}")
            self.interrupt_marker = False # 中断

        self.update_title.emit("正在安装pip...")
        put2 = tool.run_command(f'{self.file_path_pth}/python.exe "{pip_path}"') # 安装pip
        # 如果返回值不为1 则返回报错
        if put2 != 1:
            self.error.emit(f"发生错误 {put2}")
            self.interrupt_marker = False # 中断

    def AutoGetPIPInstallCMD(self):
        """自动获取并安装pip"""
        pip_path = tool.extract_curl_path(self.url)

        self.update_title.emit("执行自动化命令...")
        put = tool.run_command(f'{self.url} && {self.file_path_pth}/python "{pip_path}"',True) # 组合命令
        # 如果返回值不为1 则返回报错
        if put != 1:
            self.error.emit(f"发生错误 {put}")
            self.interrupt_marker = False # 中断

    def AutoGetPIPInstallOpenCMD(self):
        """自动获取并安装pip保持CMD打开"""
        pip_path = tool.extract_curl_path(self.url)

        self.update_title.emit("等待CMD关闭...")
        put = tool.run_command(f'{self.url} && {self.file_path_pth}/python "{pip_path}"',True,"/k") # 组合命令
        # 如果返回值不为1 则返回报错
        if put != 1:
            self.error.emit(f"发生错误 {put}")
            self.interrupt_marker = False # 中断

    def GetPIP(self,visible=False):
        """获取pip"""
        self.update_title.emit("正在下载get-pip.py...")
        put = tool.run_command(self.url,visible) # 下载get-pip.py
        # 如果返回值不为1 则返回报错
        if put != 1:
            self.error.emit(f"发生错误 {put}")
            self.interrupt_marker = False # 中断

    def GetPIPOpen(self):
        """获取pip"""
        self.update_title.emit("等待CMD关闭...")
        put = tool.run_command(self.url,True,"/k") # 下载get-pip.py
        # 如果返回值不为1 则返回报错
        if put != 1:
            self.error.emit(f"发生错误 {put}")
            self.interrupt_marker = False # 中断

    def InstallPIP(self,visible=False):
        """安装pip"""
        self.update_title.emit("正在安装pip...")
        put2 = tool.run_command(f'{self.file_path_pth}/python.exe "{self.pip}"',visible) # 安装pip
        # 如果返回值不为1 则返回报错
        if put2 != 1:
            self.error.emit(f"发生错误 {put2}")
            self.interrupt_marker = False # 中断

    def InstallPIPOpen(self):
        """安装pip"""
        self.update_title.emit("等待CMD关闭...")
        put2 = tool.run_command(f'{self.file_path_pth}/python.exe "{self.pip}"',True,"/k") # 安装pip
        # 如果返回值不为1 则返回报错
        if put2 != 1:
            self.error.emit(f"发生错误 {put2}")
            self.interrupt_marker = False # 中断

class VenvBatchProcessing(QThread):
    """
    Venv批处理
    """
    finished = pyqtSignal()
    error = pyqtSignal(str)
    update_title = pyqtSignal(str)

    def __init__(self, comm, cmd1, cmd2,config_cmd=None,activate_path=""):
        super().__init__()
        self.comm = comm
        self.cmd1 = cmd1
        self.cmd2 = cmd2
        self.config = config_cmd
        self.activate_path = activate_path
        # 中断标记
        self.interrupt_marker = True

    def run(self):
        try:
            # 第一个判断条件多的
            # 打开cmd并保持打开
            if self.cmd1 and self.cmd2:
                self.ExecuteCommandVenvOpenCMD()
            elif self.cmd1:
                self.ExecuteCommandVenvCMD()
            else:
                self.ExecuteCommandVenv()

            # 正常完成
            if self.interrupt_marker:
                self.finished.emit()

        except Exception as e:
            self.error.emit(f"发生错误 {e}")

    def ExecuteCommandVenv(self):
        """安装Venv"""

        self.update_title.emit("正在安装Venv...")
        put = tool.run_command(self.comm)  # 下载get-pip.py
        # 如果返回值不为1 则返回报错 并且有报错文本
        if put != 1 and put != "":
            self.error.emit(f"发生错误 {put}")
            self.interrupt_marker = False # 中断

    def ExecuteCommandVenvCMD(self):
        """执行Venv命令 打开cmd"""

        self.update_title.emit("安装Venv中...")
        put = tool.run_command(self.comm) # 执行命令
        # 如果返回值不为1 则返回报错
        if put != 1 and put != "":
            self.error.emit(f"发生错误 {put}")
            self.interrupt_marker = False # 中断

        self.update_title.emit("配置Venv中...")
        put = tool.run_command_temp_cmd(self.config,self.activate_path,True) # 执行配置
        if put != 1 and put != "":
            self.error.emit(f"发生错误 {put}")
            self.interrupt_marker = False # 中断

    def ExecuteCommandVenvOpenCMD(self):
        """执行Venv命令 保持CMD打开"""

        self.update_title.emit("安装Venv中...")
        put = tool.run_command(self.comm) # 执行命令
        # 如果返回值不为1 则返回报错
        if put != 1 and put != "":
            self.error.emit(f"发生错误 {put}")
            self.interrupt_marker = False # 中断

        self.update_title.emit("等待CMD中...")
        put = tool.run_command_temp_cmd(self.config,self.activate_path,True,"/k") # 执行配置
        if put != 1 and put != "":
            self.error.emit(f"发生错误 {put}")
            self.interrupt_marker = False # 中断

class DeleteFolder(QThread):
    """
    删除文件夹
    """
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
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

class GetPythonVersions(QThread):
    """
    获取python版本
    """
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            self.finished.emit(tool.get_python_all_versions())
        except Exception as e:
            self.error.emit(f"获取版本超时")
            print(e)

class GetPythonFile(QThread):
    """
    获取python文件
    """
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self,v):
        super().__init__()
        self.v = v

    def run(self):
        try:
            self.finished.emit(tool.get_python_versions_all_file(self.v))
        except Exception as e:
            self.error.emit(f"获取文件超时")
            print(e)

class DownloadThread(QThread):
    """
    Signals:
        progress(int)        -> 下载百分比 (0~100)
        speed(str)           -> 当前速度，如 "2.34 MB/s"
        finished(str)        -> 下载完成，返回文件路径
        error(str)           -> 错误信息
    """

    progress = pyqtSignal(int)
    speed = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url: str, filename: str, save_dir: str):
        super().__init__()
        self.url = url
        self.filename = filename
        self.save_dir = save_dir
        self._is_running = True

    def run(self):
        try:
            save_path = Path(self.save_dir) / self.filename
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with requests.get(self.url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))

                downloaded = 0
                start_time = self.msecsElapsed() / 1000

                with open(save_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if not self._is_running:
                            break
                        if not chunk:
                            continue

                        f.write(chunk)
                        downloaded += len(chunk)

                        now = self.msecsElapsed() / 1000
                        if now - start_time > 0:
                            sp = downloaded / (now - start_time)
                            if sp > 1024 * 1024:
                                sp_str = f"{sp / 1024 / 1024:.2f} MB/s"
                            else:
                                sp_str = f"{sp / 1024:.2f} KB/s"
                            self.speed.emit(sp_str)

                        if total:
                            self.progress.emit(int(downloaded / total * 100))

                if self._is_running:
                    self.finished.emit(str(save_path))
                else:
                    try:
                        save_path.unlink(missing_ok=True)
                    except:
                        pass

        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self._is_running = False

    def msecsElapsed(self):
        import time
        return int(time.time() * 1000)

class DownloadManager(QObject):
    """
    多任务下载管理器（内部含 Worker 线程）

    对外信号:
        progress(int, int)   -> task_id, percent
        speed(int, str)      -> task_id, speed
        finished(int, str)    -> task_id, path
        error(int, str)      -> task_id, msg
        task_added(int)       -> task_id (新任务加入通知)
    """
    progress = pyqtSignal(int, int)
    speed = pyqtSignal(int, str)
    finished = pyqtSignal(int, str)
    error = pyqtSignal(int, str)
    task_added = pyqtSignal(int)

    # ==================== 内部 Worker ====================

    class _Worker(QThread):
        """（私有）单文件下载线程"""
        _progress = pyqtSignal(int, int)
        _speed = pyqtSignal(int, str)
        _finished = pyqtSignal(int, str)
        _error = pyqtSignal(int, str)

        def __init__(self, task_id: int, url: str, filename: str, save_dir: str):
            super().__init__()
            self.task_id = task_id
            self.url = url
            self.filename = filename
            self.save_dir = save_dir
            self._running = True

        def run(self):
            try:
                save_path = Path(self.save_dir) / self.filename
                save_path.parent.mkdir(parents=True, exist_ok=True)

                with requests.get(self.url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    total = int(r.headers.get("content-length", 0))
                    downloaded = 0
                    start = time.time()

                    with open(save_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if not self._running:
                                break
                            if not chunk:
                                continue

                            f.write(chunk)
                            downloaded += len(chunk)

                            now = time.time()
                            if now - start >= 1:
                                sp = downloaded / (now - start)
                                sp_str = (
                                    f"{sp / 1024 / 1024:.2f} MB/s"
                                    if sp > 1 << 20
                                    else f"{sp / 1024:.2f} KB/s"
                                )
                                self._speed.emit(self.task_id, sp_str)
                                start = now

                            if total:
                                self._progress.emit(
                                    self.task_id, int(downloaded / total * 100)
                                )

                if self._running:
                    self._finished.emit(self.task_id, str(save_path))
                else:
                    save_path.unlink(missing_ok=True)

            except Exception as e:
                self._error.emit(self.task_id, str(e))

        def stop(self):
            self._running = False

    # ==================== Manager 本体 ====================

    def __init__(self, save_dir: str = "./downloads", max_threads: int = 3):
        super().__init__()
        self.save_dir = save_dir
        self.max_threads = max_threads

        self._queue: List[Tuple[int, str, str]] = []
        self._workers: Dict[int, "_Worker"] = {}
        self._running = 0
        self._task_id = 0

    # ----------------- 对外 API -----------------

    def add(self, url: str, filename: str) -> int:
        """追加单个下载任务，返回 task_id"""
        self._task_id += 1
        self._queue.append((self._task_id, url, filename))
        self.task_added.emit(self._task_id)
        self._try_start()
        return self._task_id

    def add_batch(self, file_list: List[Tuple[str, str]]) -> List[int]:
        """批量追加 [(url, filename), ...]"""
        return [self.add(url, name) for url, name in file_list]

    def pause(self, task_id: int):
        """暂停（取消）指定任务"""
        w = self._workers.get(task_id)
        if w:
            w.stop()

    def cancel(self, task_id: int):
        self.pause(task_id)

    def remove(self, task_id: int):
        """从队列中移除未开始的任务"""
        self._queue = [t for t in self._queue if t[0] != task_id]

    @property
    def active_count(self) -> int:
        return self._running

    @property
    def queue_count(self) -> int:
        return len(self._queue)

    @property
    def total_count(self) -> int:
        return self._task_id

    # ----------------- 内部逻辑 -----------------

    def _try_start(self):
        while self._running < self.max_threads and self._queue:
            tid, url, name = self._queue.pop(0)
            self._start_worker(tid, url, name)

    def _start_worker(self, tid: int, url: str, filename: str):
        worker = self._Worker(tid, url, filename, self.save_dir)

        # 转发
        worker._progress.connect(self.progress, Qt.QueuedConnection)
        worker._speed.connect(self.speed, Qt.QueuedConnection)
        worker._finished.connect(self._on_finished, Qt.QueuedConnection)
        worker._error.connect(self.error, Qt.QueuedConnection)

        self._workers[tid] = worker
        self._running += 1
        worker.start()

    def _on_finished(self, tid: int, path: str):
        # 无论怎样都收干净
        w = self._workers.pop(tid, None)
        if w:
            try:
                w.stop()
                w.wait(1000)
                w.deleteLater()
            except Exception:
                pass

        self._running = max(0, self._running - 1)

        # ✅ 一定先发信号（别在前面炸）
        self.finished.emit(tid, path)

        # ✅ 再调度下一个
        self._try_start()