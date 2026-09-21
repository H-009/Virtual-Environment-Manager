import webbrowser

from PyQt5.QtWidgets import QHBoxLayout, QHeaderView, QTableWidgetItem
from qtpy.QtCore import QTimer, Signal, Qt
from qtpy.QtGui import QColor
from qfluentwidgets import MessageBox, MaskDialogBase, MessageBoxBase, SubtitleLabel, BodyLabel, StrongBodyLabel, \
    TextBrowser, TableWidget, HyperlinkButton
from qfluentwidgets.components.dialog_box.dialog import Ui_MessageBox

# 消息框



# 危险倒计时消息框
class DangerCountdownMessageBox(MessageBox):
    def __init__(self, title, content, parent=None, countdown_seconds=5,text="确认"):
        super().__init__(title, content, parent)
        self.countdown_seconds = countdown_seconds
        self.remaining = countdown_seconds
        self.text = text

        # 初始禁用确认按钮
        self.yesButton.setEnabled(False)
        # 初始显示计时器
        self.yesButton.setText(f'{self.text}({countdown_seconds}s)')
        self.cancelButton.setText("取消")
        # 设置独立QSS
        self.yesButton.setStyleSheet("""
            QPushButton {
                background-color: #d13438; /* 正常状态：Fluent 红色 */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c42b2f; /* 悬停状态：稍深红 */
            }
            QPushButton:pressed {
                background-color: #a82428; /* 点击状态：更深红 */
            }
            QPushButton:disabled {
                background-color: #8a1c20; /* 禁用状态：暗红/黑红 */
                color: #cccccc;            /* 文字颜色变灰，体现不可用 */
            }
        """)
        # 启动倒计时定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # 每秒触发一次

    def update_countdown(self):
        self.remaining -= 1
        if self.remaining <= 0:
            # 倒计时结束，停止计时并启用按钮
            self.timer.stop()
            self.yesButton.setEnabled(True)
            self.yesButton.setText(self.text)
        else:
            # 更新按钮文本显示剩余时间
            self.yesButton.setText(f'{self.text}({self.remaining}s)')

# 倒计时消息框
class CountdownMessageBox(MessageBox):
    def __init__(self, title, content, parent=None, countdown_seconds=5,text="确认"):
        super().__init__(title, content, parent)
        self.countdown_seconds = countdown_seconds
        self.remaining = countdown_seconds
        self.text = text

        self.cancelButton.hide()

        # 初始禁用确认按钮
        self.yesButton.setEnabled(False)
        # 初始显示计时器
        self.yesButton.setText(f'{self.text}({countdown_seconds}s)')
        self.cancelButton.setText("取消")
        # 启动倒计时定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)  # 每秒触发一次

    def update_countdown(self):
        self.remaining -= 1
        if self.remaining <= 0:
            # 倒计时结束，停止计时并启用按钮
            self.timer.stop()
            self.yesButton.setEnabled(True)
            self.yesButton.setText(self.text)
        else:
            # 更新按钮文本显示剩余时间
            self.yesButton.setText(f'{self.text}({self.remaining}s)')

# 提示消息框
class TipMessageBox(MaskDialogBase, Ui_MessageBox):
    yesSignal = Signal()
    cancelSignal = Signal()

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent=parent)
        self._setUpUi(title, content, self.widget)

        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 50))
        self.setMaskColor(QColor(0, 0, 0, 76))
        self._hBoxLayout.removeWidget(self.widget)
        self._hBoxLayout.addWidget(self.widget, 1, Qt.AlignmentFlag.AlignCenter)

        self.buttonGroup.setMinimumWidth(280)
        self.widget.setFixedSize(
            max(self.contentLabel.width(), self.titleLabel.width()) + 48,
            self.contentLabel.y() + self.contentLabel.height() + 105
        )

        self.yesButton.setText("明白👌")
        self.cancelButton.hide()

# 发布消息框
class ReleaseMessageBox(MessageBoxBase):
    def __init__(self, release_json: dict, parent=None):
        super().__init__(parent)
        self.release = release_json

        # -------- 标题 --------
        self.titleLayout = QHBoxLayout()

        self.titleLabel = SubtitleLabel(f"新版本发布 {self.release['version']}", self)
        self.titleLayout.addWidget(self.titleLabel)
        self.viewLayout.addLayout(self.titleLayout)

        if self.release.get("is_prerelease"):
            pre_tag = BodyLabel("预发布")
            pre_tag.setFixedWidth(80)
            pre_tag.setAlignment(Qt.AlignCenter)
            pre_tag.setStyleSheet(
                "color: white;"
                "background-color: #D19A3A;"
                "border-radius: 4px;"
                "padding: 2px 8px;"
                "font-size: 12px;"
            )
            self.titleLayout.addWidget(pre_tag)
        else:
            pre_tag = BodyLabel("正式版")
            pre_tag.setFixedWidth(80)
            pre_tag.setAlignment(Qt.AlignCenter)
            pre_tag.setStyleSheet(
                "color: white;"
                "background-color: #0E8A4A;"
                "border-radius: 4px;"
                "padding: 2px 8px;"
                "font-size: 12px;"
            )
            self.titleLayout.addWidget(pre_tag)


        # -------- 发布时间 --------
        pub_time = self.release["publish_time"].replace("T", " ").replace("Z", "")
        self.viewLayout.addWidget(BodyLabel(f"发布时间：{pub_time}"))

        # -------- 更新日志 --------
        self.viewLayout.addWidget(StrongBodyLabel("更新日志"))
        self.noteBrowser = TextBrowser(self)
        self.noteBrowser.setMarkdown(self.release["release_note"])
        self.noteBrowser.setOpenExternalLinks(True)
        self.viewLayout.addWidget(self.noteBrowser)

        # -------- 下载资源表 --------
        self.viewLayout.addWidget(StrongBodyLabel("下载资源"))
        assets = self.release.get("download_assets", [])

        self.table = TableWidget(self)
        self.table.setRowCount(len(assets))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["文件名", "SHA256","大小"])
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(TableWidget.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # 自己平分剩余空间
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed) # 固定第二列宽度
        self.table.setColumnWidth(1, 200)

        for row, a in enumerate(assets):
            # 文件名 → 超链接
            link = HyperlinkButton(
                url=a["download_url"],
                text=a["filename"],
                parent=self.table
            )
            link.setToolTip(a["download_url"])
            self.table.setCellWidget(row, 0, link)

            # SHA256
            self.table.setItem(row, 1, QTableWidgetItem(a["sha256"]))

            # 大小
            self.table.setItem(
                row, 2,
                QTableWidgetItem(f"{a['size'] / 1024 / 1024:.2f} MB")
            )

        self.table.setFixedHeight(120)
        self.viewLayout.addWidget(self.table)

        # -------- 底部按钮 --------
        self.yesButton.setText("查看发布页")
        self.yesButton.clicked.connect(
            lambda: webbrowser.open(self.release["detail_page_url"])
        )
        self.cancelButton.setText("关闭")

        self.widget.setMinimumWidth(720)