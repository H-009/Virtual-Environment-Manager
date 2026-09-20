import os
from PIL import Image
from PyQt5.QtCore import pyqtSignal, Qt, QUrl, QTimer
from PyQt5.QtGui import QKeySequence, QPixmap, QImage, QPainter
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QShortcut, QFileDialog, QMessageBox, QApplication


class MediaEngineLite(QWidget):
    """精简版媒体显示部件，仅显示媒体，无控制界面"""

    # 定义信号
    mediaLoaded = pyqtSignal(str)  # 媒体加载完成
    mediaCleared = pyqtSignal()  # 媒体被清除
    playStateChanged = pyqtSignal(bool)  # 播放状态变化
    errorOccurred = pyqtSignal(str)  # 错误信号

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化变量
        self.current_media_path = ""
        self.is_playing = False
        self.is_muted = False
        self.volume = 50
        self.is_video = False
        self.is_image = False
        self.original_pixmap = None

        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
            QLabel {
                background-color: #000000;
                color: #888888;
                font-size: 14px;
            }
        """)

        # 初始化UI
        self.initUI()

        # 初始化媒体播放器
        self.initMediaPlayer()

        # 初始化快捷键
        self.initShortcuts()

    def initUI(self):
        """初始化用户界面"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 图片显示标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 视频显示部件
        self.video_widget = QVideoWidget()
        self.video_widget.hide()  # 默认隐藏

        # 添加到布局
        layout.addWidget(self.video_widget)

        # 设置窗口属性
        self.setAcceptDrops(True)

    def initMediaPlayer(self):
        """初始化媒体播放器"""
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setVolume(self.volume)

        # 连接信号
        self.media_player.stateChanged.connect(self.onPlayerStateChanged)
        self.media_player.positionChanged.connect(self.onPositionChanged)
        self.media_player.durationChanged.connect(self.onDurationChanged)
        self.media_player.error.connect(self.onPlayerError)

    def initShortcuts(self):
        """初始化快捷键"""
        # 打开文件
        shortcut_open = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut_open.activated.connect(self.openFile)

        # 播放/暂停
        shortcut_space = QShortcut(QKeySequence("Space"), self)
        shortcut_space.activated.connect(self.togglePlayPause)

        # 停止
        shortcut_s = QShortcut(QKeySequence("S"), self)
        shortcut_s.activated.connect(self.stop)

        # 静音
        shortcut_m = QShortcut(QKeySequence("M"), self)
        shortcut_m.activated.connect(self.toggleMute)

        # 音量控制
        shortcut_up = QShortcut(QKeySequence("Up"), self)
        shortcut_up.activated.connect(self.volumeUp)

        shortcut_down = QShortcut(QKeySequence("Down"), self)
        shortcut_down.activated.connect(self.volumeDown)

        # 播放控制
        shortcut_left = QShortcut(QKeySequence("Left"), self)
        shortcut_left.activated.connect(self.seekBackward)

        shortcut_right = QShortcut(QKeySequence("Right"), self)
        shortcut_right.activated.connect(self.seekForward)

        # 全屏
        shortcut_f11 = QShortcut(QKeySequence("F11"), self)
        shortcut_f11.activated.connect(self.toggleFullscreen)

        shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        shortcut_esc.activated.connect(self.exitFullscreen)

        # 清空
        shortcut_w = QShortcut(QKeySequence("Ctrl+W"), self)
        shortcut_w.activated.connect(self.clear)

        # 退出
        shortcut_q = QShortcut(QKeySequence("Ctrl+Q"), self)
        shortcut_q.activated.connect(self.close)

        # 显示信息
        shortcut_i = QShortcut(QKeySequence("Ctrl+I"), self)
        shortcut_i.activated.connect(self.showMediaInfo)

        # 重新加载
        shortcut_r = QShortcut(QKeySequence("F5"), self)
        shortcut_r.activated.connect(self.reloadMedia)

    # ==================== 核心媒体功能 ====================

    def loadMedia(self, file_path):
        """加载媒体文件"""
        if not os.path.exists(file_path):
            self.errorOccurred.emit(f"文件不存在: {file_path}")
            return False

        self.current_media_path = file_path

        # 判断文件类型
        file_ext = os.path.splitext(file_path)[1].lower()
        image_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']

        if file_ext in image_exts:
            return self.loadImage(file_path)
        elif file_ext in video_exts:
            return self.loadVideo(file_path)
        else:
            self.errorOccurred.emit(f"不支持的文件格式: {file_ext}")
            return False

    def loadImage(self, file_path):
        """加载图片"""
        try:
            # 重置视频
            self.resetVideo()

            # 加载图片
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                # 尝试使用PIL加载
                pil_image = Image.open(file_path)
                if pil_image.mode != "RGBA":
                    pil_image = pil_image.convert("RGBA")
                data = pil_image.tobytes("raw", "RGBA")
                qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimage)

            if pixmap.isNull():
                raise Exception("无法加载图片")

            self.original_pixmap = pixmap
            self.is_image = True
            self.is_video = False

            # 显示图片
            self.showImage()
            self.mediaLoaded.emit(file_path)
            return True

        except Exception as e:
            self.errorOccurred.emit(f"加载图片失败: {str(e)}")
            return False

    def loadVideo(self, file_path):
        """加载视频"""
        try:
            # 重置图片
            self.resetImage()

            # 设置媒体
            url = QUrl.fromLocalFile(file_path)
            content = QMediaContent(url)
            self.media_player.setMedia(content)

            self.is_video = True
            self.is_image = False

            # 显示视频部件
            self.video_widget.show()
            self.image_label.hide()

            self.mediaLoaded.emit(file_path)
            return True

        except Exception as e:
            self.errorOccurred.emit(f"加载视频失败: {str(e)}")
            return False

    def showImage(self):
        """显示图片（自适应）"""
        if not self.original_pixmap or self.original_pixmap.isNull():
            return

        # 获取显示区域大小
        label_size = self.image_label.size()
        if label_size.width() <= 0 or label_size.height() <= 0:
            return

        # 计算缩放后的图片大小
        pixmap_size = self.original_pixmap.size()
        pixmap_size.scale(label_size, Qt.KeepAspectRatio)

        # 缩放图片
        scaled_pixmap = self.original_pixmap.scaled(
            pixmap_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # 显示图片
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.show()
        self.video_widget.hide()

    def reloadMedia(self):
        """重新加载当前媒体"""
        if self.current_media_path:
            self.loadMedia(self.current_media_path)

    # ==================== 控制函数 ====================

    def play(self):
        """播放"""
        if self.is_video:
            self.media_player.play()
            self.is_playing = True
            self.playStateChanged.emit(True)

    def pause(self):
        """暂停"""
        if self.is_video:
            self.media_player.pause()
            self.is_playing = False
            self.playStateChanged.emit(False)

    def stop(self):
        """停止"""
        if self.is_video:
            self.media_player.stop()
            self.is_playing = False
            self.playStateChanged.emit(False)

    def togglePlayPause(self):
        """切换播放/暂停"""
        if not self.is_video:
            return

        if self.is_playing:
            self.pause()
        else:
            self.play()

    def setVolume(self, volume):
        """设置音量"""
        self.volume = max(0, min(100, volume))
        if self.is_video:
            self.media_player.setVolume(self.volume)

    def volumeUp(self):
        """音量增加"""
        self.setVolume(self.volume + 5)

    def volumeDown(self):
        """音量减少"""
        self.setVolume(self.volume - 5)

    def toggleMute(self):
        """切换静音"""
        if self.is_video:
            self.is_muted = not self.is_muted
            self.media_player.setMuted(self.is_muted)

    def setPosition(self, position):
        """设置播放位置（毫秒）"""
        if self.is_video:
            self.media_player.setPosition(position)

    def seekForward(self, seconds=10):
        """快进"""
        if self.is_video and self.is_playing:
            current_pos = self.media_player.position()
            duration = self.media_player.duration()
            new_pos = min(current_pos + seconds * 1000, duration)
            self.media_player.setPosition(new_pos)

    def seekBackward(self, seconds=10):
        """快退"""
        if self.is_video and self.is_playing:
            current_pos = self.media_player.position()
            new_pos = max(current_pos - seconds * 1000, 0)
            self.media_player.setPosition(new_pos)

    def toggleFullscreen(self):
        """切换全屏"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def exitFullscreen(self):
        """退出全屏"""
        if self.isFullScreen():
            self.showNormal()

    def clear(self):
        """清空显示"""
        self.resetImage()
        self.resetVideo()
        self.current_media_path = ""
        self.image_label.show()
        self.mediaCleared.emit()

    def openFile(self):
        """打开文件对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择媒体文件",
            "",
            "媒体文件 (*.jpg *.jpeg *.png *.bmp *.gif *.mp4 *.avi *.mov *.mkv *.flv *.wmv *.webm);;"
            "所有文件 (*.*)"
        )

        if file_path:
            self.loadMedia(file_path)

    def showMediaInfo(self):
        """显示媒体信息"""
        if not self.current_media_path:
            return

        info = f"""
        当前文件: {os.path.basename(self.current_media_path)}
        文件路径: {self.current_media_path}
        媒体类型: {'视频' if self.is_video else '图片'}
        播放状态: {'播放中' if self.is_playing else '停止'}
        音量: {self.volume}%
        静音: {'是' if self.is_muted else '否'}
        """

        if self.is_video and self.media_player.duration() > 0:
            current = self.media_player.position() // 1000
            total = self.media_player.duration() // 1000
            info += f"\n播放进度: {current // 60:02d}:{current % 60:02d} / {total // 60:02d}:{total % 60:02d}"

        QMessageBox.information(self, "媒体信息", info.strip())

    # ==================== 内部辅助函数 ====================

    def resetImage(self):
        """重置图片显示"""
        self.is_image = False
        self.original_pixmap = None
        self.image_label.clear()

    def resetVideo(self):
        """重置视频播放"""
        if self.is_playing:
            self.media_player.stop()
        self.media_player.setMedia(QMediaContent())
        self.video_widget.hide()
        self.image_label.show()
        self.is_video = False
        self.is_playing = False

    def formatTime(self, milliseconds):
        """格式化时间显示"""
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    # ==================== 事件处理 ====================

    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)

        # 重新显示图片（自适应）
        if self.is_image and self.original_pixmap:
            QTimer.singleShot(50, self.showImage)

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """拖放事件"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):
                self.loadMedia(file_path)

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == Qt.LeftButton:
            self.toggleFullscreen()

    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_Space:
            self.togglePlayPause()
        elif event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
        elif event.key() == Qt.Key_Up:
            self.volumeUp()
        elif event.key() == Qt.Key_Down:
            self.volumeDown()
        elif event.key() == Qt.Key_Left and self.is_video:
            self.seekBackward()
        elif event.key() == Qt.Key_Right and self.is_video:
            self.seekForward()
        elif event.key() == Qt.Key_M:
            self.toggleMute()
        elif event.key() == Qt.Key_S:
            self.stop()
        elif event.key() == Qt.Key_F5:
            self.reloadMedia()
        elif event.key() == Qt.Key_F11:
            self.toggleFullscreen()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        """右键菜单事件"""
        from PyQt5.QtWidgets import QMenu

        menu = QMenu(self)

        # 文件操作
        menu.addAction("打开文件 (Ctrl+O)", self.openFile)
        menu.addAction("重新加载 (F5)", self.reloadMedia)
        menu.addSeparator()

        # 播放控制
        if self.is_video:
            menu.addAction("播放/暂停 (空格键)", self.togglePlayPause)
            menu.addAction("停止 (S)", self.stop)
            menu.addSeparator()

        # 音量控制
        menu.addAction("增加音量 (↑)", self.volumeUp)
        menu.addAction("减少音量 (↓)", self.volumeDown)
        menu.addAction("静音切换 (M)", self.toggleMute)
        menu.addSeparator()

        # 播放控制
        if self.is_video and self.is_playing:
            menu.addAction("快退10秒 (←)", self.seekBackward)
            menu.addAction("快进10秒 (→)", self.seekForward)
            menu.addSeparator()

        # 视图
        menu.addAction("全屏切换 (F11)", self.toggleFullscreen)
        menu.addSeparator()

        # 其他
        menu.addAction("显示信息 (Ctrl+I)", self.showMediaInfo)
        menu.addAction("清空媒体 (Ctrl+W)", self.clear)
        menu.addSeparator()
        menu.addAction("退出 (Ctrl+Q)", self.close)

        menu.exec_(event.globalPos())

    # ==================== 信号处理 ====================

    def onPlayerStateChanged(self, state):
        """播放器状态变化"""
        self.is_playing = (state == QMediaPlayer.PlayingState)
        self.playStateChanged.emit(self.is_playing)

    def onPositionChanged(self, position):
        """播放位置变化"""
        pass

    def onDurationChanged(self, duration):
        """总时长变化"""
        pass

    def onPlayerError(self, error):
        """播放器错误"""
        error_msg = f"播放错误: {error}"
        self.errorOccurred.emit(error_msg)

    # ==================== 公共属性访问 ====================

    def getCurrentMedia(self):
        """获取当前媒体信息"""
        return {
            'path': self.current_media_path,
            'is_video': self.is_video,
            'is_image': self.is_image,
            'is_playing': self.is_playing,
            'is_muted': self.is_muted,
            'volume': self.volume
        }

class WallpaperEngine(QWidget):
    """极简壁纸引擎 - 自动循环播放，不可暂停"""

    # 定义信号
    mediaLoaded = pyqtSignal(str)  # 媒体加载完成
    mutedChanged = pyqtSignal(bool)  # 静音状态变化
    errorOccurred = pyqtSignal(str)  # 错误信号

    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化变量
        self.current_media_path = ""
        self.is_muted = False
        self.is_playing = False
        self.is_image = False
        self.original_pixmap = None
        self.fade_alpha = 0
        self.fade_timer = None

        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

        # 初始化UI
        self.initUI()

        # 初始化媒体播放器
        self.initMediaPlayer()

        # 初始化快捷键
        self.initShortcuts()

        # 启动淡入效果
        self.startFadeIn()

    def initUI(self):
        """初始化用户界面"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 视频显示部件
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.video_widget)

    def initMediaPlayer(self):
        """初始化媒体播放器"""
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)

        # 设置循环播放
        self.media_player.mediaStatusChanged.connect(self.onMediaStatusChanged)

        # 连接错误信号
        self.media_player.error.connect(self.onPlayerError)

        # 设置初始音量
        self.media_player.setVolume(50)

        # 设置播放结束后自动重新开始
        self.media_player.mediaStatusChanged.connect(self.handleMediaStatus)

    def initShortcuts(self):
        """初始化快捷键"""
        # 打开文件
        shortcut_open = QShortcut(QKeySequence("Ctrl+O"), self)
        shortcut_open.activated.connect(self.openFile)

        # 静音切换
        shortcut_mute = QShortcut(QKeySequence("Ctrl+M"), self)
        shortcut_mute.activated.connect(self.toggleMute)

        # 退出程序
        shortcut_quit = QShortcut(QKeySequence("Ctrl+Q"), self)
        shortcut_quit.activated.connect(self.close)

    def startFadeIn(self):
        """启动淡入效果"""
        self.fade_alpha = 0
        if self.fade_timer:
            self.fade_timer.stop()

        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.updateFade)
        self.fade_timer.start(20)  # 20毫秒更新一次

    def updateFade(self):
        """更新淡入效果"""
        self.fade_alpha += 5
        if self.fade_alpha >= 255:
            self.fade_alpha = 255
            if self.fade_timer:
                self.fade_timer.stop()
                self.fade_timer = None

    def openFile(self):
        """打开文件 - 唯一的外部控制函数之一"""
        # 显示文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择壁纸文件",
            "",
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.flv *.wmv *.webm);;"
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.gif *.webp);;"
            "所有文件 (*.*)"
        )

        if file_path and os.path.exists(file_path):
            self.loadMedia(file_path)

    def toggleMute(self):
        """切换静音 - 唯一的外部控制函数之二"""
        self.is_muted = self.is_muted
        self.media_player.setMuted(self.is_muted)
        self.mutedChanged.emit(self.is_muted)

        # 显示静音状态提示
        if self.is_muted:
            self.showTemporaryMessage("🔇 已静音", 1000)
        else:
            self.showTemporaryMessage("🔊 取消静音", 1000)

    def loadMedia(self, file_path):
        """加载媒体文件"""
        try:
            self.current_media_path = file_path

            # 判断文件类型
            file_ext = os.path.splitext(file_path)[1].lower()
            image_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
            video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']

            if file_ext in image_exts:
                self.loadImage(file_path)
            elif file_ext in video_exts:
                self.loadVideo(file_path)
            else:
                self.errorOccurred.emit(f"不支持的文件格式: {file_ext}")
                return

            self.mediaLoaded.emit(file_path)

        except Exception as e:
            self.errorOccurred.emit(f"加载文件失败: {str(e)}")

    def loadVideo(self, file_path):
        """加载视频作为壁纸"""
        # 重置图片
        self.resetImage()

        # 设置媒体
        url = QUrl.fromLocalFile(file_path)
        content = QMediaContent(url)
        self.media_player.setMedia(content)

        self.is_image = False

        # 开始播放
        self.playVideo()

        # 显示成功消息
        self.showTemporaryMessage(f"✓ 已加载视频壁纸", 1500)

    def loadImage(self, file_path):
        """加载图片作为壁纸"""
        try:
            # 重置视频
            self.resetVideo()

            # 加载图片
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                # 尝试使用PIL加载
                pil_image = Image.open(file_path)
                if pil_image.mode != "RGBA":
                    pil_image = pil_image.convert("RGBA")
                data = pil_image.tobytes("raw", "RGBA")
                qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimage)

            if pixmap.isNull():
                raise Exception("无法加载图片")

            self.original_pixmap = pixmap
            self.is_image = True

            # 显示图片
            self.showImage()

            # 显示成功消息
            self.showTemporaryMessage(f"✓ 已加载图片壁纸", 1500)

        except Exception as e:
            self.errorOccurred.emit(f"加载图片失败: {str(e)}")

    def playVideo(self):
        """播放视频（自动循环）"""
        if not self.is_image:  # 确保不是图片模式
            self.media_player.play()
            self.is_playing = True

    def showImage(self):
        """显示图片（自适应填充）"""
        if not self.original_pixmap or self.original_pixmap.isNull():
            return

        # 获取窗口大小
        window_size = self.size()
        if window_size.width() <= 0 or window_size.height() <= 0:
            return

        # 计算缩放后的图片大小（填充模式）
        scaled_pixmap = self.original_pixmap.scaled(
            window_size,
            Qt.KeepAspectRatioByExpanding,  # 保持宽高比并填充
            Qt.SmoothTransformation
        )

        # 计算裁剪位置（居中）
        x = (scaled_pixmap.width() - window_size.width()) // 2
        y = (scaled_pixmap.height() - window_size.height()) // 2

        # 裁剪并设置
        cropped_pixmap = scaled_pixmap.copy(x, y, window_size.width(), window_size.height())

        # 创建调色板设置背景
        from PyQt5.QtGui import QPalette
        palette = QPalette()
        palette.setBrush(QPalette.Window, cropped_pixmap)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def handleMediaStatus(self, status):
        """处理媒体状态 - 实现循环播放"""
        if status == QMediaPlayer.EndOfMedia:
            # 播放结束时自动重新开始
            self.media_player.setPosition(0)
            self.media_player.play()

    def resetImage(self):
        """重置图片显示"""
        self.is_image = False
        self.original_pixmap = None

        # 重置背景
        from PyQt5.QtGui import QPalette
        palette = QPalette()
        palette.setColor(QPalette.Window, Qt.black)
        self.setPalette(palette)

    def resetVideo(self):
        """重置视频播放"""
        if self.is_playing:
            self.media_player.stop()
        self.media_player.setMedia(QMediaContent())
        self.is_playing = False

    def onMediaStatusChanged(self, status):
        """媒体状态变化"""
        # 自动循环播放
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()

    def onPlayerError(self, error):
        """播放器错误"""
        error_msg = f"播放错误: {error}"
        self.errorOccurred.emit(error_msg)
        self.showTemporaryMessage(f"✗ 播放错误", 2000)

    def resizeEvent(self, event):
        """窗口大小变化事件"""
        super().resizeEvent(event)

        # 重新显示图片（自适应）
        if self.is_image and self.original_pixmap:
            QTimer.singleShot(50, self.showImage)

    def getCurrentMedia(self):
        """获取当前媒体信息（只读）"""
        return {
            'path': self.current_media_path,
            'is_image': self.is_image,
            'is_muted': self.is_muted,
            'is_playing': self.is_playing
        }

    def isMuted(self):
        """获取静音状态"""
        return self.is_muted

    def getMediaPath(self):
        """获取当前媒体路径"""
        return self.current_media_path
