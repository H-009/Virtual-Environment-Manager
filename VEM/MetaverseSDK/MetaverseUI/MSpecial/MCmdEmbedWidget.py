import time
import subprocess
import win32gui
import win32process
import win32con
import win32api
import psutil

from qtpy.QtWidgets import QWidget
from qtpy.QtCore import QThread, Signal, QTimer


# ===================================================
# CMD 窗口持续查找线程
# ===================================================
class CmdWindowFinder(QThread):
    found = Signal(int)  # 每次找到都发
    finished_once = Signal()  # 首次成功结束

    def __init__(self, pid, parent=None):
        super().__init__(parent)
        self.pid = pid
        self._running = True
        self._embedded = False

    def run(self):
        while self._running:
            hwnd = CmdEmbedWidget.find_console_window(self.pid)
            if hwnd and not self._embedded:
                self._embedded = True
                self.found.emit(hwnd)
                self.finished_once.emit()
                # 如果你只嵌一次就停，这里 return
                return

            time.sleep(0.01)

    def stop(self):
        self._running = False


# ===================================================
# CMD 监控线程（检测 CMD 是否存活）
# ===================================================
class CmdMonitorThread(QThread):
    running_changed = Signal(bool)

    def __init__(self, proc, parent=None, frequency=0.5):
        super().__init__(parent)
        self.proc = proc
        self.frequency = frequency
        self._alive = True

    def run(self):
        while self._alive:
            alive = False
            if self.proc:
                try:
                    p = psutil.Process(self.proc.pid)
                    alive = p.is_running() and p.status() != psutil.STATUS_ZOMBIE
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    alive = False

            if not alive:
                # ✅ 只发射一次 False
                self.running_changed.emit(False)
                self._alive = False
                break

            self.running_changed.emit(True)
            time.sleep(self.frequency)

    def safe_stop(self):
        self._alive = False
        self.quit()
        self.wait()

    def stop(self):
        self._alive = False
        self.quit()
        self.wait()


# ===================================================
# CmdEmbed（嵌入 + 自动输入）
# ===================================================
class CmdEmbedWidget(QWidget):
    def __init__(self, parent=None, workdir="C:\\", mode="finder",delay=500,frequency=0.5,physical_pixels=False):
        super().__init__(parent)
        self.mode = mode
        self.time = delay
        self.frequency = frequency
        self.workdir = workdir

        self.proc = None
        self.cmd_hwnd = None
        self.finder_thread = None
        self.monitor_thread = None
        self._cmd_full_screen = False
        self.physical_pixels = physical_pixels

        self.start_cmd()

    def start_cmd(self):
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = win32con.SW_SHOWMINIMIZED

        self.proc = subprocess.Popen(
            "cmd.exe",
            cwd=self.workdir,
            startupinfo=si,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        # ✅ 启动存活监控线程
        self.monitor_thread = CmdMonitorThread(self.proc,frequency=self.frequency)
        self.monitor_thread.start()

        # ✅ 选择嵌入方式
        if self.mode == "finder":
            self.start_finder()
        elif self.mode == "timer":
            QTimer.singleShot(self.time, self.embed_cmd)
        else:
            raise ValueError(f"未知 mode: {self.mode}")

    # ===================================================
    # 方式一：持续捕捉
    # ===================================================
    def start_finder(self):
        self.finder_thread = CmdWindowFinder(self.proc.pid)
        self.finder_thread.found.connect(self.on_cmd_found)
        self.finder_thread.finished_once.connect(self.finder_thread.stop)
        self.finder_thread.start()

    # ===================================================
    # 方式二：延迟嵌入
    # ===================================================
    def embed_cmd(self):
        self.cmd_hwnd = self.find_console_window(self.proc.pid)
        if not self.cmd_hwnd:
            QTimer.singleShot(self.time, self.embed_cmd)
            return

        self.finalize_embed()

    # ===================================================
    # 公共：真正嵌入
    # ===================================================
    def on_cmd_found(self, hwnd: int):
        self.cmd_hwnd = hwnd
        self.finalize_embed()
        self.finder_thread.stop()

    def finalize_embed(self):
        hwnd = self.cmd_hwnd
        # 去标题栏 去边框 防止抢焦点 防F11最大化最小化

        # ---------- GWL_STYLE ----------
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style &= ~(
            win32con.WS_CAPTION |
            win32con.WS_THICKFRAME |
            win32con.WS_MAXIMIZEBOX |
            win32con.WS_MINIMIZEBOX |
            win32con.WS_SYSMENU
        )
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

        # ---------- GWL_EXSTYLE ----------
        # 去焦点
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        ex_style |= (
            win32con.WS_EX_TOOLWINDOW
        )
        ex_style &= ~win32con.WS_EX_WINDOWEDGE
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

        win32gui.SetParent(hwnd, int(self.winId()))
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

        if not self.physical_pixels:
            # 使用逻辑像素
            self.resize_cmd()
        else:
            # 使用物理像素
            self.resize_cmd_physical_pixels()

    # ================= 全屏 =================
    def cmd_full_screen_on(self):
        if not self.cmd_hwnd or self._cmd_full_screen:
            return

        hwnd = self.cmd_hwnd

        self._cmd_normal_style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        self._cmd_normal_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        self._cmd_normal_rect = win32gui.GetWindowRect(hwnd)
        self._cmd_normal_parent = win32gui.GetParent(hwnd)

        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        win32gui.SetParent(hwnd, None)

        style = win32con.WS_POPUP | win32con.WS_VISIBLE
        ex_style = win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOOLWINDOW | win32con.WS_EX_TOPMOST
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
        )

        win32gui.InvalidateRect(hwnd, None, True)
        win32gui.UpdateWindow(hwnd)

        self._cmd_full_screen = True

    def resize_cmd(self):
        if self.cmd_hwnd:
            win32gui.MoveWindow(
                self.cmd_hwnd,
                0, 0,
                self.width(),
                self.height(),
                True
            )

    def resize_cmd_physical_pixels(self):
        if not self.cmd_hwnd:
            return

        from ctypes import windll
        hwnd = int(self.winId())
        dpi = windll.user32.GetDpiForWindow(hwnd)

        scale = dpi / 96.0

        w = int(self.width() * scale)
        h = int(self.height() * scale)

        win32gui.MoveWindow(
            self.cmd_hwnd,
            0, 0,
            w, h,
            True
        )

    def resizeEvent(self, event):
        if not self.physical_pixels:
            self.resize_cmd()
        else:
            # 使用物理像素
            self.resize_cmd_physical_pixels()

    def send_command(self, text: str):
        """虚拟按键模拟自动输入"""
        if not self.cmd_hwnd:
            return

        VK_SHIFT = win32con.VK_SHIFT

        for ch in text:
            # VkKeyScan 返回值：
            # 低字节 = virtual key
            # 高字节 bit0 = Shift
            vk_shift = win32api.VkKeyScan(ch)
            vk = vk_shift & 0xFF
            shift = (vk_shift >> 8) & 0xFF

            scan = win32api.MapVirtualKey(vk, 0)

            # Shift DOWN
            if shift & 1:
                win32gui.PostMessage(
                    self.cmd_hwnd,
                    win32con.WM_KEYDOWN,
                    VK_SHIFT,
                    (win32api.MapVirtualKey(VK_SHIFT, 0) << 16) | 1
                )

            # Key DOWN
            win32gui.PostMessage(
                self.cmd_hwnd,
                win32con.WM_KEYDOWN,
                vk,
                (scan << 16) | 1
            )

            # Key UP
            win32gui.PostMessage(
                self.cmd_hwnd,
                win32con.WM_KEYUP,
                vk,
                (scan << 16) | 0xC0000001
            )

            # Shift UP
            if shift & 1:
                win32gui.PostMessage(
                    self.cmd_hwnd,
                    win32con.WM_KEYUP,
                    VK_SHIFT,
                    (win32api.MapVirtualKey(VK_SHIFT, 0) << 16) | 0xC0000001
                )

        # Enter
        win32gui.PostMessage(
            self.cmd_hwnd,
            win32con.WM_KEYDOWN,
            win32con.VK_RETURN,
            0
        )
        win32gui.PostMessage(
            self.cmd_hwnd,
            win32con.WM_KEYUP,
            win32con.VK_RETURN,
            0xC0000001
        )

    def refresh(self):
        """
        手动刷新 CMD 显示
        """
        rect = win32gui.GetClientRect(self.cmd_hwnd)
        win32gui.InvalidateRect(self.cmd_hwnd, rect, True)
        win32gui.UpdateWindow(self.cmd_hwnd)

    def _force_win32_repaint(self):
        rect = win32gui.GetClientRect(self.cmd_hwnd)
        win32gui.InvalidateRect(self.cmd_hwnd, rect, True)
        win32gui.UpdateWindow(self.cmd_hwnd)

    @staticmethod
    def find_console_window(pid):
        result = []

        def callback(hwnd, _):
            if win32gui.GetClassName(hwnd) == "ConsoleWindowClass":
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == pid:
                    result.append(hwnd)

        win32gui.EnumWindows(callback, None)
        return result[0] if result else None

    def safe_destroy_cmd(self):
        win32gui.SendMessage(
            self.cmd_hwnd,
            win32con.WM_SYSCOMMAND,
            win32con.SC_CLOSE,
            0
        )