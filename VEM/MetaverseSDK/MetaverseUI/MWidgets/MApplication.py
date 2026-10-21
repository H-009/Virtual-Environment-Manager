from qtpy.QtCore import Signal
from qtpy.QtNetwork import QLocalServer, QLocalSocket
from qtpy.QtWidgets import QApplication


# 单应用程序
class SingleApplication(QApplication):

    # 当第二个实例启动时触发
    second_instance_started = Signal()

    def __init__(self, app_id: str, argv):
        """
        :param app_id: 唯一字符串标识
        :param argv: sys.argv
        """
        super().__init__(argv)

        self.app_id = app_id
        self.server_name = f"{app_id}_LocalServer"
        self.server = None
        self.is_running = False
        self.main_window = None

        self._try_run_server()

    def _try_run_server(self):
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)

        if socket.waitForConnected(500):
            # 已有实例在运行
            self.is_running = True
            socket.disconnectFromServer()
            return

        # 当前是第一个实例
        self.server = QLocalServer()
        self.server.newConnection.connect(self._on_new_connection)

        # 防止上次异常退出残留
        QLocalServer.removeServer(self.server_name)
        self.server.listen(self.server_name)

    def _on_new_connection(self):
        """
        第二个实例尝试连接
        """
        while self.server.hasPendingConnections():
            sock = self.server.nextPendingConnection()
            sock.deleteLater()

        self.second_instance_started.emit()

        # 激活主窗口
        if self.main_window:
            self.main_window.showNormal()
            self.main_window.raise_()
            self.main_window.activateWindow()

    def isAlreadyRunning(self):
        return self.is_running