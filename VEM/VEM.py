import ctypes
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import darkdetect
import psutil
import pywintypes
from MetaverseSDK.MetaverseTool.Config import JsonConfigTool

from MetaverseSDK.MetaverseUI.MCore.MPool.MBaseSoundPool import BSP
from MetaverseSDK.MetaverseUI.MCore.MPool.MSvgIconPool import SIP
from MetaverseSDK.MetaverseUI.MCore.MThread.MFileWorker import DeleteFolder
from MetaverseSDK.MetaverseUI.MCore.MThread.MUnzipWorker import UnzipWorker, UnzipWorkerByte
from MetaverseSDK.MetaverseUI.MReviseWidgets.MLabel import BodyLabel
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem, QStackedWidget,QFileDialog
from PyQt5.QtCore import Qt, QLocale, QTimer, QSize, QEventLoop, QEvent, QObject
from pathvalidate import is_valid_filepath
from qfluentwidgets import FluentWindow, setTheme, FluentIcon, NavigationItemPosition, setThemeColor, SimpleCardWidget,\
    InfoBar, InfoBarPosition, Dialog, RoundMenu, Action, ListWidget,\
    FluentTranslator, LineEdit,SplashScreen, NavigationPanel, NavigationToolButton, \
    Flyout, FlyoutAnimationType, FlyoutView, InfoBadge, InfoBadgePosition, InfoBadgeManager
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow
from qframelesswindow import StandardTitleBar

from MetaverseSDK.MetaverseUI.MFluentWidgets.MIndeterminateProgressRingDialog import CometTailIndeterminateProgressRingDialog,\
    FixedLengthIndeterminateProgressRingDialog,SegmentedArcIndeterminateProgressRingDialog,IndeterminateProgressRingDialog

from MetaverseSDK.MetaverseUI.MFluentWidgets.MProgressBarDialog import ProgressBarDialog
from MetaverseSDK.MetaverseUI.MFluentWidgets.MProgressRingDialog import ByteProgressRingDialog,ProgressRingDialog

from MetaverseSDK.MetaverseUI.MFluentWidgets.MDialog import LineDialog,WorkingDirectorySelectLineDialog,LineDictDialog,\
    NotificationDialog,QuickCommandDialog,TextEditDialog

from MetaverseSDK.MetaverseUI.MSpecial.MCmdEmbedWidget import CmdEmbedWidget

from MetaverseSDK.MetaverseTool.Config.JsonConfigPool import JCP

from MetaverseSDK.MetaverseResource import MetaverseSVG, MetaverseOGG

import Threads
import ico
import tool
import objgraph

from MetaverseSDK.MetaverseResource.MetaverseFluentIcon import MetaverseFluentIcon

from uimixin import UiMixin
from updatemixin import UpdateMixin


# 全局配置OpenGL渲染参数
# 额外开启Qt的OpenGL硬件渲染后端，将所有UI绘制任务直接交给GPU处理，大幅降低CPU渲染负载
# 部分老旧集成显卡可能不支持OpenGL 3.3核心模式，可以降级到setVersion(2, 0)保证兼容性
# 不要和Qt的软件渲染后端同时启用，避免出现渲染冲突导致界面闪烁
# fmt = QSurfaceFormat()
# fmt.setVersion(3, 3)  # 指定OpenGL 3.3版本，兼容性和性能平衡最优
# fmt.setProfile(QSurfaceFormat.CoreProfile)  # 使用核心模式，移除废弃API
# fmt.setSamples(4)  # 开启4倍抗锯齿，提升画面质感
# QSurfaceFormat.setDefaultFormat(fmt)


# # 跨工作目录
# # 获取当前脚本所在目录
# current_dir = os.path.dirname(os.path.abspath(__file__))
# # 将当前目录添加到Python模块搜索路径
# if current_dir not in sys.path:
#     sys.path.append(current_dir)

# 导航栏徽章管理器
@InfoBadgeManager.register("StableHiddenNav")
class StableHiddenNavBadgeManager(InfoBadgeManager):

    def eventFilter(self, obj, e):
        if obj is not self.target:
            return super().eventFilter(obj, e)

        # 1️⃣ 如果徽章逻辑上是隐藏的，直接吃掉 Show 事件
        if e.type() == QEvent.Show and not self.badge.isVisible():
            return True

        # 2️⃣ Resize / Move 始终参与定位（防止左上角）
        if e.type() in (QEvent.Resize, QEvent.Move):
            self.badge.move(self.position())

        return super().eventFilter(obj, e)

class FluentOverlayWindow(FramelessWindow):
    """
    浮层版 FluentWindow（类似 Win11 汉堡菜单）
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitleBar(StandardTitleBar(self))

        # 主内容
        self.stackWidget = QStackedWidget(self)

        # 导航面板（浮层）
        self.navPanel = NavigationPanel(self, True)
        self.navPanel.setExpandWidth(240)
        self.navPanel.setAcrylicEnabled(True)
        self.navPanel.hide()

        # 汉堡按钮
        self.menuBtn = NavigationToolButton(FluentIcon.MENU, self.titleBar)
        self.titleBar.hBoxLayout.insertWidget(3, self.menuBtn)
        self.menuBtn.clicked.connect(self.toggleNav)

        # 布局
        self.container = QWidget(self)
        self.vLayout = QVBoxLayout(self.container)
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.vLayout.addWidget(self.stackWidget)

        #self.setCentralWidget(self.container)

        self.resize(960, 640)
        self.setWindowTitle("Fluent Overlay Window")

        self.stackWidget.currentChanged.connect(self._syncNav)

    # ------------------ API ------------------

    def addSubInterface(self, widget: QWidget, icon, text: str,
                        position=NavigationItemPosition.TOP):
        routeKey = widget.objectName() or text

        self.stackWidget.addWidget(widget)

        self.navPanel.addItem(
            routeKey=routeKey,
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(widget),
            position=position
        )

    def switchTo(self, widget: QWidget):
        self.stackWidget.setCurrentWidget(widget)

    def toggleNav(self):
        if self.navPanel.isVisible():
            self.navPanel.collapse()
        else:
            self.navPanel.show()
            self.navPanel.expand()

    # ------------------ 内部 ------------------

    def _syncNav(self, index):
        widget = self.stackWidget.widget(index)
        self.navPanel.setCurrentItem(widget.objectName())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.navPanel.setFixedHeight(self.height())

def install_click_debug(widget):
    """
    给任意 QWidget 安装点击调试：
    鼠标按下时打印被点中的 Qt 控件
    """
    class ClickDebug(QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.MouseButtonPress:
                pos = event.globalPos()
                app = QApplication.instance()

                # Qt 视角：鼠标下是哪个控件
                under = app.widgetAt(pos)

                if under:
                    print("=" * 60)
                    print(f"🖱️  鼠标点击 @ {pos.x()}, {pos.y()}")
                    print(f"🎯 Qt 控件:")
                    print(f"   • 类型 : {type(under).__name__}")
                    print(f"   • 对象名: {under.objectName() or '(未命名)'}")
                    print(f"   • 地址 : 0x{id(under):X}")
                    print(f"   • 父链:")
                    p = under
                    while p:
                        print(f"     ↳ {type(p).__name__}  name={p.objectName()}")
                        p = p.parent()
                    print("=" * 60)
                else:
                    print("🖱️  点击位置没有 Qt widget（可能是原生窗口/桌面）")

            return super().eventFilter(obj, event)

    d = ClickDebug()
    widget.installEventFilter(d)
    widget._click_debug = d   # 防 GC

# install_click_debug(self) # 安装gui控件调试器

class MainUI(UiMixin,UpdateMixin,FluentWindow):
    def __init__(self):
        super().__init__()
        # 图钉开关
        self.switch_pin_bool = True
        # 电源开关
        self.switch_power_bool = True
        # 控制台列表开关
        self.switch_console_list_bool = False
        # 预设脚本上限开关
        self.switch_preset_scripts_max_bool = False
        # 图钉命令上限开关
        self.switch_pin_comm_max_bool = False
        # 配置命令全局行号
        self.config_older_number = 0
        # 配置命令列表
        self.config_older_list = []
        # 命令对象字典
        self.order_obj_list = []
        # 启动动画-快列表
        self.startup_animation_high = ["不显示-0ms","非常快-10ms","快-100ms","稍快-500ms"]
        # 启动动画-中列表
        self.startup_animation_medium = ["中-700ms","常规-1000ms","一般-1500ms"]
        # 启动动画-慢列表
        self.startup_animation_off = ["稍慢-2000ms","慢-2500ms","非常慢-5000ms","久-10000ms"]
        # 启动图标列表
        self.startup_ico_list = ["小-80px","中-120px","大-240px"]
        # CMD对象字典
        self.cmd_obj_dict = {}
        # 控制台对象字典
        self.console_obj_dict = {}
        # 预设命令字典
        self.preset_scripts_dict = {}
        # 主题映射表
        self.theme_map = {"明亮": "LIGHT", "黑暗": "DARK", "自动": "AUTO", }
        # 反转主题映射表
        self.twist_theme_map = {"LIGHT": "明亮", "DARK": "黑暗", "AUTO": "自动", }
        # 新建虚拟环境命令批处理列表
        self.python_batch_list = []
        # 配置虚拟环境命令批处理列表
        self.config_python_batch_list = []
        # 下载列表
        self.download_list = []
        # 便携式环境批处理集合
        self.emb_batch_set = set()

        # 通知和内容
        self.emb_notification = False
        self.emb_notification_text = ''

        # 版本
        self.VEM_Version = "v1.16.1"
        self.CMD_Version = "v0.8.0"

        # 预制图标
        # 绿色开始
        self.PLAY_SOLID_icon = FluentIcon.PLAY_SOLID.icon(color=QColor("#00ff00"))
        # 绿色发送
        self.SEND_FILL_icon = FluentIcon.SEND_FILL.icon(color=QColor("#00ff00"))
        # 红色电源
        self.POWER_BUTTON_icon = FluentIcon.POWER_BUTTON.icon(color=QColor("#ff0000"))
        # 红色扫把
        self.BROOM_icon = FluentIcon.BROOM.icon(color=QColor("#ff0000"))
        # 橙色压缩包
        self.ZIP_FOLDER_icon = FluentIcon.ZIP_FOLDER.icon(color=QColor("#ffA500"))
        # 蓝色物联网
        self.IOT_icon = FluentIcon.IOT.icon(color=QColor("#00A5ff"))

        # 获取Python版本
        version_info = sys.version_info
        self.Python__version__ = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

        # 载入资源池
        SIP.load("Python",MetaverseSVG.Python)

        # 资源
        pixmap_VEM = QPixmap()
        pixmap_VEM.loadFromData(ico.VEM)
        self.resource_VEM = QIcon(pixmap_VEM)

        # 读取主题色
        self.theme_model = JCP.get("config.json", ["setting","theme_model"],"LIGHT")
        # 读取强调色
        self.theme_color = JCP.get("config.json", ["setting","theme_color"],"#ff009faa")
        # 读取云母效果
        self.mica_effect = JCP.get("config.json", ["setting","mica_effect"],True)
        # 读取懒加载
        self.lazy = JCP.get("config.json", ["setting","lazy"],False)
        # 自动强调色
        self.theme_color_auto = JCP.get("config.json", ["setting","theme_color_auto"],True)
        # 启用DPI缩放
        self.activated_dpi_zoom_switch = JCP.get("config.json", ["setting","DPI_zoom"],False)
        # 启用非整数缩放
        self.activated_dpi_non_int_zoom_switch = JCP.get("config.json", ["setting","DPI_non_int_zoom"],False)
        # 启用高DPI像素映射
        self.high_DPI_pixel_mapping = JCP.get("config.json", ["setting","high_DPI_pixel_mapping"],False)
        # 启动时全屏
        self.full_screen_startup_init_switch = JCP.get("config.json", ["setting","full_screen_startup"],False)
        # 启动后全屏
        self.full_screen_after_startup_init_switch = JCP.get("config.json", ["setting","full_screen_after_startup"],False)
        # 启动后最大化
        self.maximize_after_startup_init_switch = JCP.get("config.json", ["setting","maximize_after_startup"],False)
        # 关闭便携式环境的脱控通知
        self.close_emb_out_control_notification_switch = JCP.get("config.json",["setting","close_emb_out_control_notification_switch"], False)
        # 关闭虚拟环境开机提示
        self.close_venv_power_on_tip_switch = JCP.get("config.json",["setting","close_venv_power_on_tip_switch"], False)
        # 关闭虚拟环境关机提示
        self.close_venv_power_out_tip_switch = JCP.get("config.json",["setting","close_venv_power_out_tip_switch"], False)
        # 关闭控制台激活提示
        self.close_console_activation_tip_switch = JCP.get("config.json",["setting","close_console_activation_tip_switch"], False)
        # 关闭虚拟环境关机提示
        self.close_console_destroy_tip_switch = JCP.get("config.json",["setting","close_console_destroy_tip_switch"], False)
        # 关闭虚拟环境切换提示
        self.close_console_switch_tip_switch = JCP.get("config.json",["setting","close_console_switch_tip_switch"], False)
        # 强制更新CMD
        self.mandatory_update_CMD_switch = JCP.get("config.json", ["setting","refresh_CMD"], False)
        # 启用手动更新CMD
        self.enable_manual_update_CMD_switch = JCP.get("config.json", ["setting","manual_CMD"], False)
        # 启用CMD重启
        self.enable_cmd_reload_CMD_switch = JCP.get("config.json", ["setting","reload_CMD"], False)
        # 启用CMD全屏
        self.enable_cmd_full_screen_switch = JCP.get("config.json", ["setting","full_screen_CMD"], False)
        # 关机保护
        self.shutdown_protection_switch = JCP.get("config.json", ["setting","shutdown_protection"], True)
        # 重启保护
        self.reload_switch = JCP.get("config.json", ["setting","reload_protection"], True)
        # 全屏保护
        self.full_screen_switch = JCP.get("config.json", ["setting","full_screen"], True)
        # 自动进入环境
        self.auto_enter_venv = JCP.get("config.json", ["setting","auto_enter_venv"], True)
        # 嵌入延时
        self.delay_cmd = JCP.get("config.json", ["setting","delay"], "250ms")
        # 监控频率
        self.frequency_cmd = JCP.get("config.json", ["setting","frequency"], "0.5s") # 防止CMD阻塞UI
        # 回调时长
        self.pullback_duration = JCP.get("config.json", ["setting","pullback_duration"], "10ms")
        # CMD被动关机决定
        self.CMD_passive_shutdown = JCP.get("config.json", ["setting","CMD_passive_shutdown"], True)
        # 自动决定下的CMD被动关机通知
        self.disable_auto_CMD_passive_shutdown_notification = JCP.get("config.json", ["setting","disable_auto_CMD_passive_shutdown_notification"], False)
        # CMD自动配置模式
        self.auto_config_model = JCP.get("config.json", ["setting","auto_config_model"], "虚拟环境")
        # 虚拟环境配置命令回调时长
        self.venv_config_callback_duration = JCP.get("config.json", ["setting","venv_config_callback_duration"], "sync")
        # 控制台配置命令回调时长
        self.console_config_callback_duration = JCP.get("config.json", ["setting","console_config_callback_duration"], "50ms")
        # 允许叠加回调时长
        self.allow_overlay_callback_duration = JCP.get("config.json", ["setting","allow_overlay_callback_duration"], False)
        # 启动动画时长
        self.startup_animation_duration = JCP.get("config.json", ["setting","startup_animation_duration"], "常规-1000ms")
        # 启动图标大小
        self.startup_ico_size = JCP.get("config.json", ["setting","startup_ico_size"], "中-120px")
        # 启动图标阴影
        self.startup_ico_shadow = JCP.get("config.json", ["setting","startup_ico_shadow"], False)
        # 下载路径
        self.downloads_path = JCP.get("config.json", ["setting","downloads_path"],os.getcwd()+"\\Downloads")
        # 最大并行下载数
        self.max_parallel_download = JCP.get("config.json", ["setting","max_parallel_download"], "3")
        # 播放音效
        self.play_sound = JCP.get("config.json", ["setting","play_sound"], False)
        # 警告音效
        self.play_sound_warning = JCP.get("config.json", ["setting","play_sound_warning"], False)
        # 操作完成音效
        self.play_sound_operation_completed = JCP.get("config.json", ["setting","play_sound_operation_completed"], False)
        # 下载完成音效
        self.play_sound_download_complete = JCP.get("config.json", ["setting","play_sound_download_complete"], False)
        # 重要提示音效
        self.play_sound_important_tip = JCP.get("config.json", ["setting","play_sound_important_tip"], False)
        # 过渡时长
        self.transition_duration = JCP.get("config.json", ["setting","transition_duration"], "0ms")
        # 启动页面过渡时长
        self.startup_animation_transition_duration = JCP.get("config.json",["setting","startup_animation_transition_duration"],"0ms")
        # CMD坐标空间模式
        self.CMD_coordinate_space_mode = JCP.get("config.json", ["setting","CMD_coordinate_space_mode"], "逻辑像素模式")
        # 平滑滚动区域
        self.smooth_scrolling_area = JCP.get("config.json", ["setting","smooth_scrolling_area"], False)
        # 上下翻页堆叠部件
        self.page_up_down_stacked_widget = JCP.get("config.json", ["setting","page_up_down_stacked_widget"], False)
        # 禁止创建原生控件同级窗口
        self.prohibit_creating_native_control_windows_same_level = JCP.get("config.json", ["setting","prohibit_creating_native_control_windows_same_level"], False)
        # 启动时检查更新
        self.startup_check_update = JCP.get("config.json", ["setting","startup_check_update"], False)
        # 跳过退出保存
        self.skip_exit_save = JCP.get("config.json", ["setting","skip_exit_save"], False)

        # 初始化音效池
        BSP.load("Warning",MetaverseOGG.Warning)
        BSP.load("OperationCompleted",MetaverseOGG.OperationCompleted)
        BSP.load("DownloadComplete",MetaverseOGG.DownloadComplete)
        BSP.load("ImportantTip",MetaverseOGG.ImportantTip)

        # 后台线程引用
        self.github_release_thread = None

        self.init_window()  # 初始化窗口
        self.init_navigationInterface()  # 初始化导航栏
        self.init_download_badge() # 初始化导航栏下载徽章
        self.init_menu() # 初始化菜单
        self.init_download_manager() # 初始化下载管理器

    # 初始化窗口
    def init_window(self):
        # 基础属性
        self.setWindowTitle("VEM 虚拟环境管理器")
        self.setWindowIcon(self.resource_VEM)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VEM")

        # 更新云母效果
        self.setMicaEffectEnabled(self.mica_effect)

        # 如果不是不显示-0ms 开始
        if self.startup_animation_duration != "不显示-0ms":
            # 创建启动页面
            self.splashScreen = SplashScreen(self.windowIcon(), self, enableShadow=self.startup_ico_shadow)

            size = {"小-80px":80,"中-120px":120,"大-240px":240}.get(self.startup_ico_size,120)
            self.splashScreen.setIconSize(QSize(size, size))
            #self.splashScreen.titleBar.closeBtn.setEnabled(False)
            self.splashScreen.titleBar.closeBtn.clicked.connect(lambda :sys.exit())

        screen_size = QApplication.primaryScreen().availableGeometry()
        # 中心坐标
        h = 1200
        w = 800
        x = (screen_size.width() - h) // 2
        y = (screen_size.height() - w) // 2
        self.setGeometry(x, y, h, 800)  # 窗口大小 还原

        # 全屏
        if self.full_screen_startup_init_switch:
            self.showFullScreen()

        # 如果不是不显示-0ms 结束
        if self.startup_animation_duration != "不显示-0ms":
            startup_animation_duration = {"0ms": 0, "10ms": 10, "20ms": 20, "30ms": 30}.get(self.startup_animation_transition_duration, 0)
            # 提前显示主窗口 防止启动页面饿死 并延时显示防止出现Win7窗口
            time = QTimer()
            time.singleShot(startup_animation_duration, lambda: self.show())

            # 延时
            self.createSubInterface()

            # 关闭启动页
            self.splashScreen.finish()

        # 启动设置
        # 启动时检查更新
        if self.startup_check_update:
            self.get_new_version()

    # 初始化导航栏
    def init_navigationInterface(self):
        self.navigationInterface.setExpandWidth(170)  # 固定抽屉长度

        # 主页
        self.Home = QWidget(self)
        self.Home.setObjectName("Home")
        self.init_homepage()  # 初始化主页
        self.addSubInterface(
            self.Home,
            FluentIcon.HOME,
            "主页"
        )

        # 虚拟环境
        self.VenvManage = QWidget(self)
        self.VenvManage.setObjectName("VenvManage")
        self.init_venv_manage()  # 初始化环境管理
        self.addSubInterface(
            self.VenvManage,
            FluentIcon.LIBRARY,
            "环境"
        )

        # 控制台
        self.Console = QWidget(self)
        self.Console.setObjectName("Console")
        self.init_console() # 初始化控制台
        self.addSubInterface(
            self.Console,
            FluentIcon.COMMAND_PROMPT,
            "控制台"
        )

        # 图钉管理
        self.PIN_Manage = QWidget(self)
        self.PIN_Manage.setObjectName("PIN_Manage")
        self.init_pin() # 初始化配置文件
        self.addSubInterface(
            self.PIN_Manage,
            FluentIcon.PIN,
            "图钉"
        )

        # 预设脚本管理
        self.PresetScripts_Manage = QWidget(self)
        self.PresetScripts_Manage.setObjectName("PresetScripts_Manage")
        self.init_preset_scripts() # 初始化预设脚本
        self.addSubInterface(
            self.PresetScripts_Manage,
            FluentIcon.QUICK_NOTE,
            "预设脚本"
        )

        # 配置文件管理
        self.ConfigFile_Manage = QWidget(self)
        self.ConfigFile_Manage.setObjectName("ConfigFile_Manage")
        self.init_config() # 初始化配置文件
        self.addSubInterface(
            self.ConfigFile_Manage,
            FluentIcon.DOCUMENT,
            "配置文件"
        )

        # 虚拟环境管理
        self.Venv = QWidget(self)
        self.Venv.setObjectName("Venv")
        self.init_venv()  # 初始化环境管理
        self.addSubInterface(
            self.Venv,
            self.IOT_icon,
            "虚拟环境"
        )

        # 便携式环境
        self.EmbEnv = QWidget(self)
        self.EmbEnv.setObjectName("EmbEnv")
        self.init_emb() # 初始化便携式环境
        self.addSubInterface(
            self.EmbEnv,
            self.ZIP_FOLDER_icon,
            "便携式环境"
        )

        # 基础环境
        self.BaseEnv = QWidget(self)
        self.BaseEnv.setObjectName("BaseEnv")
        self.init_python() # 初始化基础环境
        self.addSubInterface(
            self.BaseEnv,
            SIP.get("Python"),
            "基础环境"
        )

        # 创建
        self.Created = QWidget(self)
        self.Created.setObjectName("Created")
        self.init_created()  # 初始化创建环境
        self.addSubInterface(
            self.Created,
            FluentIcon.ADD,
            "创建",
            position=NavigationItemPosition.BOTTOM
        )

        # 下载
        self.Download = QWidget(self)
        self.Download.setObjectName("Download")
        self.init_download()  # 初始化下载
        self.addSubInterface(
            self.Download,
            FluentIcon.DOWNLOAD,
            "下载",
            position=NavigationItemPosition.BOTTOM
        )

        # 链接
        self.Link = QWidget(self)
        self.Link.setObjectName("Link")
        self.init_link()  # 初始化链接
        self.addSubInterface(
            self.Link,
            MetaverseFluentIcon.Link,
            "链接",
            position=NavigationItemPosition.BOTTOM
        )

        # 安装
        self.Installation = QWidget(self)
        self.Installation.setObjectName("Installation")
        self.init_installation()  # 初始化安装
        self.addSubInterface(
            self.Installation,
            MetaverseFluentIcon.Installation,
            "安装",
            position=NavigationItemPosition.BOTTOM
        )

        # 下载列表 不可选中导航栏按钮
        self.navigationInterface_DownloadList = self.navigationInterface.addItem(
            routeKey='DownloadList',
            icon=MetaverseFluentIcon.DownloadList,
            text='下载列表',
            onClick=self.flyout_download_list,
            selectable=False,              # 不可选中，不切换界面
            position=NavigationItemPosition.BOTTOM
        )

        # 设置
        self.setting = QWidget(self)
        self.setting.setObjectName("setting")
        self.init_setting()  # 初始化设置
        self.addSubInterface(
            self.setting,
            FluentIcon.SETTING,
            "设置",
            position=NavigationItemPosition.BOTTOM
        )

    # 启动页面延时
    def createSubInterface(self):
        duration = self.startup_animation_duration.split('-')
        loop = QEventLoop(self)
        QTimer.singleShot(int(duration[1][:-2]), loop.quit)
        loop.exec()

    # 选择环境树状表项目
    def select_venv_item(self, index):
        try:
            item = self.venv_tree.itemFromIndex(index)
            if not item:
                return
            # 有子节点 = 文件夹 排除
            if item.childCount() > 0:
                # 禁用电源按钮
                self.cmd_power_button.setEnabled(False)
                # 禁用图钉按钮
                self.pin_button.setEnabled(False)
                # 禁用预设脚本按钮
                self.preset_scripts_button.setEnabled(False)
                # 禁用手动更新按钮
                self.manual_update_button.setEnabled(False)
                # 禁用重启按钮
                self.cmd_reload_button.setEnabled(False)
                # 禁用全屏按钮
                self.cmd_full_screen_button.setEnabled(False)
                return
            # 是python 单独设置后排除
            type_item = item.data(0, Qt.UserRole)
            if type_item["type"] == "python":
                self.cmd_stackedwidget.setCurrentIndex(1)
                self.power_python_label_text.setText(type_item["name"])
                self.power_python_path_label_text.setText(type_item["path"])
                # 禁用电源按钮
                self.cmd_power_button.setEnabled(False)
                # 禁用图钉按钮
                self.pin_button.setEnabled(False)
                # 禁用预设脚本按钮
                self.preset_scripts_button.setEnabled(False)
                # 禁用手动更新按钮
                self.manual_update_button.setEnabled(False)
                # 禁用重启按钮
                self.cmd_reload_button.setEnabled(False)
                # 禁用全屏按钮
                self.cmd_full_screen_button.setEnabled(False)
                return
            # 是emb 单独设置后排除
            if type_item["type"] == "emb":
                self.cmd_stackedwidget.setCurrentIndex(2)
                self.power_emb_label_text.setText(type_item["name"])
                self.power_emb_path_label_text.setText(type_item["dir"])
                # 三元表达式实现 如果为空 设置空白 否则不变
                self.power_start_script_path_label_text.setText(type_item["start_script"] if type_item["start_script"] else " ")
                # 禁用电源按钮
                self.cmd_power_button.setEnabled(False)
                # 禁用图钉按钮
                self.pin_button.setEnabled(False)
                # 禁用预设脚本按钮
                self.preset_scripts_button.setEnabled(False)
                # 禁用手动更新按钮
                self.manual_update_button.setEnabled(False)
                # 禁用重启按钮
                self.cmd_reload_button.setEnabled(False)
                # 禁用全屏按钮
                self.cmd_full_screen_button.setEnabled(False)
                return

            # 解禁电源按钮
            self.cmd_power_button.setEnabled(True)
            # 解禁图钉按钮
            self.pin_button.setEnabled(True)
            # 解禁预设脚本按钮
            self.preset_scripts_button.setEnabled(True)

            # 启用手动更新
            if self.enable_manual_update_CMD_switch:
                # 解禁手动更新按钮
                self.manual_update_button.setEnabled(True)

            # 启用CMD重启
            if self.cmd_reload_button:
                # 解禁重启按钮
                self.cmd_reload_button.setEnabled(True)

            # 启用CMD全屏
            if self.enable_cmd_full_screen_switch:
                # 解禁全屏按钮
                self.cmd_full_screen_button.setEnabled(True)

            item = self.venv_tree.itemFromIndex(index)
            data = item.data(0, Qt.UserRole)

            # 存在 使用CMD的路径而非名称
            if data.get("dir") in self.cmd_obj_dict:
                self.cmd_stackedwidget.setCurrentWidget(self.cmd_obj_dict[data.get("dir")][1])
                # 更新当前选择的CMD
                self.select_cmd = self.cmd_obj_dict[data.get("dir")][0]
                if self.mandatory_update_CMD_switch:
                    # 强制刷新CMD
                    self.select_cmd.refresh()
                self.cmd_power_button.setIcon(self.POWER_BUTTON_icon)
                self.switch_power_bool = False
            # 如果当前CMD不存在
            else:
                self.cmd_stackedwidget.setCurrentIndex(0)
                self.power_label_text.setText(item.text(0))
                self.cmd_power_button.setIcon(self.PLAY_SOLID_icon)
                self.switch_power_bool = True
        except Exception as a:
            print(a)

    # 应用图钉
    def apply_commands(self,item):
        try:
            self.select_cmd.send_command(item.text())
        except pywintypes.error as e:
            if e.winerror == 1816:
                print(e)
                InfoBar.warning(
                    title="警告",
                    content=f"配额不足 无法处理此命令",
                    parent=self,
                    position=InfoBarPosition.TOP
                )
        except Exception as a:
            print(a)
            InfoBar.warning(
                title="警告",
                content=f"CMD未开机或被销毁",
                parent=self,
                position=InfoBarPosition.TOP
            )

    # 开关图钉
    def switch_pin(self):
        # 开
        if not self.switch_pin_bool:
            self.pin_button.setIcon(FluentIcon.PIN)
            self.switch_pin_bool = True
        # 关
        else:
            self.pin_button.setIcon(FluentIcon.UNPIN)
            self.switch_pin_bool = False

        self.pin_card.toggle()

    # 开关机按钮
    def power_on_off(self):
        try:
            item = self.venv_tree.currentItem()
            # 按钮状态是开机 并且选中不为空
            if self.switch_power_bool is True and item is not None:
                # 构建新CMD
                cmd_card = SimpleCardWidget()
                cmd_card_vlayout = QVBoxLayout()
                cmd_card.setLayout(cmd_card_vlayout)
                self.cmd_stackedwidget.addWidget(cmd_card)
                self.cmd_stackedwidget.setCurrentWidget(cmd_card)

                # 防崩溃式硬转换
                delay = {"0ms": 0, "50ms": 50, "100ms": 100, "250ms": 250, "500ms": 500}.get(self.delay_cmd, 0)
                frequency = {"0.5s": 0.5, "1.0s": 1, "2.0s": 2, "5.0s": 5}.get(self.frequency_cmd, 0.5) # 最低0.5s 防止阻塞
                pullback_duration = {"0ms": 0, "10ms": 10, "50ms": 50, "100ms": 100,"250ms": 250,"500ms": 500}.get(self.pullback_duration, 0)
                coordinate_space = {"逻辑像素模式":False,"物理像素模式":True}.get(self.CMD_coordinate_space_mode,False)
                # 获取项内数据
                data = item.data(0, Qt.UserRole)

                # 进入盘符 防止bug
                pt = os.path.splitdrive(data.get("start_parameter"))
                # 添加CMD
                cmd = CmdEmbedWidget(self,workdir=pt[0], mode="timer", delay=delay, frequency=frequency,physical_pixels=coordinate_space)
                cmd_card_vlayout.addWidget(cmd)

                # 添加CMD对象字典
                self.cmd_obj_dict[data.get("dir")] = [cmd, cmd_card]
                # 更新当前选择的CMD
                self.select_cmd = cmd

                # 更新图标
                self.cmd_power_button.setIcon(self.POWER_BUTTON_icon)
                item.setIcon(0, self.PLAY_SOLID_icon)
                # 绑定意外退出信号
                self.select_cmd.monitor_thread.running_changed.connect(lambda state: self.unexpected_exit(item,item.text(0), data.get("dir"), state, self.select_cmd, cmd_card))

                # 关闭开关机通知
                if not self.close_venv_power_on_tip_switch:
                    # 提示
                    InfoBar.success(
                        title="已启动",
                        content=f"虚拟环境 {item.text(0)} 已启动",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )

                # 自动进入环境
                if self.auto_enter_venv:
                    # 回调时长使用CMD的延时
                    # 回调时长叠加
                    auto_enter_timer = QTimer()
                    auto_enter_timer.singleShot(delay+pullback_duration, lambda:cmd.send_command(pt[1]))

                self.switch_power_bool = False
            elif self.switch_power_bool is False and item is not None:
                if self.shutdown_protection_switch:
                    w = Dialog("确认关闭虚拟环境？", "强制关闭会丢失当前全部的工作进度 并且不会保留任何工作数据", self)

                    if w.exec():
                        # 关闭当前的CMD
                        if self.select_cmd.finder_thread:
                            self.select_cmd.finder_thread.stop()
                            self.select_cmd.finder_thread.wait()
                            self.select_cmd.finder_thread.deleteLater()
                        if self.select_cmd.monitor_thread:
                            self.select_cmd.monitor_thread.stop()
                            self.select_cmd.monitor_thread.wait()
                            self.select_cmd.monitor_thread.deleteLater()
                        if self.select_cmd.proc:
                            self.select_cmd.proc.terminate()
                            self.select_cmd.proc.wait(timeout=1)
                        self.select_cmd.safe_destroy_cmd()  # 完全删除

                        # 回到选择页
                        self.cmd_stackedwidget.setCurrentIndex(0)
                        self.power_label_text.setText(item.text(0))
                        self.switch_power_bool = True
                        # 移出键
                        data = item.data(0, Qt.UserRole)
                        del self.cmd_obj_dict[data.get("dir")]
                        # 更新图标
                        self.cmd_power_button.setIcon(self.PLAY_SOLID_icon)
                        item.setIcon(0, self.POWER_BUTTON_icon)

                        # 关闭开关机通知
                        if not self.close_venv_power_out_tip_switch:
                            InfoBar.info(
                                title="已关闭",
                                content=f"虚拟环境 {item.text(0)} 已关闭",
                                parent=self,
                                position=InfoBarPosition.TOP
                            )
                else:
                    # 关闭当前的CMD
                    if self.select_cmd.finder_thread:
                        self.select_cmd.finder_thread.stop()
                        self.select_cmd.finder_thread.wait()
                        self.select_cmd.finder_thread.deleteLater()
                    if self.select_cmd.monitor_thread:
                        self.select_cmd.monitor_thread.stop()
                        self.select_cmd.monitor_thread.wait()
                        self.select_cmd.monitor_thread.deleteLater()
                    if self.select_cmd.proc:
                        self.select_cmd.proc.terminate()
                        self.select_cmd.proc.wait(timeout=1)
                    self.select_cmd.safe_destroy_cmd()  # 完全删除

                    # 回到选择页
                    self.cmd_stackedwidget.setCurrentIndex(0)
                    self.power_label_text.setText(item.text(0))
                    self.switch_power_bool = True
                    # 移出键
                    data = item.data(0, Qt.UserRole)
                    del self.cmd_obj_dict[data.get("dir")]
                    # 更新图标
                    self.cmd_power_button.setIcon(self.PLAY_SOLID_icon)
                    item.setIcon(0, self.POWER_BUTTON_icon)

                    # 关闭开关机通知
                    if not self.close_venv_power_out_tip_switch:
                        InfoBar.info(
                            title="已关闭",
                            content=f"虚拟环境 {item.text(0)} 已关闭",
                            parent=self,
                            position=InfoBarPosition.TOP
                        )
        except OSError as e: # 捕捉OS报错
            print(e)
            InfoBar.error(
                title="错误",
                content=str(e.strerror), # 转为字符串 防止类型二次崩溃
                parent=self,
                position=InfoBarPosition.TOP
            )
        except Exception as a:
            print(a)
            InfoBar.error(
                title="错误",
                content=str(a),
                parent=self,
                position=InfoBarPosition.TOP
            )

    # 关闭事件
    def closeEvent(self, event):
        # 有打开的CMD和控制台
        if self.cmd_obj_dict != {} or self.console_obj_dict != {}:
            w = Dialog("确认退出？", "仍有工作进度未保存 强制关闭会丢失当前的全部工作进度", self)
            # 确认
            w_exec = w.exec()
            if w_exec:
                # 批量删除未关闭的CMD
                for i in self.cmd_obj_dict:
                    cmd = self.cmd_obj_dict[i]
                    cmd = cmd[0]

                    try:
                        if cmd.finder_thread:
                            cmd.finder_thread.stop()
                        if cmd.monitor_thread:
                            cmd.monitor_thread.stop()

                        if cmd.proc and cmd.proc.pid:
                            parent = psutil.Process(cmd.proc.pid)
                            for child in parent.children(recursive=True):
                                child.kill()
                            parent.kill()

                    except Exception as e:
                        print(e)

                # 批量删除未关闭的控制台
                for i in self.console_obj_dict:
                    cmd = self.console_obj_dict[i]
                    cmd = cmd[0]

                    try:
                        if cmd.finder_thread:
                            cmd.finder_thread.stop()
                        if cmd.monitor_thread:
                            cmd.monitor_thread.stop()

                        if cmd.proc and cmd.proc.pid:
                            parent = psutil.Process(cmd.proc.pid)
                            for child in parent.children(recursive=True):
                                child.kill()
                            parent.kill()

                    except Exception as e:
                        print(e)

                super().closeEvent(event)
            # 取消
            elif not w_exec:
                event.ignore()
                return
        # 没有打开的CMD
        else:
            super().closeEvent(event)

        # 跳过退出保存
        if self.skip_exit_save:
            # 判断是否修改
            # 池中Json
            new_json = JCP.read("config.json")
            # 本地Json
            old_json = JsonConfigTool.read_json("config.json")
            # 是否相同
            same = JsonConfigTool.json_equal(new_json,old_json)
            # 不相同
            if not same:
                # 保存池
                JCP.save()
        else:
            # 保存池
            JCP.save()

    # 意外退出
    def unexpected_exit(self, item,cmd_name,path, state,obj,card):
        try:
            if not state:
                # cmd存在
                if path in self.cmd_obj_dict:
                    InfoBar.error(
                        title="意外退出",
                        content=f"虚拟环境 {cmd_name} 意外退出",
                        parent=self,
                        position=InfoBarPosition.TOP,
                        duration=1500
                    )
                    if obj.finder_thread:
                        obj.finder_thread.stop()
                        obj.finder_thread.wait()
                    if obj.monitor_thread:
                        obj.monitor_thread.stop()
                        obj.monitor_thread.wait()
                    if self.select_cmd.proc:
                        self.select_cmd.proc.terminate()
                    del self.cmd_obj_dict[path]
                    item.setIcon(0, self.POWER_BUTTON_icon)

                    # 是否是选中页
                    if self.cmd_stackedwidget.currentWidget() == card:
                        # 更新图标
                        self.cmd_power_button.setIcon(self.PLAY_SOLID_icon)
                        # 回到选择页
                        self.cmd_stackedwidget.setCurrentIndex(0)
                        self.power_label_text.setText(item.text(0))
                        self.switch_power_bool = True

                    # 播放音效 警告音效未禁用
                    if self.play_sound and not self.play_sound_warning:
                        BSP.play("Warning")

        except Exception as a:
            print(a)

    # 开关控制台列表
    def switch_console_list(self):
        # 开
        if not self.switch_console_list_bool:
            self.console_list_button.setIcon(FluentIcon.HIDE)
            self.switch_console_list_bool = True
        # 关
        else:
            self.console_list_button.setIcon(FluentIcon.VIEW)
            self.switch_console_list_bool = False
        self.console_list_card.toggle()

    # 开关控制台按钮 开
    def console_on(self):
        try:
            # 新建
            dialog = WorkingDirectorySelectLineDialog("激活控制台","输入控制台名称 工作目录","Console",self)
            if dialog.exec():
                cmd_name = dialog.line.text()
                dir_name = dialog.line_dir.text()
                # 判断是否重名
                if cmd_name in self.console_obj_dict:
                    InfoBar.warning(
                        title="激活失败",
                        content=f"控制台 {cmd_name} 已被激活",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                    return False # 返回给判断
                # 判断路径是否存在
                elif not os.path.exists(dir_name):
                    InfoBar.warning(
                        title="激活失败",
                        content=f"工作目录 {dir_name} 不存在",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                    return False
                else:
                    # 构建新CMD
                    cmd_card = SimpleCardWidget()
                    cmd_card_vlayout = QVBoxLayout()
                    cmd_card.setLayout(cmd_card_vlayout)
                    self.console_stackedwidget.addWidget(cmd_card)
                    self.console_stackedwidget.setCurrentWidget(cmd_card)

                    # 防崩溃式硬转换
                    delay = {"0ms": 0, "50ms": 50, "100ms": 100, "250ms": 250, "500ms": 500}.get(self.delay_cmd, 0)
                    frequency = {"0.5s": 0.5, "1.0s": 1, "2.0s": 2, "5.0s": 5}.get(self.frequency_cmd, 0.5) # 最低0.5s 防止阻塞
                    coordinate_space = {"逻辑像素模式":False,"物理像素模式":True}.get(self.CMD_coordinate_space_mode,False)

                    # 添加CMD
                    cmd = CmdEmbedWidget(self,workdir=dir_name, mode="timer", delay=delay, frequency=frequency,physical_pixels=coordinate_space)
                    cmd_card_vlayout.addWidget(cmd)

                    # 添加CMD对象字典
                    self.console_obj_dict[cmd_name] = [cmd, cmd_card]
                    # 更新当前选择的控制台
                    self.select_console = cmd
                    # 添加项
                    self.console_list.addItem(cmd_name)
                    # 选中最后项 也就是新加入项
                    self.console_list.setCurrentRow(self.console_list.count() - 1)
                    # 手动触发部分选中函数
                    # 启用手动更新
                    if self.enable_manual_update_CMD_switch:
                        # 解禁手动更新按钮
                        self.console_manual_update_button.setEnabled(True)
                    # 启用CMD重启
                    if self.enable_cmd_reload_CMD_switch:
                        # 解禁重启按钮
                        self.console_reload_button.setEnabled(True)
                    # 启用CMD全屏
                    if self.enable_cmd_full_screen_switch:
                        # 解禁全屏按钮
                        self.console_full_screen_button.setEnabled(True)

                    # 绑定意外退出信号
                    self.select_console.monitor_thread.running_changed.connect(lambda state: self.console_unexpected_exit(self.console_list.currentItem().text(), state, self.select_console))

                    # 关闭控制台激活通知
                    if not self.close_console_activation_tip_switch:
                        InfoBar.success(
                            title="已激活",
                            content=f"控制台 {cmd_name} 已激活",
                            parent=self,
                            position=InfoBarPosition.TOP
                        )
                    # 返回值
                    return True

        except OSError as e: # 捕捉OS报错
            print(e)
            InfoBar.error(
                title="错误",
                content=str(e.strerror), # 转为字符串 防止类型二次崩溃
                parent=self,
                position=InfoBarPosition.TOP
            )
            return False
        except Exception as a:
            print(a)
            InfoBar.error(
                title="错误",
                content=str(a),
                parent=self,
                position=InfoBarPosition.TOP
            )
            return False

    # 开关控制台按钮 关
    def console_off(self):
        try:
            # 控制台列表为空
            if not self.console_list.count() == 0:
                # 关闭当前的控制台
                if self.select_console.finder_thread:
                    self.select_console.finder_thread.stop()
                    self.select_console.finder_thread.wait()
                    self.select_console.finder_thread.deleteLater()
                if self.select_console.monitor_thread:
                    self.select_console.monitor_thread.stop()
                    self.select_console.monitor_thread.wait()
                    self.select_console.monitor_thread.deleteLater()
                if self.select_console.proc:
                    self.select_console.proc.terminate()
                    self.select_console.proc.wait(timeout=1)
                self.select_console.safe_destroy_cmd()  # 完全删除

                # 移出键
                cmd_name = self.console_list.currentItem().text()
                del self.console_obj_dict[cmd_name]

                # 删除项 依据item的行数删除
                self.console_list.takeItem(self.console_list.row(self.console_list.currentItem()))
                self.select_console_item() # 刷新

                # 关闭控制台销毁通知
                if not self.close_console_destroy_tip_switch:
                    InfoBar.info(
                        title="已销毁",
                        content=f"控制台 {cmd_name} 已销毁",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
        except OSError as e: # 捕捉OS报错
            print(e)
            InfoBar.error(
                title="错误",
                content=str(e.strerror), # 转为字符串 防止类型二次崩溃
                parent=self,
                position=InfoBarPosition.TOP
            )
        except Exception as a:
            print(a)
            InfoBar.error(
                title="错误",
                content=str(a),
                parent=self,
                position=InfoBarPosition.TOP
            )

    # 控制台意外退出
    def console_unexpected_exit(self,cmd_name, state,obj):
        try:
            if not state:
                # cmd存在
                if cmd_name in self.console_obj_dict:
                    InfoBar.error(
                        title="意外退出",
                        content=f"控制台 {cmd_name} 意外退出",
                        parent=self,
                        position=InfoBarPosition.TOP,
                        duration=1500
                    )
                    if obj.finder_thread:
                        obj.finder_thread.stop()
                        obj.finder_thread.wait()
                    if obj.monitor_thread:
                        obj.monitor_thread.stop()
                        obj.monitor_thread.wait()
                    if self.select_console.proc:
                        self.select_console.proc.terminate()

                    # 移出键
                    cmd_name = self.console_list.currentItem().text()
                    del self.console_obj_dict[cmd_name]

                    # 删除项 依据item的行数删除
                    self.console_list.takeItem(self.console_list.row(self.console_list.currentItem()))
                    self.select_console_item()  # 刷新

                    # 播放音效 警告音效未禁用
                    if self.play_sound and not self.play_sound_warning:
                        BSP.play("Warning")

        except Exception as a:
            print(a)

    # 选择控制台列表项目
    def select_console_item(self):
        try:
            # 启用手动更新
            if self.enable_manual_update_CMD_switch:
                # 解禁手动更新按钮
                self.console_manual_update_button.setEnabled(True)

            # 启用重启
            if self.enable_cmd_reload_CMD_switch:
                # 解禁手动更新按钮
                self.console_reload_button.setEnabled(True)

            # 启用CMD全屏
            if self.enable_cmd_full_screen_switch:
                # 解禁全屏按钮
                self.console_full_screen_button.setEnabled(True)

            item = self.console_list.currentItem()

            # 存在
            if item:
                if item.text() in self.console_obj_dict:
                    self.console_stackedwidget.setCurrentWidget(self.console_obj_dict[item.text()][1])
                    # 更新当前选择的CMD
                    self.select_console = self.console_obj_dict[item.text()][0]
                    if self.mandatory_update_CMD_switch:
                        # 强制刷新CMD
                        self.select_console.refresh()
            # 如果当前CMD不存在
            else:
                self.console_stackedwidget.setCurrentIndex(0)
                # 禁用手动更新按钮
                self.console_manual_update_button.setEnabled(True)
                # 禁用重启按钮
                self.console_reload_button.setEnabled(True)
                # 禁用全屏按钮
                self.console_full_screen_button.setEnabled(True)
        except Exception as a:
            print(a)

    # 上一个控制台列表项目
    def up_console_item(self):
        try:
            # 有控制台存在
            if self.console_obj_dict != {}:
                # 是否超索引
                if self.console_list.currentRow()-1 >= 0:
                    self.console_list.setCurrentRow(self.console_list.currentRow()-1)
                else:
                    # 重置
                    self.console_list.setCurrentRow(self.console_list.count()-1)
                # 触发槽函数
                self.select_console_item()

                # 关闭控制台切换通知
                if not self.close_console_switch_tip_switch:
                    InfoBar.info(
                        title="提示",
                        content=f"当前所选控制台 {self.console_list.currentItem().text()}",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
        except Exception as a:
            print(a)

    # 下一个控制台列表项目
    def down_console_item(self):
        try:
            # 有控制台存在
            if self.console_obj_dict != {}:
                # 是否超索引
                if not self.console_list.currentRow() >= self.console_list.count()-1:
                    self.console_list.setCurrentRow(self.console_list.currentRow()+1)
                else:
                    # 重置
                    self.console_list.setCurrentRow(0)
                # 触发槽函数
                self.select_console_item()

                # 关闭控制台切换通知
                if not self.close_console_switch_tip_switch:
                    InfoBar.info(
                        title="提示",
                        content=f"当前所选控制台 {self.console_list.currentItem().text()}",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
        except Exception as a:
            print(a)

    # 手动更新控制台
    def manual_update_console(self):
        try:
            self.select_console.refresh()
            InfoBar.success(
                title="完成",
                content=f"控制台强制刷新已完成",
                parent=self,
                position=InfoBarPosition.TOP
            )
        except Exception as a:
            print(a)
            InfoBar.warning(
                title="警告",
                content=f"控制台未激活或被销毁",
                parent=self,
                position=InfoBarPosition.TOP
            )

    # 重启控制台
    def reload_console(self):
        # CMD重启保护
        if self.reload_switch:
            dialog = Dialog("重启提示","重启当前控制台会丢失当前未保存的数据")

            if dialog.exec():
                # 没有控制台存在
                if not self.console_obj_dict != {}:
                    InfoBar.warning(
                        title="警告",
                        content=f"控制台未激活无法重启",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                else:
                    # 执行关闭再开启
                    self.console_off()
                    self.console_on()
        else:
            # 没有控制台存在
            if not self.console_obj_dict != {}:
                InfoBar.warning(
                    title="警告",
                    content=f"控制台未激活无法重启",
                    parent=self,
                    position=InfoBarPosition.TOP
                )
            else:
                # 执行关闭再开启
                self.console_off()
                self.console_on()

    # 全屏控制台
    def full_screen_console(self):

        # CMD全屏保护
        if self.full_screen_switch:
            dialog = Dialog("全屏提示","全屏操作不可逆\n全屏后无法退出全屏状态\n"
                            "并且切换桌面会导致控制台丢失焦点\n如需关闭控制台 输入命令 exit/EXIT 强制退出控制台")

            if dialog.exec():
                try:
                    self.select_console.cmd_full_screen_on()
                except Exception as a:
                    print(a)
                    InfoBar.warning(
                        title="警告",
                        content=f"控制台未激活或被销毁",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
            dialog.accept()
            dialog.deleteLater()
        else:
            try:
                self.select_console.cmd_full_screen_on()
            except Exception as a:
                print(a)
                InfoBar.warning(
                    title="警告",
                    content=f"控制台未激活或被销毁",
                    parent=self,
                    position=InfoBarPosition.TOP
                )

    # 更新主题模式
    def update_theme_model(self, theme):
        try:
            theme_name = (self.theme_map[theme])
            setTheme(tool.str_to_theme(theme_name),lazy=self.lazy)
            JCP.update("config.json", ["setting","theme_model"], theme_name)
            self.theme_model = theme_name
            self.theme_color_auto = JCP.get("config.json", ["setting","theme_color_auto"],True)
            if self.theme_color_auto:
                if self.theme_model == "DARK":  # 暗
                    self.select_color_button.setColor(QColor("#ff29f1ff"))
                    JCP.update("config.json", ["setting","theme_color"], "#ff29f1ff")
                    self.hyperlink_file_label.set_text_color("#ff29f1ff")
                elif self.theme_model == "LIGHT":  # 亮
                    self.select_color_button.setColor(QColor("#ff009faa"))
                    JCP.update("config.json", ["setting","theme_color"], "#ff009faa")
                    self.hyperlink_file_label.set_text_color("#ff009faa")
                elif self.theme_model == "AUTO":  # 自动
                    current_theme = darkdetect.theme()  # 获取系统主题
                    if current_theme == 'Dark':
                        self.select_color_button.setColor(QColor("#ff29f1ff"))
                        JCP.update("config.json", ["setting","theme_color"], "#ff29f1ff")
                        self.hyperlink_file_label.set_text_color("#ff29f1ff")
                    if current_theme == 'Light':
                        self.select_color_button.setColor(QColor("#ff009faa"))
                        JCP.update("config.json", ["setting","theme_color"], "#ff009faa")
                        self.hyperlink_file_label.set_text_color("#ff009faa")

        except Exception as a:
            print(a)

    # 更新主题强调色
    def update_theme_color(self, color):
        try:
            setThemeColor(color,lazy=self.lazy)
            JCP.update("config.json", ["setting","theme_color"], color)
            JCP.update("config.json", ["setting","theme_color_auto"], False)
            self.theme_color = color
            self.hyperlink_file_label.set_text_color(color)

            # 不处在隐藏
            if self.downloadBadge.text() != "":
                # 更新背景颜色 强制使用强调色
                self.downloadBadge.setCustomBackgroundColor(self.theme_color, self.theme_color)
        except Exception as a:
            print(a)

    # 恢复默认强调色
    def restore_default_color(self):
        try:
            content = """黑暗主题模式下换回 十六进制颜色代码#ff29f1ff
            明亮主题模式下换回 十六进制颜色代码#ff009faa
            并切换回自动强调色模式 随主题模式切换"""

            w = Dialog('确认恢复主题默认强调色？', content, self)

            if w.exec():
                if self.theme_model == "DARK":  # 暗
                    self.theme_color = "#ff29f1ff"

                elif self.theme_model == "LIGHT":  # 亮
                    self.theme_color = "#ff009faa"

                elif self.theme_model == "AUTO":  # 自动
                    current_theme = darkdetect.theme()  # 获取系统主题
                    if current_theme == 'Dark':
                        self.theme_color = "#ff29f1ff"

                    if current_theme == 'Light':
                        self.theme_color = "#ff009faa"

                setThemeColor(QColor(self.theme_color),lazy=self.lazy)
                JCP.update("config.json", ["setting","theme_color"], self.theme_color)
                self.select_color_button.setColor(QColor(self.theme_color))
                self.hyperlink_file_label.set_text_color(self.theme_color)

                # 徽章不处在隐藏
                if self.downloadBadge.text() != "":
                    # 更新背景颜色 强制使用强调色
                    self.downloadBadge.setCustomBackgroundColor(self.theme_color, self.theme_color)

                InfoBar.success(
                    title="完成",
                    content="默认颜色已恢复",
                    parent=self,
                    position=InfoBarPosition.TOP
                )

                JCP.update("config.json", ["setting","theme_color_auto"], True)
        except Exception as a:
            print(a)

    # 切换堆叠创建窗口
    def created_stacked_update(self,page):
        if page == "虚拟环境":
            self.created_stacked.setCurrentIndex(0)
        elif page == "便携式环境":
            self.created_stacked.setCurrentIndex(1)
        elif page == "基础环境":
            self.created_stacked.setCurrentIndex(2)
        elif page == "配置文件":
            self.created_stacked.setCurrentIndex(3)
        elif page == "预设脚本":
            self.created_stacked.setCurrentIndex(4)
        elif page == "图钉":
            self.created_stacked.setCurrentIndex(5)

    # 切换分段创建虚拟环境窗口
    def segmented_stacked_update(self,page):
        if page == "现有":
            self.segmented_venv_stacked.setCurrentIndex(0)
        if page == "新建":
            self.segmented_venv_stacked.setCurrentIndex(1)
        if page == "配置":
            self.segmented_venv_stacked.setCurrentIndex(2)

    # 获取python版本
    @staticmethod
    def get_python_version_by_cmd(python_exe: str):
        try:
            out = subprocess.check_output(
                [python_exe, "--version"],
                stderr=subprocess.STDOUT,
                text=True,
                timeout=2
            )
            return out.strip()
        except Exception:
            return "未知"

    # 打开添加基础环境窗口
    def open_add_python_window(self):
        python_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 Python 解释器",
            "C:/",
            "Python Executable (python.exe pythonw.exe);;"
            "All Files (*.*)"
        )
        if python_path != '':
            self.add_python_path_line.setText(python_path)

    # 添加基础环境
    def add_python(self):
        # 判断路径是否存在
        path = self.add_python_path_line.text()
        if os.path.exists(path):
            name = Path(path).name.lower()
            if "python" in name and name.endswith(".exe"):

                # 获取python版本
                python_v = self.get_python_version_by_cmd(path)
                JCP.update(
                    "config.json",
                    ["python",os.path.dirname(path)],
                    {
                        "name": python_v, # 名称
                        "path": path, # 解释器路径
                        "dir": os.path.dirname(path), # 解释器目录
                        "version": python_v[7:] # 版本
                    }
                )
                self.add_python_path_line.setText("")
                InfoBar.success(
                    title="成功",
                    content=f"基础环境 {python_v} 添加成功",
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                self.update_python() # 刷新基础环境

        else:
            InfoBar.error(
                title="错误",
                content="基础解释器不存在",
                parent=self,
                position=InfoBarPosition.TOP
            )

    # 打开添加虚拟环境窗口
    def open_add_venv_window(self):
        python_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 VENV 虚拟环境",
            "C:/",
            "Python Virtual Environment (pyvenv.cfg);;"
            "All Files (*.*)"
        )
        if python_path != '':
            self.venv_dir_line.setText(python_path)
            self.venv_dir_name.setText(os.path.basename(os.path.dirname(python_path)))
            self.start_parameter_line.setText(os.path.dirname(python_path)+"/Scripts/activate")

    # cfg解析器
    @staticmethod
    def cfg_parser(file_path):
        config_dict = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释行
                    if not line or line.startswith('#') or line.startswith(';'):
                        continue

                    # 分割键和值，只分割第一个 '='
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config_dict[key.strip()] = value.strip()
        except FileNotFoundError:
            print(f"文件不存在: {file_path}")

        return config_dict

    # 添加虚拟环境
    def add_venv(self):
        try:
            # 判断文件是否存在
            path = self.venv_dir_line.text()
            if os.path.exists(path):
                cfg = self.cfg_parser(path) # 获取cfg
                dir_path = os.path.dirname(path)
                JCP.update(
                    "config.json",
                    ["venv",dir_path],
                    {
                        "name": self.venv_dir_name.text(), # 名称
                        "python": cfg["home"]+"\\python.exe", # 基础解释器
                        "cfg_file": path, # cfg配置文件
                        "dir": dir_path, # venv目录
                        "start_parameter": self.start_parameter_line.text(),# 启动参数
                        "include-system-site-packages": tool.str_to_bool(cfg["include-system-site-packages"]),# 全局开关
                        "version": cfg["version"] # 版本
                    }
                )
                self.venv_dir_line.setText("")
                self.start_parameter_line.setText("")
                self.venv_dir_name.setText("")
                InfoBar.success(
                    title="成功",
                    content=f"虚拟环境 {self.venv_dir_name.text()} 添加成功",
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                self.update_venv() # 刷新虚拟环境

            else:
                InfoBar.error(
                    title="错误",
                    content="虚拟环境配置文件不存在",
                    parent=self,
                    position=InfoBarPosition.TOP
                )
        except Exception as a:
            print(a)

    # 添加跳转
    def add_jump(self,model):
        self.stackedWidget.setCurrentWidget(self.Created)  # 跳转创建
        if model == "python":
            self.create_navigation.setCurrentItem('基础环境')# 创建基础环境页
        elif model == "emb":
            self.create_navigation.setCurrentItem('便携式环境')
        elif model == "venv":
            self.create_navigation.setCurrentItem('虚拟环境')
        elif model == "preset":
            self.create_navigation.setCurrentItem('预设脚本')
        elif model == "config":
            self.create_navigation.setCurrentItem('配置文件')
        elif model == "pin":
            self.create_navigation.setCurrentItem('图钉')

    # 添加配置命令
    def add_config_older(self):
        text = self.add_config_older_line.text()
        if text != "":
            self.add_config_older_line.setText("")

            # 创建新项
            self.config_older_list.append(text)
            self.config_older_number += 1
            self.card_config_older_text.append(f"{self.config_older_number}  {text}")
            self.one_older_max_label.setText("0/4000")
        else:
            InfoBar.warning(
                title="警告",
                content="命令不能为空",
                parent=self,
                position=InfoBarPosition.TOP
            )

    # 创建配置命令
    def create_config(self):
        name = self.add_config_name_line.text()
        older_list = self.config_older_list
        if name != "" and older_list != []:
            JCP.update(
                "config.json",
                ["config",name],
                {
                    "name": name,  # 名称
                    "older_list": older_list  # 命令列表
                }
            )

            InfoBar.success(
                title="成功",
                content=f"配置文件 {name} 添加成功",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.reset_config_older() # 重置
            self.update_config() # 更新
        elif name != "" and older_list == []:
            InfoBar.warning(
                title="警告",
                content="命令不能为空",
                parent=self,
                position=InfoBarPosition.TOP
            )
        else:
            InfoBar.warning(
                title="警告",
                content="名称不能为空",
                parent=self,
                position=InfoBarPosition.TOP
            )

    # 重置配置命令
    def reset_config_older(self):
        self.config_older_number = 0
        self.config_older_list = []
        self.one_older_max_label.setText("0/4000")
        self.add_config_name_line.setText("")
        self.add_config_older_line.setText("")
        self.card_config_older_text.clear()

    # 创建预设脚本
    def create_preset_scripts(self):
        if self.preset_scripts_name_line.text() == "": # 名称为空
            InfoBar.warning(
                title="警告",
                content="名称不能为空",
                parent=self,
                position=InfoBarPosition.TOP
            )
        elif self.preset_scripts_line.text() == "": # 命令为空
            InfoBar.warning(
                title="警告",
                content="命令不能为空",
                parent=self,
                position=InfoBarPosition.TOP
            )
        elif self.preset_scripts_dict == {}: # 参数为空
            InfoBar.warning(
                title="警告",
                content="缺失重要参数 %",
                parent=self,
                position=InfoBarPosition.TOP
            )
        elif not self.switch_preset_scripts_max_bool: # 命令超上限
            InfoBar.warning(
                title="警告",
                content="命令超过最大上限",
                parent=self,
                position=InfoBarPosition.TOP
            )
        else: # 全部满足
            name = self.preset_scripts_name_line.text()
            # 使用默认描述
            description = self.preset_scripts_description_line.placeholderText()
            # 如果不为空再使用新描述
            if self.preset_scripts_description_line.text() != "":
                description = self.preset_scripts_description_line.text()
            JCP.update(
                "config.json",
                ["preset_scripts",name],
                {
                    "name": name,  # 名称
                    "description": description, # 描述
                    "older": self.preset_scripts_line.text(), # 命令
                    "parameters_dict": self.preset_scripts_dict # 参数字典
                }
            )
            InfoBar.success(
                title="成功",
                content=f"预设文件 {name} 添加成功",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.reset_preset_scripts() # 重置
            self.update_preset_scripts() # 更新

    # 重置预设脚本
    def reset_preset_scripts(self):
        self.preset_scripts_description_line.setText("")
        self.preset_scripts_name_line.setText("")
        self.preset_scripts_line.setText("")
        while self.preset_scripts_layout.count():
            item = self.preset_scripts_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.preset_scripts_layout.addWidget(BodyLabel(f"所需0个参数")) # 默认文本

    # 创建图钉
    def create_pin_comm(self):
        comm = self.pin_comm_line.text()
        if comm == "":  # 命令为空
            InfoBar.warning(
                title="警告",
                content="命令不能为空",
                parent=self,
                position=InfoBarPosition.TOP
            )
        elif not self.switch_pin_comm_max_bool:  # 命令超上限
            InfoBar.warning(
                title="警告",
                content="命令超过最大上限",
                parent=self,
                position=InfoBarPosition.TOP
            )
        else: # 全部满足
            JCP.append("config.json",["pin"],comm)
            InfoBar.success(
                title="成功",
                content=f"图钉 {comm} 添加成功",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.reset_pin_comm() # 重置
            self.pin_list.itemClicked.disconnect() # 断开全部信号
            self.update_pin() # 更新图钉

    # 重置图钉
    def reset_pin_comm(self):
        self.pin_comm_line.setText("")
        self.pin_comm_one_older_max_label.setText("0/1000")

    # 弹出预设
    def flyout_reset_scripts(self):
        try:
            file_datas = JCP.get("config.json",["preset_scripts"])
            key = file_datas.keys()

            view = FlyoutView(
                title='预设脚本',
                content="选择预设并填充占位符变量 进行快速命令调用",
                isClosable=True
            )
            listwidget = ListWidget()
            listwidget.setFixedWidth(400)
            for k in key:
                item = QListWidgetItem(file_datas[k]["name"]) # 使用名称 而非内部码
                item.setData(Qt.UserRole,file_datas[k])

                listwidget.addItem(item)
            listwidget.currentItemChanged.connect(self.quick_command)

            view.setFixedHeight(300)
            view.addWidget(listwidget)

            w = Flyout.make(view, self.preset_scripts_button, self,aniType=FlyoutAnimationType.DROP_DOWN)
            view.closed.connect(w.close)
        except Exception as a:
            print(a)

    # 弹出快速命令
    def quick_command(self,item):
        try:
            name = item.data(Qt.UserRole)["name"] # 名称
            description = item.data(Qt.UserRole)["description"] # 描述
            older = item.data(Qt.UserRole)["older"] # 命令
            parameters_dict = item.data(Qt.UserRole)["parameters_dict"] # 参数字典
            parameters_num = len(parameters_dict) # 参数数量

            dialog = QuickCommandDialog("快速命令",f"预设 {name} 所需 {parameters_num} 个参数",self)

            dialog.description_label.setText("描述:"+description)
            dialog.older_label.setText("原始命令:"+older)

            # 清空命令对象列表
            self.order_obj_list = []
            # 命令占位符列表
            self.order_placeholders_list = []
            # 命令映射表
            self.order_mapping_dict = {}

            for i in parameters_dict:
                layout = QHBoxLayout()
                label = BodyLabel(i + ":")
                label.setMaximumWidth(50)
                layout.addWidget(label)
                line_edit = LineEdit()
                line_edit.setPlaceholderText(parameters_dict[i])
                layout.addWidget(line_edit)
                self.order_obj_list.append(line_edit)
                self.order_placeholders_list.append(i)
                dialog.scrollArea_card_layout.addLayout(layout)
            dialog.adjustSize() # 强制刷新
            dialog.setMinimumWidth(500) # 重新固定宽度

            # 空命令计数
            comm_none_num = 0

            # 组合命令
            if dialog.exec():
                # 记录空计数
                for i in self.order_obj_list:
                    if i.text() == "":
                        comm_none_num += 1
                # 存在空参数
                if comm_none_num != 0:
                    InfoBar.error(
                        title="应用失败",
                        content=f"存在{comm_none_num}个空参数",
                        parent=self,
                        position=InfoBarPosition.TOP,
                        duration=1500
                    )
                else:
                    # 组合参数
                    try:
                        # 组合映射表 遍历双列表
                        for i,j in zip(self.order_placeholders_list,self.order_obj_list):
                            self.order_mapping_dict[i] = j.text()
                        # 更新命令
                        comm = tool.replace_placeholders_regex(older,self.order_mapping_dict)
                        self.select_cmd.send_command(comm)
                    except pywintypes.error as e:
                        if e.winerror == 1816:
                            print(e)
                            InfoBar.warning(
                                title="警告",
                                content=f"配额不足 无法处理此命令",
                                parent=self,
                                position=InfoBarPosition.TOP
                            )
                    except Exception as a:
                        print(a)
                        InfoBar.warning(
                            title="警告",
                            content=f"CMD未开机或被销毁",
                            parent=self,
                            position=InfoBarPosition.TOP
                        )
        except Exception as a:
            print(a)

    # 手动更新CMD
    def manual_update_CMD(self):
        try:
            self.select_cmd.refresh()
            InfoBar.success(
                title="完成",
                content=f"CMD强制刷新已完成",
                parent=self,
                position=InfoBarPosition.TOP
            )
        except Exception as a:
            print(a)
            InfoBar.warning(
                title="警告",
                content=f"CMD未开机或被销毁",
                parent=self,
                position=InfoBarPosition.TOP
            )

    # 全屏CMD
    def full_screen_CMD(self):

        # CMD全屏保护
        if self.full_screen_switch:
            dialog = Dialog("全屏提示","全屏操作不可逆\n全屏后无法退出全屏状态\n"
                            "并且切换桌面会导致CMD丢失焦点\n如需关闭CMD 输入命令 exit/EXIT 强制退出CMD")

            if dialog.exec():
                try:
                    self.select_cmd.cmd_full_screen_on()
                except Exception as a:
                    print(a)
                    InfoBar.warning(
                        title="警告",
                        content=f"CMD未开机或被销毁",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
            dialog.accept()
            dialog.deleteLater()
        else:
            try:
                self.select_cmd.cmd_full_screen_on()
            except Exception as a:
                print(a)
                InfoBar.warning(
                    title="警告",
                    content=f"CMD未开机或被销毁",
                    parent=self,
                    position=InfoBarPosition.TOP
                )

    # 重启CMD
    def reload_CMD(self):

        # CMD重启保护
        if self.reload_switch:
            dialog = Dialog("重启提示","重启当前CMD会丢失当前未保存的数据")

            if dialog.exec():
                item = self.venv_tree.currentItem()
                # 按钮状态是开机 并且选中不为空
                if self.switch_power_bool is True and item is not None:
                    InfoBar.warning(
                        title="警告",
                        content=f"CMD未开机无法重启",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                elif self.switch_power_bool is False and item is not None:
                    # 执行两次电源
                    self.power_on_off()
                    self.power_on_off()
        else:
            item = self.venv_tree.currentItem()
            # 按钮状态是开机 并且选中不为空
            if self.switch_power_bool is True and item is not None:
                InfoBar.warning(
                    title="警告",
                    content=f"CMD未开机无法重启",
                    parent=self,
                    position=InfoBarPosition.TOP
                )
            elif self.switch_power_bool is False and item is not None:
                # 执行两次电源
                self.power_on_off()
                self.power_on_off()


    # 打开添加便携式环境窗口
    def open_add_emb_window(self):
        python_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 EMB 嵌入包",
            "C:/",
            "Python Embeddable (*.zip);;"
            "All Files (*.*)"
        )
        if python_path != '':
            self.add_emb_path_line.setText(python_path)

    # 打开添加get-pip窗口
    def open_add_get_pip_window(self):
        python_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 get-pip.py 引导脚本",
            "C:/",
            "Python get-pip.py (*.py);;"
            "All Files (*.*)"
        )
        if python_path != '':
            self.custom_install_pip_line.setText(python_path)

    # 解锁PTH动态禁用
    def unlock_pth_dynamic_disabled(self,s):
        # 一并禁用
        # 如果禁用时被禁用复选框需禁用控件
        if self.custom_pip_acquisition_box.isChecked():
            # 禁用他所需禁用的控件并设置状态
            self.custom_pip_acquisition_box.setChecked(False)
            self.custom_pip_acquisition_line.setEnabled(False)

        if self.custom_install_pip_box.isChecked():
            self.custom_install_pip_box.setChecked(False)
            self.custom_install_pip_line.setEnabled(False)
            self.custom_install_pip_path_button.setEnabled(False)

        if self.automatically_obtain_install_pip_box.isChecked():
            self.automatically_obtain_install_pip_box.setChecked(False)

        self.custom_pip_acquisition_box.setEnabled(s)
        self.custom_install_pip_box.setEnabled(s)

        self.automatically_obtain_install_pip_box.setEnabled(s)

    # 自动获取动态禁用
    def automatic_acquisition_dynamic_disabled(self,s):
        # 一并禁用
        twist_s = not s # bool反转
        # 如果禁用时被禁用复选框需禁用控件
        if self.custom_pip_acquisition_box.isChecked():
            # 禁用他所需禁用的控件并设置状态
            self.custom_pip_acquisition_box.setChecked(False)
            self.custom_pip_acquisition_line.setEnabled(False)

        if self.custom_install_pip_box.isChecked():
            self.custom_install_pip_box.setChecked(False)
            self.custom_install_pip_line.setEnabled(False)
            self.custom_install_pip_path_button.setEnabled(False)

        self.custom_pip_acquisition_box.setEnabled(twist_s)
        self.custom_install_pip_box.setEnabled(twist_s)

    # 自定义获取动态禁用
    def custom_get_dynamic_disabled(self,s):
        # 一并禁用
        self.custom_pip_acquisition_line.setEnabled(s)

        if not s and not self.custom_install_pip_box.isChecked(): # 同时取消勾选
            self.automatically_obtain_install_pip_box.setEnabled(not s) # 启用
        elif s:
            self.automatically_obtain_install_pip_box.setEnabled(not s) # 禁用

        if self.automatically_obtain_install_pip_box.isChecked():
            self.automatically_obtain_install_pip_box.setChecked(False)

    # 自定义下载动态禁用
    def custom_install_dynamic_disabled(self,s):
        # 一并禁用
        self.custom_install_pip_line.setEnabled(s)
        self.custom_install_pip_path_button.setEnabled(s)

        if not s and not self.custom_pip_acquisition_box.isChecked(): # 同时取消勾选
            self.automatically_obtain_install_pip_box.setEnabled(not s) # 启用
        elif s:
            self.automatically_obtain_install_pip_box.setEnabled(not s) # 禁用

        if self.automatically_obtain_install_pip_box.isChecked():
            self.automatically_obtain_install_pip_box.setChecked(False)

    # CMD创建动态禁用
    def CMD_dynamic_disabled(self,s):
        self.creat_CMD_open_box.setEnabled(s)

        if not s:
            self.creat_CMD_open_box.setChecked(False)

    # 使用外部CMD创建动态禁用
    def use_ext_CMD_dynamic_disabled(self,s):
        self.config_keep_CMD_open_after_creation_box.setEnabled(s)

        if not s:
            self.config_keep_CMD_open_after_creation_box.setChecked(False)

    # 打开安装便携式环境窗口
    def open_install_emb_window(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "选择 安装位置",
            "C:/"
        )

        if path != '':
            dir_path = "python-embed"  # 默认文件夹
            if self.add_emb_path_line.text() == "":
                if path.endswith("/") or path.endswith("\\"): # 以/\结尾
                    self.add_emb_install_path_line.setText(path+dir_path)
                else:
                    self.add_emb_install_path_line.setText(path+"/"+dir_path)
            else:
                dir_path, ext = os.path.splitext(os.path.basename(self.add_emb_path_line.text()))  # 嵌入包存在则使用嵌入包名
                if path.endswith("/") or path.endswith("\\"): # 以/\结尾
                    self.add_emb_install_path_line.setText(path+dir_path)
                else:
                    self.add_emb_install_path_line.setText(path+"/"+dir_path)

    # 便携式环境解包
    def emb_unpack(self):
        zip_path = self.add_emb_path_line.text()
        out_path = self.add_emb_install_path_line.text()
        if os.path.exists(zip_path):
            try:
                # 安装路径是否为空
                if out_path == "":
                    InfoBar.error(
                        title="错误",
                        content=f"安装路径不能为空",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                elif not is_valid_filepath(out_path, platform="windows"):
                    InfoBar.error(
                        title="错误",
                        content=f"安装路径不合规",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                elif not os.path.exists(os.path.dirname(out_path)):
                    InfoBar.error(
                        title="错误",
                        content=f"安装路径父目录不存在",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                # 安装路径合规
                else:
                    # 解析嵌入包
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        # 列出所有文件名
                        file_list = zip_ref.namelist()
                        # 获取总文件数量
                        num = len([name for name in zip_ref.namelist() if not name.endswith("/")])
                    # 是嵌入包
                    if "python.exe" in file_list or "pythonw.exe" in file_list:
                        dialog = ProgressRingDialog("解包中...", num,self)
                        dialog.show()
                        self.zip_thread = UnzipWorker(zip_path,out_path) # 异步操作改为成员对象
                        self.zip_thread.progress.connect(lambda x:dialog.set_num(x))
                        self.zip_thread.finished.connect(lambda :self.unpacking_complete(dialog,self.zip_thread))
                        self.zip_thread.error.connect(lambda x:self.unpacking_error(x,dialog,self.zip_thread))
                        self.zip_thread.start()
                    else:
                        InfoBar.error(
                            title="错误",
                            content=f"该zip不是Python嵌入包",
                            parent=self,
                            position=InfoBarPosition.TOP
                        )
            except Exception as a:
                print(a)
                InfoBar.error(
                    title="错误",
                    content=f"无法解析该嵌入包 可能丢失或被损坏",
                    parent=self,
                    position=InfoBarPosition.TOP,
                    duration=1500
                )
        else:
            InfoBar.error(
                title="错误",
                content=f"嵌入包不存在",
                parent=self,
                position=InfoBarPosition.TOP
            )

    # 解包完成
    def unpacking_complete(self,dialog,thread):
        dialog.accept()
        dialog.deleteLater()
        InfoBar.success(
            title="完成",
            content=f"解包完成",
            parent=self,
            position=InfoBarPosition.TOP
        )
        thread.deleteLater()
        self.reset_emb() # 重置
        self.update_emb()  # 更新便携式环境
        # 播放音效 操作完成音效未禁用
        if self.play_sound and not self.play_sound_operation_completed:
            BSP.play("OperationCompleted")

    # 解包错误
    def unpacking_error(self,text,dialog,thread):
        dialog.accept()
        dialog.deleteLater()
        InfoBar.error(
            title="错误",
            content=text,
            parent=self,
            position=InfoBarPosition.TOP,
            duration=1500
        )
        thread.deleteLater()

    # 重置创建便携式环境
    def reset_emb(self):
        self.add_emb_path_line.setText("")
        self.add_emb_install_path_line.setText("")

        self.unlock_library_box.setChecked(False)
        self.create_startup_script_box.setChecked(False)
        self.creat_CMD_box.setChecked(False)
        self.creat_CMD_open_box.setChecked(False)
        self.automatically_obtain_install_pip_box.setChecked(False)
        self.custom_pip_acquisition_box.setChecked(False)
        self.custom_install_pip_box.setChecked(False)

        self.custom_pip_acquisition_line.setText(f'curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py')
        self.custom_install_pip_line.setText("")

    # 解包并激活便携式环境
    def unpack_activate_emb(self):
        zip_path = self.add_emb_path_line.text()
        out_path = self.add_emb_install_path_line.text()
        # 解包
        if os.path.exists(zip_path):
            try:
                # 安装路径是否为空
                if out_path == "":
                    InfoBar.error(
                        title="错误",
                        content=f"安装路径不能为空",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                elif not is_valid_filepath(out_path, platform="windows"):
                    InfoBar.error(
                        title="错误",
                        content=f"安装路径不合规",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                elif not os.path.exists(os.path.dirname(out_path)):
                    InfoBar.error(
                        title="错误",
                        content=f"安装路径父目录不存在",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                # 后续检查
                # 自定义获取pip存在 命令不规范 低延时操作
                elif "自定义获取pip" in self.emb_batch_set and not tool.is_valid_get_pip_source_re(self.custom_pip_acquisition_line.text()):
                    InfoBar.error(
                        title="错误",
                        content=f"命令不规范 非法命令",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                # 自定义获取pip存在 文件不存在
                elif "自定义安装pip" in self.emb_batch_set and not os.path.exists(self.custom_install_pip_line.text()):
                    InfoBar.error(
                        title="错误",
                        content=f"引导脚本不存在",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                # 安装路径合规
                else:
                    # 关闭脱控通知
                    if not self.close_emb_out_control_notification_switch:
                        w = NotificationDialog(
                            title='通知',
                            content=f"创建后 Emb会脱离VEM 但VEM仍会记录Emb位置\n"
                                    f"如需继续手动控制Emb 勾选[创建启动脚本] 将在Emb目录外生成 python.dat 用于快速进入环境\n\n"
                                    f"如需在创建时关闭此通知\n"
                                    f"👉设置-通知-关闭便携式环境的脱控通知",
                            parent=self
                        )
                        w.exec()

                    # 解析嵌入包
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        # 列出所有文件名
                        file_list = zip_ref.namelist()
                    # 是嵌入包
                    if "python.exe" in file_list or "pythonw.exe" in file_list:
                        dialog = ByteProgressRingDialog("快速解包中...",self)
                        dialog.show()
                        self.zip_byte_thread = UnzipWorkerByte(zip_path,out_path) # 异步操作改为成员对象
                        self.zip_byte_thread.progress.connect(lambda cur, tot:dialog.set_num(cur,tot))
                        self.zip_byte_thread.finished.connect(lambda :self.unpacking_complete_byte(dialog,self.zip_byte_thread))
                        self.zip_byte_thread.error.connect(lambda x:self.unpacking_error(x,dialog,self.zip_byte_thread))
                        self.zip_byte_thread.start()
                    else:
                        InfoBar.error(
                            title="错误",
                            content=f"该zip不是Python嵌入包",
                            parent=self,
                            position=InfoBarPosition.TOP
                        )
            except Exception as a:
                print(a)
                InfoBar.error(
                    title="错误",
                    content=f"无法解析该嵌入包 可能丢失或被损坏",
                    parent=self,
                    position=InfoBarPosition.TOP,
                    duration=1500
                )
        else:
            InfoBar.error(
                title="错误",
                content=f"嵌入包不存在",
                parent=self,
                position=InfoBarPosition.TOP
            )

    # 解包完成 激活并执行
    def unpacking_complete_byte(self,dialog,thread):
        dialog.accept()
        dialog.deleteLater()
        thread.deleteLater()
        # 不是空集合 存在批处理
        if self.emb_batch_set:
            # 重置通知和内容
            self.emb_notification = False
            self.emb_notification_text = ''
            # 不确定进度环
            Indeterminate_dialog = IndeterminateProgressRingDialog("执行批处理任务...",self)
            Indeterminate_dialog.show()
            # 执行EMB批处理
            self.emb_thread_batch_processing = Threads.EmbBatchProcessing(self.emb_batch_set,
                                                                          self.add_emb_install_path_line.text(),
                                                                          self.custom_pip_acquisition_line.text(),
                                                                          self.custom_install_pip_line.text())
            self.emb_thread_batch_processing.finished.connect(lambda :self.emb_batch_processing_end(Indeterminate_dialog))
            self.emb_thread_batch_processing.emb_dir.connect(lambda emb:self.update_emb_notification(emb))
            self.emb_thread_batch_processing.update_title.connect(lambda title:Indeterminate_dialog.label.setText(title))
            self.emb_thread_batch_processing.error.connect(lambda err:InfoBar.success(title="错误",content=err,parent=self,position=InfoBarPosition.TOP))
            self.emb_thread_batch_processing.start()
        # 空集合 解包完成
        else:
            dir_path = self.add_emb_install_path_line.text()
            base_path = os.path.basename(dir_path)
            python_v = self.get_python_version_by_cmd(dir_path+"/python.exe")
            # 添加到配置
            JCP.update(
                "config.json",
                ["emb",dir_path],
                {
                    "name": base_path, # 名称
                    "dir": dir_path, # emb目录
                    "pth": False,# 是否解锁第三方库
                    'start_script': False, # 启动脚本路径
                    "version": python_v[7:] # 版本
                }
            )
            InfoBar.success(
                title="完成",
                content=f"解包完成",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.reset_emb()  # 重置
            self.update_emb() # 更新便携式环境
            # 播放音效 操作完成音效未禁用
            if self.play_sound and not self.play_sound_operation_completed:
                BSP.play("OperationCompleted")

    # 便携式环境批处理队列
    def emb_batch(self,text, checked):
        if checked:
            self.emb_batch_set.add(text)
        else:
            self.emb_batch_set.discard(text)

    # EMB批处理完成
    def emb_batch_processing_end(self,dialog):
        try:
            # 清理
            dialog.accept()
            dialog.deleteLater()
            self.emb_thread_batch_processing.deleteLater()

            dir_path = self.add_emb_install_path_line.text()
            python_v = self.get_python_version_by_cmd(dir_path+"/python.exe")
            script_path = False # 默认没启动脚本
            if self.create_startup_script_box.isChecked(): # 启动脚本路径
                script_path = self.emb_notification_text
            # 添加到配置
            JCP.update(
                "config.json",
                ["emb",dir_path],
                {
                    "name": python_v, # 名称
                    "dir": dir_path, # emb目录
                    "pth": self.unlock_library_box.isChecked(),# 是否解锁第三方库
                    'start_script': script_path, # 启动脚本路径
                    "version": python_v[7:] # 版本
                }
            )
            InfoBar.success(
                title="完成",
                content=f"便携式环境创建完成",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )

            self.reset_emb() # 重置
            self.update_emb() # 更新便携式环境

            # 播放音效 操作完成音效未禁用
            if self.play_sound and not self.play_sound_operation_completed:
                BSP.play("OperationCompleted")

            # EMB通知
            if self.emb_notification:
                w = NotificationDialog(
                    title='通知',
                    content=f"启动脚本 python.bat 已经创建在 {self.emb_notification_text}",
                    parent=self
                )
                w.exec()
        except Exception as a:
            print(a)

    # 更新EMB通知
    def update_emb_notification(self,emb):
        self.emb_notification = True
        self.emb_notification_text = emb

    # 初始化菜单
    def init_menu(self):
        # 图钉列表菜单
        self.pin_list_menu = RoundMenu(parent=self.pin_list)
        self.pin_list_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_row(self.pin_list)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_pin),
            Action(FluentIcon.EDIT, '编辑命令', triggered=self.edit_pin_list_name),
            Action(FluentIcon.ADD, '创建图钉', triggered=lambda: self.add_jump("pin")),
            Action(FluentIcon.DELETE, '删除', triggered=self.delete_pin_list)
        ])
        # 环境树树枝菜单
        self.venv_tree_branch_menu = RoundMenu(parent=self.venv_tree)
        self.venv_tree_branch_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_tree_row(self.venv_tree)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_venv_tree),
            Action(MetaverseFluentIcon.Up, '收起', triggered=lambda: self.venv_tree.currentItem().setExpanded(False)),
            Action(MetaverseFluentIcon.Down, '展开', triggered=lambda: self.venv_tree.currentItem().setExpanded(True))
        ])
        # 环境树虚拟环境菜单
        self.venv_tree_venv_menu = RoundMenu(parent=self.venv_tree)
        self.venv_tree_venv_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_tree_row(self.venv_tree)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_venv_tree),
            Action(FluentIcon.POWER_BUTTON, '电源', triggered=self.power_on_off),
            Action(FluentIcon.ADD, '创建', triggered=lambda: self.add_jump("venv")),
            Action(FluentIcon.APPLICATION, '管理', triggered=lambda :self.stackedWidget.setCurrentWidget(self.Venv))
        ])
        # 环境树便携式环境菜单
        self.venv_tree_emb_menu = RoundMenu(parent=self.venv_tree)
        self.venv_tree_emb_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_tree_row(self.venv_tree)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_venv_tree),
            Action(FluentIcon.ADD, '创建', triggered=lambda: self.add_jump("emb")),
            Action(FluentIcon.APPLICATION, '管理', triggered=lambda :self.stackedWidget.setCurrentWidget(self.EmbEnv))
        ])
        # 环境树基础环境菜单
        self.venv_tree_python_menu = RoundMenu(parent=self.venv_tree)
        self.venv_tree_python_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_tree_row(self.venv_tree)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_venv_tree),
            Action(FluentIcon.ADD, '创建', triggered=lambda: self.add_jump("python")),
            Action(FluentIcon.APPLICATION, '管理', triggered=lambda :self.stackedWidget.setCurrentWidget(self.BaseEnv))
        ])

        # python环境表格菜单
        self.python_table_menu = RoundMenu(parent=self.python_table)
        self.python_table_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_row(self.python_table)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_python),
            Action(FluentIcon.EDIT, '编辑名称', triggered=self.edit_python_name),
            Action(FluentIcon.ADD, '创建环境', triggered=lambda: self.add_jump("python")),
            Action(FluentIcon.DELETE, '删除条目', triggered=self.delete_python)
        ])
        # 添加分割线
        self.python_table_menu.addSeparator()
        self.python_table_menu.addAction(Action(FluentIcon.INFO, '详情', triggered=self.details_python))
        self.python_table_menu.addAction(Action('全选', shortcut='Ctrl+A', triggered=self.python_table.selectAll))

        # emb环境表格菜单
        self.emb_table_menu = RoundMenu(parent=self.emb_table)
        self.emb_table_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_row(self.emb_table)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_emb),
            Action(FluentIcon.ADD, '创建环境', triggered=lambda: self.add_jump("emb")),
            Action(FluentIcon.DELETE, '删除条目', triggered=self.delete_emb)
        ])
        # 添加分割线
        self.emb_table_menu.addSeparator()
        self.emb_table_menu.addAction(Action(FluentIcon.INFO, '详情', triggered=self.details_emb))
        self.emb_table_menu.addAction(Action('全选', shortcut='Ctrl+A', triggered=self.emb_table.selectAll))

        # venv环境表格菜单
        self.venv_table_menu = RoundMenu(parent=self.venv_table)
        self.venv_table_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_row(self.venv_table)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_venv),
            Action(FluentIcon.EDIT, '编辑名称', triggered=self.edit_venv_name),
            Action(FluentIcon.EDIT, '编辑启动参数', triggered=self.edit_venv_startup_parameters),
            Action(FluentIcon.ADD, '创建环境', triggered=lambda: self.add_jump("venv")),
            Action(FluentIcon.DELETE, '卸载', triggered=self.delete_venv_folder),
            Action(FluentIcon.DELETE, '删除条目', triggered=self.delete_venv)
        ])
        # 添加分割线
        self.venv_table_menu.addSeparator()
        self.venv_table_menu.addAction(Action(FluentIcon.INFO, '详情', triggered=self.details_venv))
        self.venv_table_menu.addAction(Action('全选', shortcut='Ctrl+A', triggered=self.venv_table.selectAll))

        # 配置文件表格菜单
        self.config_table_menu = RoundMenu(parent=self.config_table)
        self.config_table_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_row(self.config_table)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_config),
            Action(FluentIcon.EDIT, '编辑名称', triggered=self.edit_config_name),
            Action(FluentIcon.EDIT, '编辑命令列表', triggered=self.edit_config_older_list),
            Action(FluentIcon.ADD, '创建配置', triggered=lambda: self.add_jump("config")),
            Action(FluentIcon.DELETE, '删除', triggered=self.delete_config)
        ])
        # 添加分割线
        self.config_table_menu.addSeparator()
        self.config_table_menu.addAction(Action(FluentIcon.INFO, '详情', triggered=self.details_config))
        self.config_table_menu.addAction(Action('全选', shortcut='Ctrl+A', triggered=self.config_table.selectAll))

        # 预设脚本表格菜单
        self.preset_scripts_table_menu = RoundMenu(parent=self.preset_scripts_table)
        self.preset_scripts_table_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_row(self.preset_scripts_table)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_preset_scripts),
            Action(FluentIcon.EDIT, '编辑名称', triggered=self.edit_preset_scripts_name),
            Action(FluentIcon.EDIT, '编辑描述', triggered=self.edit_preset_scripts_description),
            Action(FluentIcon.EDIT, '编辑命令参数', triggered=self.edit_preset_scripts_older_parameters),
            Action(FluentIcon.ADD, '创建预设', triggered=lambda: self.add_jump("preset")),
            Action(FluentIcon.DELETE, '删除', triggered=self.delete_preset_scripts)
        ])
        # 添加分割线
        self.preset_scripts_table_menu.addSeparator()
        self.preset_scripts_table_menu.addAction(Action(FluentIcon.INFO, '详情', triggered=self.details_preset_scripts))
        self.preset_scripts_table_menu.addAction(Action('全选', shortcut='Ctrl+A', triggered=self.preset_scripts_table.selectAll))

        # 图钉表格菜单
        self.pin_table_menu = RoundMenu(parent=self.pin_table)
        self.pin_table_menu.addActions([
            Action(FluentIcon.COPY, '复制', shortcut='Ctrl+C', triggered=lambda: self.copy_row(self.pin_table)),
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_pin),
            Action(FluentIcon.EDIT, '编辑命令', triggered=self.edit_pin_name),
            Action(FluentIcon.ADD, '创建图钉', triggered=lambda: self.add_jump("pin")),
            Action(FluentIcon.DELETE, '删除', triggered=self.delete_pin)
        ])
        # 添加分割线
        self.pin_table_menu.addSeparator()
        self.pin_table_menu.addAction(Action(FluentIcon.INFO, '详情', triggered=self.details_pin))
        self.pin_table_menu.addAction(Action('全选', shortcut='Ctrl+A', triggered=self.pin_table.selectAll))

        # 空白区域菜单
        # 图钉列表空白菜单
        self.pin_list_none_menu = RoundMenu(parent=self.pin_list)
        self.pin_list_none_menu.addActions([
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_pin),
            Action(FluentIcon.ADD, '创建图钉', triggered=lambda: self.add_jump("pin"))
        ])
        # 环境树空白菜单
        self.venv_tree_none_menu = RoundMenu(parent=self.venv_tree)
        self.venv_tree_none_menu.addActions([
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_venv_tree),
            Action(FluentIcon.ADD, '创建环境', triggered=lambda: self.add_jump("venv"))
        ])
        # python环境表格空白菜单
        self.python_table_none_menu = RoundMenu(parent=self.python_table)
        self.python_table_none_menu.addActions([
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_python),
            Action(FluentIcon.ADD, '创建环境', triggered=lambda: self.add_jump("python"))
        ])
        # emb环境表格空白菜单
        self.emb_table_none_menu = RoundMenu(parent=self.emb_table)
        self.emb_table_none_menu.addActions([
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_emb),
            Action(FluentIcon.ADD, '创建环境', triggered=lambda: self.add_jump("emb"))
        ])
        # venv环境表格空白菜单
        self.venv_table_none_menu = RoundMenu(parent=self.venv_table)
        self.venv_table_none_menu.addActions([
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_venv),
            Action(FluentIcon.ADD, '创建环境', triggered=lambda: self.add_jump("venv"))
        ])
        # 配置文件表格空白菜单
        self.config_table_none_menu = RoundMenu(parent=self.config_table)
        self.config_table_none_menu.addActions([
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_config),
            Action(FluentIcon.ADD, '创建配置', triggered=lambda: self.add_jump("config"))
        ])
        # 预设脚本表格空白菜单
        self.preset_scripts_table_none_menu = RoundMenu(parent=self.preset_scripts_table)
        self.preset_scripts_table_none_menu.addActions([
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_preset_scripts),
            Action(FluentIcon.ADD, '创建预设', triggered=lambda: self.add_jump("preset"))
        ])
        # 图钉表格空白菜单
        self.pin_table_none_menu = RoundMenu(parent=self.pin_table)
        self.pin_table_none_menu.addActions([
            Action(FluentIcon.SYNC, '刷新', triggered=self.update_pin),
            Action(FluentIcon.ADD, '创建图钉', triggered=lambda: self.add_jump("pin"))
        ])

    # 弹出图钉列表右键菜单
    def show_pin_list_menu(self,pos):
        try:
            item = self.pin_list.itemAt(pos)  # 拿到鼠标下的单元格

            if item is None:
                self.pin_list_none_menu.exec_(self.pin_list.viewport().mapToGlobal(pos))  # 弹空白区域菜单
            else:
                # 提前选中
                self.pin_list.setCurrentItem(item)
                # 在鼠标全局位置弹出
                self.pin_list_menu.exec_(self.pin_list.viewport().mapToGlobal(pos))
        except Exception as a:
            print(a)

    # 修改图钉列表命令
    def edit_pin_list_name(self):
        item = self.pin_list.currentItem()
        old_text = item.text()
        row = self.pin_list.row(item)

        dialog = LineDialog("修改命令", "修改图钉命令", self)
        dialog.line.setText(old_text)

        if dialog.exec():
            new_text = dialog.line.text().strip()
            if new_text and new_text != old_text:
                JCP.modify("config.json", ["pin"], row, new_text)

                # 更新图钉
                self.update_pin()

                InfoBar.success(
                    title="成功",
                    content="图钉命令已修改",
                    parent=self,
                    position=InfoBarPosition.TOP
                )

        dialog.accept()
        dialog.deleteLater()

    # 删除图钉列表命令
    def delete_pin_list(self):
        item = self.pin_list.currentItem()
        row = self.pin_list.row(item)

        dialog = Dialog("提示", "是否删除所选图钉？此操作不可撤销", self)

        if dialog.exec():

            # 提前删除
            JCP.remove("config.json", ["pin"], row)
            # 删除列表项
            self.pin_list.takeItem(row)

            # 更新图钉
            self.update_pin()

            InfoBar.success(
                title="成功",
                content=f"选中图钉已删除",
                parent=self,
                position=InfoBarPosition.TOP
            )

        dialog.accept()
        dialog.deleteLater()

    # 弹出环境树右键菜单
    def show_venv_tree_menu(self,pos):
        try:
            item = self.venv_tree.itemAt(pos)  # 拿到鼠标下的单元格

            # 项对象转换模型索引
            self.select_venv_item(self.venv_tree.indexFromItem(item))

            # 选中无项
            if item is None:
                self.venv_tree_none_menu.exec_(self.venv_tree.viewport().mapToGlobal(pos))  # 弹空白区域菜单
            # 选中树枝
            elif item.parent() is None:
                self.venv_tree_branch_menu.exec_(self.venv_tree.viewport().mapToGlobal(pos))  # 弹树枝区域菜单

            # 选中Venv
            elif item.data(0, Qt.UserRole)["type"] == "venv":
                self.venv_tree_venv_menu.exec_(self.venv_tree.viewport().mapToGlobal(pos))  # 弹虚拟环境区域菜单
            # 选中Emb
            elif item.data(0, Qt.UserRole)["type"] == "emb":
                self.venv_tree_emb_menu.exec_(self.venv_tree.viewport().mapToGlobal(pos))  # 弹便携式环境区域菜单
            # 选中Python
            elif item.data(0, Qt.UserRole)["type"] == "python":
                self.venv_tree_python_menu.exec_(self.venv_tree.viewport().mapToGlobal(pos))  # 弹基础环境区域菜单
            # 其他情况 选中空白
            else:
                self.venv_tree_none_menu.exec_(self.venv_tree.viewport().mapToGlobal(pos))  # 弹空白区域菜单

        except Exception as a:
            print(a)

    # 弹出基础环境右键菜单
    def show_python_table_menu(self,pos):
        try:
            # pos 是相对于 table 的坐标
            item = self.python_table.itemAt(pos)  # 拿到鼠标下的单元格
            if item is None:
                self.python_table_none_menu.exec_(self.python_table.viewport().mapToGlobal(pos))  # 弹空白区域菜单
            else:
                # 在鼠标全局位置弹出
                self.python_table_menu.exec_(self.python_table.viewport().mapToGlobal(pos))
        except Exception as a:
            print(a)

    # 复制行
    def copy_row(self,table):
        item = table.currentItem()
        QApplication.clipboard().setText(item.text())
        InfoBar.info(
            title="通知",
            content="内容已复制到剪切板",
            parent=self,
            position=InfoBarPosition.TOP
        )

    # 复制树行
    def copy_tree_row(self,table):
        item = table.currentItem()
        QApplication.clipboard().setText(item.text(0))
        InfoBar.info(
            title="通知",
            content="内容已复制到剪切板",
            parent=self,
            position=InfoBarPosition.TOP
        )

    # 修改基础环境名称
    def edit_python_name(self):
        try:
            # 获取当前所在行
            row = self.python_table.currentRow()
            # 拿到第0列item
            item = self.python_table.item(row, 0)

            text = item.text()

            dialog = LineDialog("修改名称","修改基础环境名称",self)
            dialog.line.setText(text)
            if dialog.exec():
                # 名称被修改
                if dialog.line.text() != text:
                    JCP.update("config.json",["python",item.data(Qt.UserRole),"name"],dialog.line.text())
                    self.update_python()  # 更新

                    InfoBar.success(
                        title="成功",
                        content="环境名称已修改",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )
                    # 更新环境树
                    self.update_venv_tree()

            # 销毁
            dialog.accept()
            dialog.deleteLater()

        except Exception as a:
            print(a)

    # 删除基础环境条目
    def delete_python(self):
        dialog = Dialog("提示", "是否删除所选基础环境条目 此操作不可撤销", self)

        if dialog.exec():
            # 获取所有选中的单元格
            selected_items = self.python_table.selectedItems()

            # 提取所有选中的行号 并用set去重 降序排列以便从后往前删除
            rows_to_delete = sorted(set(item.row() for item in selected_items), reverse=True)

            # 在删除前获取每行第一列的数据
            for row in rows_to_delete:
                # 获取该行第0列item
                item = self.python_table.item(row, 0)
                # 获取数据
                data = item.data(Qt.UserRole)
                # 删除json
                JCP.delete("config.json",["python",data])

            # 从后往前删除，防止索引偏移
            for row in rows_to_delete:
                self.python_table.removeRow(row)

            InfoBar.success(
                title="成功",
                content="选中环境条目已删除",
                parent=self,
                position=InfoBarPosition.TOP
            )

            # 更新环境树
            self.update_venv_tree()

        # 销毁
        dialog.accept()
        dialog.deleteLater()

    # 弹出便携式环境右键菜单
    def show_emb_table_menu(self,pos):
        try:
            # pos 是相对于 table 的坐标
            item = self.emb_table.itemAt(pos)  # 拿到鼠标下的单元格
            if item is None:
                self.emb_table_none_menu.exec_(self.emb_table.viewport().mapToGlobal(pos))  # 弹空白区域菜单
            else:
                # 在鼠标全局位置弹出
                self.emb_table_menu.exec_(self.emb_table.viewport().mapToGlobal(pos))
        except Exception as a:
            print(a)

    # 删除便携式环境条目
    def delete_emb(self):
        dialog = Dialog("提示", "是否删除所选便携式环境条目 此操作不可撤销", self)

        if dialog.exec():
            # 获取所有选中的单元格
            selected_items = self.emb_table.selectedItems()

            # 提取所有选中的行号 并用set去重 降序排列以便从后往前删除
            rows_to_delete = sorted(set(item.row() for item in selected_items), reverse=True)

            # 在删除前获取每行第一列的数据
            for row in rows_to_delete:
                # 获取该行第0列item
                item = self.emb_table.item(row, 0)
                # 获取数据
                data = item.data(Qt.UserRole)
                # 删除json
                JCP.delete("config.json",["emb",data])

            # 从后往前删除，防止索引偏移
            for row in rows_to_delete:
                self.emb_table.removeRow(row)

            InfoBar.success(
                title="成功",
                content="选中环境条目已删除",
                parent=self,
                position=InfoBarPosition.TOP
            )

            # 更新环境树
            self.update_venv_tree()

        # 销毁
        dialog.accept()
        dialog.deleteLater()

    # 弹出图钉右键菜单
    def show_pin_table_menu(self,pos):
        try:
            # pos 是相对于 table 的坐标
            item = self.pin_table.itemAt(pos)  # 拿到鼠标下的单元格
            if item is None:
                self.pin_table_none_menu.exec_(self.pin_table.viewport().mapToGlobal(pos))  # 弹空白区域菜单
            else:
                # 在鼠标全局位置弹出
                self.pin_table_menu.exec_(self.pin_table.viewport().mapToGlobal(pos))
        except Exception as a:
            print(a)

    # 修改图钉命令
    def edit_pin_name(self):
        try:
            # 获取当前所在行
            row = self.pin_table.currentRow()
            # 拿到第0列item
            item = self.pin_table.item(row, 0)

            text = item.text()

            dialog = LineDialog("修改命令","修改图钉命令",self)
            dialog.line.setText(text)
            if dialog.exec():
                # 名称被修改
                if dialog.line.text() != text:
                    JCP.modify("config.json",["pin"],row,dialog.line.text())
                    self.update_pin()  # 更新

                    InfoBar.success(
                        title="成功",
                        content="图钉命令已修改",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )

            # 销毁
            dialog.accept()
            dialog.deleteLater()

        except Exception as a:
            print(a)

    # 删除图钉
    def delete_pin(self):
        dialog = Dialog("提示", "是否删除所选图钉 此操作不可撤销", self)

        if dialog.exec():
            # 获取所有选中的单元格
            selected_items = self.pin_table.selectedItems()

            # 提取所有选中的行号 并用set去重 降序排列以便从后往前删除
            rows_to_delete = sorted(set(item.row() for item in selected_items), reverse=True)

            # 在删除前获取每行
            for row in rows_to_delete:
                # 删除json
                JCP.remove("config.json",["pin"],row)

            # 从后往前删除，防止索引偏移
            for row in rows_to_delete:
                self.pin_table.removeRow(row)

            # 更新图钉
            self.update_pin()

            InfoBar.success(
                title="成功",
                content="选中图钉已删除",
                parent=self,
                position=InfoBarPosition.TOP
            )

        # 销毁
        dialog.accept()
        dialog.deleteLater()

    # 弹出预设脚本右键菜单
    def show_preset_scripts_table_menu(self,pos):
        try:
            # pos 是相对于 table 的坐标
            item = self.preset_scripts_table.itemAt(pos)  # 拿到鼠标下的单元格
            if item is None:
                self.preset_scripts_table_none_menu.exec_(self.preset_scripts_table.viewport().mapToGlobal(pos))  # 弹空白区域菜单
            else:
                # 在鼠标全局位置弹出
                self.preset_scripts_table_menu.exec_(self.preset_scripts_table.viewport().mapToGlobal(pos))
        except Exception as a:
            print(a)

    # 修改预设脚本名称
    def edit_preset_scripts_name(self):
        try:
            # 获取当前所在行
            row = self.preset_scripts_table.currentRow()
            # 拿到第0列item
            item = self.preset_scripts_table.item(row, 0)

            text = item.text()

            dialog = LineDialog("修改名称","修改预设脚本名称",self)
            dialog.line.setText(text)
            if dialog.exec():
                # 名称被修改
                if dialog.line.text() != text:
                    JCP.update("config.json",["preset_scripts",item.data(Qt.UserRole),"name"],dialog.line.text())
                    self.update_preset_scripts()  # 更新

                    InfoBar.success(
                        title="成功",
                        content="预设名称已修改",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )

            # 销毁
            dialog.accept()
            dialog.deleteLater()

        except Exception as a:
            print(a)

    # 修改预设脚本描述
    def edit_preset_scripts_description(self):
        try:
            # 获取当前所在行
            row = self.preset_scripts_table.currentRow()
            # 拿到第0和1列item
            item = self.preset_scripts_table.item(row, 0)
            item2 = self.preset_scripts_table.item(row, 1)

            text = item2.text()

            dialog = LineDialog("修改描述","修改预设脚本描述",self)
            dialog.line.setText(text)
            if dialog.exec():
                # 名称被修改
                if dialog.line.text() != text:
                    JCP.update("config.json",["preset_scripts",item.data(Qt.UserRole),"description"],dialog.line.text())
                    self.update_preset_scripts()  # 更新

                    InfoBar.success(
                        title="成功",
                        content="预设描述已修改",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )

            # 销毁
            dialog.accept()
            dialog.deleteLater()

        except Exception as a:
            print(a)

    # 修改预设脚本命令参数
    def edit_preset_scripts_older_parameters(self):
        try:
            # 获取当前所在行
            row = self.preset_scripts_table.currentRow()
            # 拿到第023列item
            item = self.preset_scripts_table.item(row, 0)
            item2 = self.preset_scripts_table.item(row, 2)
            item3 = self.preset_scripts_table.item(row, 3)

            text = item2.text()
            text2 = item3.text()

            dialog = LineDictDialog("修改命令参数", "修改预设脚本命令参数", self)
            dialog.line.setText(text)

            json_data = JCP.get("config.json", ["preset_scripts", item.data(Qt.UserRole)])
            for t in json_data['parameters_dict']:
                dialog.texteditL.append(t)
                dialog.texteditR.append(json_data['parameters_dict'][t])
            cursorL = dialog.texteditL.textCursor()
            cursorL.setPosition(0)
            dialog.texteditL.setTextCursor(cursorL)
            cursorR = dialog.texteditR.textCursor()
            cursorR.setPosition(0)
            dialog.texteditR.setTextCursor(cursorR)

            if dialog.exec():
                dist_parameters_dict = tool.get_dict_from_textedits(dialog.texteditL,dialog.texteditR)

                # 命令参数被修改 命令被修改或参数被修改
                if dialog.line.text() != text or str(dist_parameters_dict) != text2:
                    JCP.update("config.json",["preset_scripts", item.data(Qt.UserRole), "older"],dialog.line.text())
                    JCP.update("config.json",["preset_scripts", item.data(Qt.UserRole), "parameters_dict"],dist_parameters_dict)
                    self.update_preset_scripts()  # 更新

                    InfoBar.success(
                        title="成功",
                        content="命令参数已修改",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )

            # 销毁
            dialog.accept()
            dialog.deleteLater()

        except Exception as a:
            print(a)

    # 删除预设脚本
    def delete_preset_scripts(self):
        dialog = Dialog("提示", "是否删除所选预设脚本 此操作不可撤销", self)

        if dialog.exec():
            # 获取所有选中的单元格
            selected_items = self.preset_scripts_table.selectedItems()

            # 提取所有选中的行号 并用set去重 降序排列以便从后往前删除
            rows_to_delete = sorted(set(item.row() for item in selected_items), reverse=True)

            # 在删除前获取每行第一列的数据
            for row in rows_to_delete:
                # 获取该行第0列item
                item = self.preset_scripts_table.item(row, 0)
                # 获取数据
                data = item.data(Qt.UserRole)
                # 删除json
                JCP.delete("config.json",["preset_scripts",data])

            # 从后往前删除，防止索引偏移
            for row in rows_to_delete:
                self.preset_scripts_table.removeRow(row)

            InfoBar.success(
                title="成功",
                content="选中预设脚本已删除",
                parent=self,
                position=InfoBarPosition.TOP
            )

        # 销毁
        dialog.accept()
        dialog.deleteLater()

    # 弹出配置文件右键菜单
    def show_config_table_menu(self,pos):
        try:
            # pos 是相对于 table 的坐标
            item = self.config_table.itemAt(pos)  # 拿到鼠标下的单元格
            if item is None:
                self.config_table_none_menu.exec_(self.config_table.viewport().mapToGlobal(pos))  # 弹空白区域菜单
            else:
                # 在鼠标全局位置弹出
                self.config_table_menu.exec_(self.config_table.viewport().mapToGlobal(pos))
        except Exception as a:
            print(a)

    # 修改配置文件名称
    def edit_config_name(self):
        try:
            # 获取当前所在行
            row = self.config_table.currentRow()
            # 拿到第0列item
            item = self.config_table.item(row, 0)

            text = item.text()

            dialog = LineDialog("修改名称","修改配置文件名称",self)
            dialog.line.setText(text)
            if dialog.exec():
                # 名称被修改
                if dialog.line.text() != text:
                    JCP.update("config.json",["config",item.data(Qt.UserRole),"name"],dialog.line.text())
                    self.update_config()  # 更新

                    InfoBar.success(
                        title="成功",
                        content="配置名称已修改",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )

            # 销毁
            dialog.accept()
            dialog.deleteLater()

        except Exception as a:
            print(a)

    # 修改配置文件命令列表
    def edit_config_older_list(self):
        try:
            # 获取当前所在行
            row = self.config_table.currentRow()
            # 拿到第1列item
            item = self.config_table.item(row, 0)
            # 拿到第1列item
            item2 = self.config_table.item(row, 1)
            text = item2.text()

            dialog = TextEditDialog("修改命令列表","修改配置文件命令列表",self)

            # 字符串列表转列表
            for t in tool.str_list_to_list(text):
                dialog.line.append(t)
            # 移动光标到文档最开头
            cursor = dialog.line.textCursor()
            cursor.setPosition(0)
            dialog.line.setTextCursor(cursor)

            if dialog.exec():
                # 被修改 字符串行转字符串列表
                if str(tool.str_line_to_list(dialog.line.toPlainText())) != text:
                    # 新命令 字符串行转列表
                    new_text = tool.str_line_to_list(dialog.line.toPlainText())
                    JCP.update("config.json",["config",item.data(Qt.UserRole),"older_list"],new_text)
                    self.update_config()  # 更新

                    InfoBar.success(
                        title="成功",
                        content="配置名称已修改",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )

            # 销毁
            dialog.accept()
            dialog.deleteLater()

        except Exception as a:
            print(a)

    # 删除配置文件
    def delete_config(self):
        dialog = Dialog("提示", "是否删除所选配置文件 此操作不可撤销", self)

        if dialog.exec():
            # 获取所有选中的单元格
            selected_items = self.config_table.selectedItems()

            # 提取所有选中的行号 并用set去重 降序排列以便从后往前删除
            rows_to_delete = sorted(set(item.row() for item in selected_items), reverse=True)

            # 在删除前获取每行第一列的数据
            for row in rows_to_delete:
                # 获取该行第0列item
                item = self.config_table.item(row, 0)
                # 获取数据
                data = item.data(Qt.UserRole)
                # 删除json
                JCP.delete("config.json",["config",data])

            # 从后往前删除，防止索引偏移
            for row in rows_to_delete:
                self.config_table.removeRow(row)

            InfoBar.success(
                title="成功",
                content="选中配置文件已删除",
                parent=self,
                position=InfoBarPosition.TOP
            )

        # 销毁
        dialog.accept()
        dialog.deleteLater()

    # 弹出虚拟环境右键菜单
    def show_venv_table_menu(self,pos):
        try:
            # pos 是相对于 table 的坐标
            item = self.venv_table.itemAt(pos)  # 拿到鼠标下的单元格
            if item is None:
                self.venv_table_none_menu.exec_(self.venv_table.viewport().mapToGlobal(pos))  # 弹空白区域菜单
            else:
                # 在鼠标全局位置弹出
                self.venv_table_menu.exec_(self.venv_table.viewport().mapToGlobal(pos))
        except Exception as a:
            print(a)

    # 修改虚拟环境名称
    def edit_venv_name(self):
        try:
            # 获取当前所在行
            row = self.venv_table.currentRow()
            # 拿到第0列item
            item = self.venv_table.item(row, 0)

            text = item.text()

            dialog = LineDialog("修改名称","修改虚拟环境名称",self)
            dialog.line.setText(text)
            if dialog.exec():
                # 名称被修改
                if dialog.line.text() != text:
                    JCP.update("config.json",["venv",item.data(Qt.UserRole),"name"],dialog.line.text())
                    self.update_venv()  # 更新

                    InfoBar.success(
                        title="成功",
                        content="环境名称已修改",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )

                    # 更新环境树
                    self.update_venv_tree()

            # 销毁
            dialog.accept()
            dialog.deleteLater()

        except Exception as a:
            print(a)

    # 修改虚拟环境启动参数
    def edit_venv_startup_parameters(self):
        try:
            # 获取当前所在行
            row = self.venv_table.currentRow()
            # 拿到第4列item
            item = self.venv_table.item(row, 4)

            text = item.text()

            dialog = LineDialog("修改启动参数","修改虚拟环境启动参数",self)
            dialog.line.setText(text)
            if dialog.exec():
                # 名称被修改
                if dialog.line.text() != text:
                    JCP.update("config.json",["venv",self.venv_table.item(row, 0).data(Qt.UserRole),"start_parameter"],dialog.line.text())
                    self.update_venv()  # 更新

                    InfoBar.success(
                        title="成功",
                        content="环境启动参数已修改",
                        parent=self,
                        position=InfoBarPosition.TOP
                    )

                    # 更新环境树
                    self.update_venv_tree()

            # 销毁
            dialog.accept()
            dialog.deleteLater()

        except Exception as a:
            print(a)

    # 删除虚拟环境条目
    def delete_venv(self):
        # cmd未全部关机
        if self.cmd_obj_dict == {}:
            dialog = Dialog("提示", "是否删除所选虚拟环境条目 此操作不可撤销", self)

            if dialog.exec():
                # 获取所有选中的单元格
                selected_items = self.venv_table.selectedItems()

                # 提取所有选中的行号 并用set去重 降序排列以便从后往前删除
                rows_to_delete = sorted(set(item.row() for item in selected_items), reverse=True)

                # 在删除前获取每行第一列的数据
                for row in rows_to_delete:
                    # 获取该行第0列item
                    item = self.venv_table.item(row, 0)
                    # 获取数据
                    data = item.data(Qt.UserRole)
                    # 删除json
                    JCP.delete("config.json",["venv",data])

                # 从后往前删除，防止索引偏移
                for row in rows_to_delete:
                    self.venv_table.removeRow(row)

                InfoBar.success(
                    title="成功",
                    content="选中环境条目已删除",
                    parent=self,
                    position=InfoBarPosition.TOP
                )

                # 重置
                self.cmd_stackedwidget.setCurrentIndex(0)
                self.power_label_text.setText("没有选中的虚拟环境")
                # 更新环境树
                self.update_venv_tree()

            # 销毁
            dialog.accept()
            dialog.deleteLater()
        else:
            InfoBar.error(
                title="错误",
                content="仍有虚拟环境未关机 删除被拒绝",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )

    # 删除环境文件夹
    def delete_venv_folder(self):
        # cmd未全部关机
        if self.cmd_obj_dict == {}:
            dialog = Dialog("提示", "是否卸载所选虚拟环境 此操作不可撤销", self)
            if dialog.exec():

                # 提取所有选中的行号 并用set去重 降序排列以便从后往前删除
                rows_to_delete = sorted(set(item.row() for item in self.venv_table.selectedItems()), reverse=True)

                # 在删除前获取每行第一列的数据
                for row in rows_to_delete:
                    # 获取该行第0列item
                    item = self.venv_table.item(row, 0)
                    # 获取数据
                    data = item.data(Qt.UserRole)

                    dialog2 = SegmentedArcIndeterminateProgressRingDialog("正在卸载虚拟环境...",self)
                    dialog2.show()

                    # 删除文件夹
                    self.delect_venv_thread = DeleteFolder(data)
                    self.delect_venv_thread.error.connect(lambda s:self.uninstall_venv_error(s,dialog2,self.delect_venv_thread))
                    self.delect_venv_thread.finished.connect(lambda :self.uninstall_venv(dialog2,self.delect_venv_thread))
                    self.delect_venv_thread.start()

            # 销毁
            dialog.accept()
            dialog.deleteLater()
        else:
            InfoBar.error(
                title="错误",
                content="仍有虚拟环境未关机 卸载被拒绝",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )

    # 卸载环境
    def uninstall_venv(self,dialog,thread):
        dialog.accept()
        dialog.deleteLater()
        thread.deleteLater()

        # 获取所有选中的单元格
        selected_items = self.venv_table.selectedItems()

        # 提取所有选中的行号 并用set去重 降序排列以便从后往前删除
        rows_to_delete = sorted(set(item.row() for item in selected_items), reverse=True)

        # 在删除前获取每行第一列的数据
        for row in rows_to_delete:
            # 获取该行第0列item
            item = self.venv_table.item(row, 0)
            # 获取数据
            data = item.data(Qt.UserRole)
            # 删除json
            JCP.delete("config.json",["venv",data])

        # 从后往前删除，防止索引偏移
        for r in rows_to_delete:
            self.venv_table.removeRow(r)

        InfoBar.success(
            title="成功",
            content="选中环境已卸载",
            parent=self,
            position=InfoBarPosition.TOP
        )

        # 重置
        self.cmd_stackedwidget.setCurrentIndex(0)
        self.power_label_text.setText("没有选中的虚拟环境")
        # 更新环境树
        self.update_venv_tree()

        # 播放音效 操作完成音效未禁用
        if self.play_sound and not self.play_sound_operation_completed:
            BSP.play("OperationCompleted")

    # 卸载错误
    def uninstall_venv_error(self,s,dialog,thread):
        dialog.accept()
        dialog.deleteLater()
        thread.deleteLater()

        InfoBar.error(title="错误",
                      content=s,
                      parent=self,
                      position=InfoBarPosition.TOP,
                      duration=1500
                      )

    # 打开安装虚拟环境窗口
    def open_install_venv_window(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "选择 安装位置",
            "C:/"
        )

        if path != '':
            dir_path = "venv"  # 默认文件夹
            if path.endswith("/") or path.endswith("\\"): # 以/\结尾
                self.venv_loca_line.setText(path+dir_path)
            else:
                self.venv_loca_line.setText(path+"/"+dir_path)
            self.venv_loca_name.setText(dir_path)

    # 虚拟环境命令批处理
    def venv_command_batch(self,state,param):
        try:
            if state:  # 选中
                if param not in self.python_batch_list:
                    self.python_batch_list.append(param)
            else:  # 取消选中
                if param in self.python_batch_list:
                    self.python_batch_list.remove(param)

            # 更新命令
            self.update_venv_command()

        except Exception as a:
            print(a)

    # 刷新虚拟环境命令
    def update_venv_command(self):
        # 选中基础解释器
        if self.base_python_box.text() != "":
            # 基础命令
            if not self.custom_prompts_prefix_box.isChecked():
                base = f'"{self.base_python_box.text()}" -m venv "{self.venv_loca_line.text()}"'
            else:
                base = f'"{self.base_python_box.text()}" -m venv "{self.venv_loca_line.text()}" --prompt "{self.prompts_prefix_line.text()}"' # 提示符命令
            # 将列表元素用空格连接
            params_str = ' '.join(self.python_batch_list)
            full_cmd = f"{base} {params_str}" if params_str else base

            self.created_parameter_line.setText(full_cmd)
        # 否则清空
        else:
            self.created_parameter_line.setText("")

    # 跳过安装pip互斥
    def skip_installing_pip_mutual_exclusion(self,s):
        if self.upgrade_package_box.isChecked():
            self.upgrade_package_box.setChecked(False)

        self.upgrade_package_box.setEnabled(not s)

    # 创建虚拟环境
    def create_venv(self):
        # 基础解释器是否存在
        if not os.path.exists(self.base_python_box.text()):
            InfoBar.error(
                title="错误",
                content="基础解释器不存在",
                parent=self,
                position=InfoBarPosition.TOP
            )
        # 是否是空路径
        elif self.venv_loca_line.text() == "":
            dialog = Dialog("提示","安装路径为空 是否将虚拟环境安装在VEM下的.venvs文件夹中")

            if dialog.exec():
                # 获取工作目录下的venvs和防重名
                path = tool.get_unique_name(os.getcwd()+"\\.venvs","venv")
                name = os.path.basename(path)
                self.venv_loca_line.setText(path)
                self.venv_loca_name.setText(name)
            # 清理
            dialog.accept()
            dialog.deleteLater()

        # 校验命令是否合法
        elif not tool.is_valid_venv_create_command(self.created_parameter_line.text()):
            InfoBar.error(
                title="错误",
                content="创建命令不合法",
                parent=self,
                position=InfoBarPosition.TOP
            )

        else:
            # 固定长度不确定进度环
            Indeterminate_dialog = FixedLengthIndeterminateProgressRingDialog("正在安装Venv...",self)
            Indeterminate_dialog.show()

            # 执行Venv批处理
            self.venv_thread_batch_processing = Threads.VenvBatchProcessing(self.created_parameter_line.text(),False,False)
            self.venv_thread_batch_processing.finished.connect(lambda :self.Venv_batch_processing_end(Indeterminate_dialog))
            self.venv_thread_batch_processing.update_title.connect(lambda title:Indeterminate_dialog.label.setText(title))
            self.venv_thread_batch_processing.error.connect(lambda err: self.batch_error(err,Indeterminate_dialog,self.venv_thread_batch_processing))
            self.venv_thread_batch_processing.start()

    # Venv批处理完成
    def Venv_batch_processing_end(self,dialog):
        try:
            # 清理
            dialog.accept()
            dialog.deleteLater()
            self.venv_thread_batch_processing.deleteLater()

            # 添加到配置
            dir_path = self.venv_loca_line.text()
            # /\结尾
            if self.venv_loca_line.text().endswith("/") or self.venv_loca_line.text().endswith("\\"):
                cfg_path = self.venv_loca_line.text()+"pyvenv.cfg"
            else:
                cfg_path = self.venv_loca_line.text() + "/pyvenv.cfg"
            # 查找基础环境版本
            venv_version = JCP.get("config.json",["python",os.path.dirname(self.base_python_box.text()),"version"],"Python")

            JCP.update(
                "config.json",
                ["venv",dir_path],
                {
                    "name": self.venv_loca_name.text(), # 名称
                    "python":self.base_python_box.text() , # 基础解释器
                    "cfg_file": cfg_path, # cfg配置文件
                    "dir": dir_path, # venv目录
                    "start_parameter": self.venv_startup_parameters_line.text(),# 启动参数
                    "include-system-site-packages": self.inherits_global_site_software_packages_box.isChecked(),# 全局开关
                    "version": venv_version # 版本
                })
            InfoBar.success(
                title="完成",
                content=f"虚拟环境创建完成",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )

            self.reset_venv() # 重置
            self.update_venv() # 更新虚拟环境

            # 播放音效 操作完成音效未禁用
            if self.play_sound and not self.play_sound_operation_completed:
                BSP.play("OperationCompleted")

        except Exception as a:
            print(a)

    # 批处理错误
    def batch_error(self,text,dialog,thread):
        dialog.accept()
        dialog.deleteLater()
        InfoBar.error(
            title="错误",
            content=text,
            parent=self,
            position=InfoBarPosition.TOP,
            duration=1500
        )
        thread.deleteLater()

    # 重置新建虚拟环境
    def reset_venv(self):
        self.venv_loca_name.setText("")
        self.venv_loca_line.setText("")
        self.base_python_box.setText("")

        self.inherits_global_site_software_packages_box.setChecked(False)
        self.try_using_symbolic_links_box.setChecked(False)
        self.forced_file_copying_box.setChecked(False)
        self.clear_existing_directories_box.setChecked(False)
        self.upgrade_package_box.setChecked(False)
        self.skip_installing_pip_box.setChecked(False)
        self.custom_prompts_prefix_box.setChecked(False)

        self.prompts_prefix_line.setText("")
        self.venv_startup_parameters_line.setText("")
        self.created_parameter_line.setText("")

    # 打开安装配置虚拟环境窗口
    def open_install_config_venv_window(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "选择 安装位置",
            "C:/"
        )

        if path != '':
            dir_path = "venv"  # 默认文件夹
            if path.endswith("/") or path.endswith("\\"): # 以/\结尾
                self.config_venv_Loca_line.setText(path+dir_path)
            else:
                self.config_venv_Loca_line.setText(path+"/"+dir_path)
            self.config_venv_name.setText(dir_path)

    # 配置虚拟环境命令批处理
    def config_venv_command_batch(self,state,param):
        try:
            if state:  # 选中
                if param not in self.config_python_batch_list:
                    self.config_python_batch_list.append(param)
            else:  # 取消选中
                if param in self.config_python_batch_list:
                    self.config_python_batch_list.remove(param)

            # 更新命令
            self.update_config_venv_command()

        except Exception as a:
            print(a)

    # 重置配置虚拟环境
    def reset_config_venv(self):
        self.config_venv_name.setText("")
        self.config_venv_Loca_line.setText("")
        self.config_base_python_box.setText("")

        self.config_inherits_global_site_software_packages_box.setChecked(False)
        self.config_clear_existing_directories_box.setChecked(False)
        self.config_forced_file_copying_box.setChecked(False)
        self.config_try_using_symbolic_links_box.setChecked(False)
        self.config_upgrade_package_box.setChecked(False)
        self.config_skip_installing_pip_box.setChecked(False)
        self.config_created_using_CMD_instead_internal_creator_box.setChecked(False)
        self.config_keep_CMD_open_after_creation_box.setChecked(False)
        self.config_custom_prompts_prefix_box.setChecked(False)

        self.config_prompts_prefix_line.setText("")
        self.config_startup_parameters_line.setText("")
        self.config_created_parameter_line.setText("")
        self.config_file_box.setText("")

    # 仅创建虚拟环境
    def only_create_venv(self):
        # 基础解释器是否存在
        if not os.path.exists(self.config_base_python_box.text()):
            InfoBar.error(
                title="错误",
                content="基础解释器不存在",
                parent=self,
                position=InfoBarPosition.TOP
            )
        # 是否是空路径
        elif self.config_venv_Loca_line.text() == "":
            dialog = Dialog("提示","安装路径为空 是否将虚拟环境安装在VEM下的.venvs文件夹中")

            if dialog.exec():
                # 获取工作目录下的venvs和防重名
                path = tool.get_unique_name(os.getcwd()+"\\.venvs","venv")
                name = os.path.basename(path)
                self.config_venv_Loca_line.setText(path)
                self.config_venv_name.setText(name)
            # 清理
            dialog.accept()
            dialog.deleteLater()

        # 校验命令是否合法
        elif not tool.is_valid_venv_create_command(self.config_created_parameter_line.text()):
            InfoBar.error(
                title="错误",
                content="创建命令不合法",
                parent=self,
                position=InfoBarPosition.TOP
            )

        else:
            try:
                # 彗星拖尾不确定进度环
                Comet_dialog = CometTailIndeterminateProgressRingDialog("正在安装Venv...",self)
                Comet_dialog.show()

                # # 执行Venv批处理
                self.config_only_venv_thread_batch_processing = Threads.VenvBatchProcessing(self.config_created_parameter_line.text(),
                                                                                       self.config_created_using_CMD_instead_internal_creator_box.isChecked(),
                                                                                       self.config_keep_CMD_open_after_creation_box.isChecked())
                self.config_only_venv_thread_batch_processing.finished.connect(lambda :self.Venv_batch_only_processing_end(Comet_dialog,self.config_only_venv_thread_batch_processing))
                self.config_only_venv_thread_batch_processing.update_title.connect(lambda title:Comet_dialog.label.setText(title))
                self.config_only_venv_thread_batch_processing.error.connect(lambda err: self.batch_error(err,Comet_dialog,self.config_only_venv_thread_batch_processing))
                self.config_only_venv_thread_batch_processing.start()
            except Exception as a:
                print(a)

    # Venv批处理创建完成
    def Venv_batch_only_processing_end(self,dialog,thread):
        try:
            # 清理
            dialog.accept()
            dialog.deleteLater()
            thread.deleteLater()

            # 添加到配置
            dir_path = self.config_venv_Loca_line.text()
            # /\结尾
            if self.config_venv_Loca_line.text().endswith("/") or self.config_venv_Loca_line.text().endswith("\\"):
                cfg_path = self.config_venv_Loca_line.text()+"pyvenv.cfg"
            else:
                cfg_path = self.config_venv_Loca_line.text() + "/pyvenv.cfg"
            # 查找基础环境版本
            venv_version = JCP.get("config.json",["python",os.path.dirname(self.config_base_python_box.text()),"version"],"Python")

            JCP.update(
                "config.json",
                ["venv",dir_path],
                {
                    "name": self.config_venv_name.text(), # 名称
                    "python":self.config_base_python_box.text() , # 基础解释器
                    "cfg_file": cfg_path, # cfg配置文件
                    "dir": dir_path, # venv目录
                    "start_parameter": self.config_startup_parameters_line.text(),# 启动参数
                    "include-system-site-packages": self.config_inherits_global_site_software_packages_box.isChecked(),# 全局开关
                    "version": venv_version # 版本
                })
            InfoBar.success(
                title="完成",
                content=f"虚拟环境创建完成",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )

            self.reset_config_venv() # 重置
            self.update_venv() # 更新虚拟环境

            # 播放音效 操作完成音效未禁用
            if self.play_sound and not self.play_sound_operation_completed:
                BSP.play("OperationCompleted")

        except Exception as a:
            print(a)

    # 配置创建虚拟环境
    def config_create_venv(self):
        # 基础解释器是否存在
        if not os.path.exists(self.config_base_python_box.text()):
            InfoBar.error(
                title="错误",
                content="基础解释器不存在",
                parent=self,
                position=InfoBarPosition.TOP
            )
        # 是否是空路径
        elif self.config_venv_Loca_line.text() == "":
            dialog = Dialog("提示","安装路径为空 是否将虚拟环境安装在VEM下的.venvs文件夹中")

            if dialog.exec():
                # 获取工作目录下的venvs和防重名
                path = tool.get_unique_name(os.getcwd()+"\\.venvs","venv")
                name = os.path.basename(path)
                self.config_venv_Loca_line.setText(path)
                self.config_venv_name.setText(name)
            # 清理
            dialog.accept()
            dialog.deleteLater()
        # 配置是否存在
        elif self.config_file_box.text() == "":
            InfoBar.error(
                title="错误",
                content="配置文件不存在",
                parent=self,
                position=InfoBarPosition.TOP
            )
        # 校验命令是否合法
        elif not tool.is_valid_venv_create_command(self.config_created_parameter_line.text()):
            InfoBar.error(
                title="错误",
                content="创建命令不合法",
                parent=self,
                position=InfoBarPosition.TOP
            )

        else:
            try:
                # 处理配置文件
                config_cmd = JCP.get("config.json",["config",self.config_file_box.text(),"older_list"],[])

                # 彗星拖尾不确定进度环
                Comet_dialog = CometTailIndeterminateProgressRingDialog("安装Venv...",self)
                Comet_dialog.show()

                # 使用CMD
                if self.config_created_using_CMD_instead_internal_creator_box.isChecked():
                    # 执行Venv批处理
                    self.config_venv_thread_batch_processing = Threads.VenvBatchProcessing(self.config_created_parameter_line.text(),
                                                                                           True,self.config_keep_CMD_open_after_creation_box.isChecked(),config_cmd,
                                                                                           activate_path=self.config_startup_parameters_line.text())
                    self.config_venv_thread_batch_processing.finished.connect(lambda :self.Venv_batch_only_processing_end(Comet_dialog,self.config_venv_thread_batch_processing,))
                    self.config_venv_thread_batch_processing.update_title.connect(lambda title:Comet_dialog.label.setText(title))
                    self.config_venv_thread_batch_processing.error.connect(lambda err: self.batch_error(err,Comet_dialog,self.config_venv_thread_batch_processing))
                    self.config_venv_thread_batch_processing.start()
                # 使用创建器
                else:
                    self.config_venv_thread_batch_processing = Threads.VenvBatchProcessing(self.config_created_parameter_line.text(),False,False)
                    self.config_venv_thread_batch_processing.finished.connect(lambda :self.Venv_batch_only_processing_end(Comet_dialog,self.config_venv_thread_batch_processing))
                    self.config_venv_thread_batch_processing.finished.connect(lambda :self.console_config_venv(config_cmd))
                    self.config_venv_thread_batch_processing.update_title.connect(lambda title:Comet_dialog.label.setText(title))
                    self.config_venv_thread_batch_processing.error.connect(lambda err: self.batch_error(err,Comet_dialog,self.config_venv_thread_batch_processing))
                    self.config_venv_thread_batch_processing.start()

            except Exception as a:
                print(a)

    # 控制台配置虚拟环境
    def console_config_venv(self,config_com):
        # 虚拟环境CMD模式
        if self.auto_config_model == "虚拟环境":
            dialog = Dialog("配置提示", "注意! 虚拟环境会自动进入环境 确保配置命令需要在环境中运行\n\n配置命令准备完毕\n\n是否将虚拟环境开机 开始自动配置虚拟环境", self)
            if dialog.exec():
                self.stackedWidget.setCurrentWidget(self.VenvManage)  # 直接跳转到控制台
                # 选中树枝下最后一个环境
                self.venv_tree.setCurrentItem(self.venv_tree.topLevelItem(0).child(self.venv_tree.topLevelItem(0).childCount() - 1))

                # 强制开机 当前环境配置时开机 并不会手动开机
                self.power_on_off()

                # 解禁电源按钮
                self.cmd_power_button.setEnabled(True)
                # 解禁图钉按钮
                self.pin_button.setEnabled(True)
                # 解禁预设脚本按钮
                self.preset_scripts_button.setEnabled(True)
                # 启用手动更新
                if self.enable_manual_update_CMD_switch:
                    # 解禁手动更新按钮
                    self.manual_update_button.setEnabled(True)
                # 启用CMD全屏
                if self.enable_cmd_full_screen_switch:
                    # 解禁全屏按钮
                    self.cmd_full_screen_button.setEnabled(True)

                # 使用同步 不叠加
                if self.venv_config_callback_duration == "sync" and not self.allow_overlay_callback_duration:
                    # 使用延时嵌入时长
                    delay = {"0ms": 0, "50ms": 50, "100ms": 100, "250ms": 250, "500ms": 500}.get(self.delay_cmd, 0)
                # 使用同步并叠加
                elif self.venv_config_callback_duration == "sync" and self.allow_overlay_callback_duration:
                    # 叠加
                    delay1 = {"0ms": 0, "50ms": 50, "100ms": 100, "250ms": 250, "500ms": 500}.get(self.delay_cmd, 0)
                    delay2 = {"0ms": 0, "10ms": 10, "50ms": 50, "100ms": 100,"250ms": 250,"500ms": 500}.get(self.pullback_duration, 0)
                    delay = delay1+delay2
                else:
                    # 使用指定的时长
                    delay = {"50ms": 50, "100ms": 100, "200ms": 200, "500ms": 500,"1000ms":1000}.get(self.venv_config_callback_duration,50)
                timer.singleShot(delay, lambda: configer())  # 常规

                def configer():
                    try:
                        for com in config_com:
                            self.select_cmd.send_command(com)
                    except Exception as e:
                        print(e)

            dialog.accept()
            dialog.deleteLater()

        # 控制台模式
        elif self.auto_config_model == "控制台":
            dialog = Dialog("配置提示", "注意! 控制台不会自动进入环境 确保配置命令不需要在环境中运行 \n创建配置控制台弹窗仅会出现一次 请确保控制台能成功创建\n\n配置命令准备完毕\n\n是否激活控制台 开始自动配置虚拟环境", self)
            if dialog.exec():
                self.stackedWidget.setCurrentWidget(self.Console) # 直接跳转到控制台
                cmd = self.console_on() # 激活控制台

                # 是否创建成功
                if cmd:
                    # 控制台配置命令延时回调
                    delay = {"50ms": 50, "100ms": 100, "200ms": 200, "500ms": 500, "1000ms": 1000}.get(self.console_config_callback_duration, 50)
                    timer.singleShot(delay, lambda: configer())  # 常规

                    def configer():
                        try:
                            for com in config_com:
                                self.select_console.send_command(com)
                        except Exception as a:
                            print(a)

            dialog.accept()
            dialog.deleteLater()













    # 初始化导航栏下载徽章
    def init_download_badge(self):
        self.downloadBadge = InfoBadge.attension(
            0,
            parent=self.navigationInterface_DownloadList.parent(),
            target=self.navigationInterface_DownloadList,
            position=InfoBadgePosition.NAVIGATION_ITEM
        )
        # 假隐藏
        self.downloadBadge.setText("")
        transparent = QColor(0,0,0,0)  # 全主题透明
        self.downloadBadge.setCustomBackgroundColor(transparent, transparent)

    # 隐藏导航栏下载徽章
    def hide_download_badge(self):
        #  隐藏徽章
        self.downloadBadge.setText("")
        transparent = QColor(0,0,0,0)  # 全主题透明
        self.downloadBadge.setCustomBackgroundColor(transparent, transparent)

    # 重置下载
    def reset_download(self):
        self.download_version_combox.setText("")
        self.download_file_combox.setText("")
        self.direct_link_line.setText("")

    # 弹出下载列表
    def flyout_download_list(self):
        try:
            download_list_view = FlyoutView(
                title='下载列表',
                content="下载任务队列",
                isClosable=True
            )
            listwidget = ListWidget()
            listwidget.setFixedWidth(400)

            download_list_view.setFixedHeight(500)
            download_list_view.addWidget(listwidget)

            # 遍历下载列表
            for i in self.download_list:
                listwidget.addItem(i)

            w = Flyout.make(download_list_view, self.navigationInterface_DownloadList, self,aniType=FlyoutAnimationType.SLIDE_RIGHT)
            download_list_view.closed.connect(w.close)
        except Exception as a:
            print(a)

    # 立即下载
    def download_now(self):
        if self.download_version_combox.text() == "":
            InfoBar.error(title="错误",
                            content=f"版本为空",
                            parent=self,
                            position=InfoBarPosition.TOP
                            )
        elif self.download_file_combox.text() == "":
            InfoBar.error(title="错误",
                            content=f"文件为空",
                            parent=self,
                            position=InfoBarPosition.TOP
                            )
        elif self.direct_link_line.text() == "":
            InfoBar.error(title="错误",
                          content=f"直链为空",
                          parent=self,
                          position=InfoBarPosition.TOP
                          )

        else:
            try:
                dialog = ProgressBarDialog("下载中...")
                dialog.show()

                url = self.direct_link_line.text()
                filename = self.download_file_combox.text()
                save_dir = self.downloads_path

                self.download_python_thread = Threads.DownloadThread(url,filename,save_dir)
                self.download_python_thread.progress.connect(dialog.progress_bar.setValue)
                self.download_python_thread.progress.connect(lambda s:dialog.label.setText(f"下载中 {str(s)}%..."))
                self.download_python_thread.speed.connect(dialog.label_R.setText)
                self.download_python_thread.error.connect(lambda s: self.uninstall_venv_error(s, dialog, self.download_python_thread))
                self.download_python_thread.finished.connect(lambda v: self.download_python_complete(dialog, self.download_python_thread, v))
                self.download_python_thread.start()
            except Exception as a:
                print(a)

    # 下载完成
    def download_python_complete(self,dialog,thread,v):
        dialog.accept()
        dialog.deleteLater()
        thread.deleteLater()

        self.reset_download() # 重置

        InfoBar.success(title="成功",
                      content=f"下载完成 保存至{v}",
                      parent=self,
                      position=InfoBarPosition.TOP,
                      duration=1500
                      )

        # 播放音效 下载完成音效未禁用
        if self.play_sound and not self.play_sound_download_complete:
            BSP.play("DownloadComplete")

    # 初始化下载器
    def init_download_manager(self):
        self.download_manager_thread = Threads.DownloadManager(self.downloads_path,int(self.max_parallel_download)) # 多任务下载管理器 最大并行下载数
        self.download_manager_thread.error.connect(lambda i,s: InfoBar.error(title="错误",content=f"任务{i}错误 {s}",parent=self,position=InfoBarPosition.TOP,duration=1500))
        self.download_manager_thread.finished.connect(lambda i,s:self.download_manager_python_complete(i,s))

    # 下载器下载完成
    def download_manager_python_complete(self,i,s):

        self.download_list.remove(os.path.basename(s))
        self.update_download_badge("-") # 减一任务

        InfoBar.success(title="成功",
                      content=f"任务{i}下载完成 保存至{s}",
                      parent=self,
                      position=InfoBarPosition.TOP,
                      duration=1500
                      )

        # 播放音效 下载完成音效未禁用
        if self.play_sound and not self.play_sound_download_complete:
            BSP.play("DownloadComplete")








if __name__ == "__main__":
    # 加入池
    JCP.load("config.json")

    # 创建翻译器
    translator = FluentTranslator(QLocale(QLocale.Chinese, QLocale.China))

    #尝试启用 OpenGL 或 ANGLE 后端（视显卡驱动而定，有时能显著提升 Fluent 效果性能）
    #app.setAttribute(Qt.AA_UseSoftwareOpenGL, False)

    # 共享 OpenGL 对象
    #QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    # 解决同时使用 Dialog 和 FluentWindow 可能导致窗口无法拉伸
    # Dialog 和 MessageBox 一同使用导致焦点残留存在
    # 焦点统一修复
    # 禁止创建原生控件同级窗口
    if JCP.get("config.json",["setting","prohibit_creating_native_control_windows_same_level"],False):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

    # 启用DPI缩放
    if JCP.get("config.json", ["setting","DPI_zoom"],False):
        # 启用高DPI缩放
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # 启用非整数缩放
    if JCP.get("config.json", ["setting","DPI_non_int_zoom"], False):
        # 支持非整数缩放比
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # 使用高 DPI 像素映射
    if JCP.get("config.json", ["setting","high_DPI_pixel_mapping"], False):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication([])

    # 安装翻译器
    app.installTranslator(translator)

    # 主题
    Theme_Model = JCP.get("config.json", ["setting","theme_model"],"LIGHT")

    setTheme(tool.str_to_theme(Theme_Model))

    # 自动强调色模式 默认自动
    if not JCP.get("config.json", ["setting","theme_color_auto"],True):
            setThemeColor(JCP.get("config.json", ["setting","theme_color"], "#ff009faa"))
    mainWin = MainUI()

    transition_duration = JCP.get("config.json", ["setting","transition_duration"],"0ms")
    duration = {"0ms": 0, "10ms": 10, "20ms": 20, "30ms": 30}.get(transition_duration,0)
    # 延时显示 解决Win7窗口过渡
    timer = QTimer()
    if JCP.get("config.json", ["setting","full_screen_after_startup"],False):
        timer.singleShot(duration, lambda: mainWin.showFullScreen()) # 启动后全屏
    elif JCP.get("config.json", ["setting","maximize_after_startup"],False):
        timer.singleShot(duration, lambda: mainWin.showMaximized()) # 启动后最大化
    else:
        timer.singleShot(duration, lambda: mainWin.show()) # 常规

    sys.exit(app.exec_())

# ff29f1ff
# ff009faa

# 在启动页面关闭时 执行 强制关闭 拒绝关闭 隐藏控制按钮

# 紧急修复 和一次性通知

# 内存泄漏调试器
# objgraph.show_growth()

# 背景音乐 枚举值 MUSIC

#downloadBadge 徽章终点位置

#table.verticalHeader().hide() # 隐藏表头 / 表格头图标

# 环境表格更新是否联动环境树
# 编辑是否继承

# 备份与恢复 公告 重置
# 内部信息

# 去掉外部cmd创建 配置创建后续待验证

# 禁用侧边栏指示器滑动动画
# self.navigationInterface.setIndicatorAnimationEnabled(False)

# 自定义背景颜色
# self.setCustomBackgroundColor(QColor(73, 156, 84), QColor(25, 33, 42))

# from BlurWindow.blurWindow import GlobalBlur 透明亚克力
# GlobalBlur(self.winId(),Acrylic=True,Dark=True, QWidget=self)

# 窗口自定义分辨率

# CMD std流历史 当前cmd详情

# 全局控制台 使用持续嵌入 意外退出重启控制台

# 各个cmd 控制台状态 加入图表

# 选择配置文件优先 APPDATA还是工作目录的配置

# 是否允许回调时长叠加

# 徽章跟随强调色

# 工作站工作模式 源码/程序/虚拟环境

# 自动配置查找环境 和 依据树查找cmd改为用 item data存的唯一值

# 读取版本信息
# JCP.get("config.json", ["info", "version"], "LIGHT")

# 控制台自动配置名称
# 控制台自动创建

# 启动页面阴影