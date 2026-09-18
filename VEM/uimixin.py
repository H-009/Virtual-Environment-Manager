from __future__ import annotations

from MetaverseSDK.MetaverseTool.Config.JsonConfigPool import JCP
from MetaverseSDK.MetaverseUI.MCore.MPool.MSvgIconPool import SIP
from MetaverseSDK.MetaverseUI.MFluentWidgets.MCard import HorizontalFoldCard
from MetaverseSDK.MetaverseUI.MFluentWidgets.MColorPickerButton import NoMaskColorPickerButton
from MetaverseSDK.MetaverseUI.MFluentWidgets.MLayoutSettingCard import LayoutSettingCard, LayoutSwitchButtonSettingCard, \
    LayoutHyperlinkSettingCard, LayoutDangerButtonSettingCard
from MetaverseSDK.MetaverseUI.MFluentWidgets.MTableWidget import RoundedTableListWidget
from MetaverseSDK.MetaverseUI.MWidgets.MStackedWidget import PopUpAniUpDownStackedWidget, PageUpDownStackedWidget, \
    PageLeftRightStackedWidget
from MetaverseSDK.MetaverseUI.MFluentWidgets.MTreeWidget import AllKeyProhibitedTreeWidget
from MetaverseSDK.MetaverseUI.MGui.MValidator import PromotionValidator, OperatorValidator, PromotionPlaceholderValidator
from MetaverseSDK.MetaverseUI.MWidgets.MLabel import HyperlinkFileLabel
from MetaverseSDK.MetaverseUI.MReviseWidgets.MLabel import BodyLabel, CaptionLabel,TitleLabel
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QHeaderView, QSizePolicy, QSpacerItem, QGridLayout
from qfluentwidgets import FluentIcon, SimpleCardWidget,EditableComboBox, ListWidget, IconWidget, ToolButton, \
    PopUpAniStackedWidget, Pivot,LineEdit, SegmentedWidget, PushButton, ComboBox, CheckBox, TextEdit, \
    SmoothScrollArea,SwitchButton, getFont
from typing import TYPE_CHECKING

import tool
from MetaverseSDK.MetaverseResource.MetaverseFluentIcon import MetaverseFluentIcon

from qfluentwidgets import __version__ as QFW__version__
from PyQt5.QtCore import QT_VERSION_STR as QT__version__
from MetaverseSDK import __version__ as SDK__version__

# 资源文件
import MetaverseSDK.MetaverseResource.MetaverseQRC

if TYPE_CHECKING:
    from VEM import MainUI
    _MixinBase = MainUI   # 类型检查时 MainUI
else:
    _MixinBase = object   # 运行时 object

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QHBoxLayout,QVBoxLayout, QWidget

from qfluentwidgets import PrimaryPushButton,SingleDirectionScrollArea


class UiMixin(_MixinBase):
    # 初始化环境管理
    def init_venv_manage(self):
        # 嵌入垂直布局
        vlayout = QHBoxLayout(self.VenvManage)

        # 树状图卡片
        tree_card = SimpleCardWidget()
        tree_card_vlayout = QVBoxLayout()
        tree_card.setLayout(tree_card_vlayout)
        tree_card.setMaximumWidth(300)  # 最大宽度
        tree_card.setMinimumWidth(200)  # 最小允许宽度
        # 创建树状表
        self.venv_tree = AllKeyProhibitedTreeWidget()
        self.venv_tree.clicked.connect(lambda index: self.select_venv_item(index))
        # 隐藏表头
        self.venv_tree.setHeaderHidden(True)
        # 添加树状图
        tree_card_vlayout.addWidget(BodyLabel("环境树"))
        tree_card_vlayout.addWidget(self.venv_tree)

        # CMD环境控制台卡片
        cmd_venv_card = SimpleCardWidget()
        cmd_venv_card_vlayout = QVBoxLayout()
        cmd_venv_card.setLayout(cmd_venv_card_vlayout)
        cmd_venv_card.setMinimumWidth(700)  # 最小宽度

        # 创建CMD控制台子卡片
        cmd_console_card = SimpleCardWidget()
        cmd_console_card_vlayout = QHBoxLayout()
        cmd_console_card.setFixedHeight(50)  # 锁死高度
        cmd_console_card.setLayout(cmd_console_card_vlayout)
        cmd_venv_card_vlayout.addWidget(cmd_console_card)
        # 电源按钮
        self.cmd_power_button = ToolButton()
        self.cmd_power_button.setIcon(self.PLAY_SOLID_icon)
        self.cmd_power_button.clicked.connect(self.power_on_off)
        cmd_console_card_vlayout.addWidget(self.cmd_power_button)
        # 禁用电源按钮
        self.cmd_power_button.setEnabled(False)

        # 图钉按钮
        self.pin_button = ToolButton()
        self.pin_button.setIcon(FluentIcon.PIN)
        self.pin_button.clicked.connect(self.switch_pin)
        cmd_console_card_vlayout.addWidget(self.pin_button)
        # 禁用图钉按钮
        self.pin_button.setEnabled(False)

        # 预设脚本按钮
        self.preset_scripts_button = ToolButton()
        self.preset_scripts_button.setIcon(FluentIcon.QUICK_NOTE)
        self.preset_scripts_button.clicked.connect(self.flyout_reset_scripts)
        cmd_console_card_vlayout.addWidget(self.preset_scripts_button)
        # 禁用预设脚本按钮
        self.preset_scripts_button.setEnabled(False)

        # 手动更新按钮
        self.manual_update_button = ToolButton()
        self.manual_update_button.setIcon(FluentIcon.SYNC)
        self.manual_update_button.clicked.connect(self.manual_update_CMD)
        cmd_console_card_vlayout.addWidget(self.manual_update_button)
        # 禁用手动更新按钮
        self.manual_update_button.setEnabled(False)

        # 控制栏弹簧
        cmd_console_card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

        # 全屏按钮
        self.cmd_full_screen_button = ToolButton()
        self.cmd_full_screen_button.setIcon(FluentIcon.FIT_PAGE)
        self.cmd_full_screen_button.clicked.connect(self.full_screen_CMD)
        cmd_console_card_vlayout.addWidget(self.cmd_full_screen_button)
        self.cmd_full_screen_button.setEnabled(False)

        # CMD堆叠窗口
        self.cmd_stackedwidget = PopUpAniStackedWidget()
        cmd_venv_card_vlayout.addWidget(self.cmd_stackedwidget)
        # 添加关机-虚拟环境页面
        card = SimpleCardWidget()
        card_vlayout = QVBoxLayout()
        icon_widget = IconWidget(FluentIcon.COMMAND_PROMPT)
        icon_widget.setFixedSize(150, 150)
        self.power_label_text = BodyLabel("没有选中的虚拟环境")
        card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        card_vlayout.addWidget(icon_widget, alignment=Qt.AlignHCenter)
        card_vlayout.addWidget(self.power_label_text, alignment=Qt.AlignHCenter)
        card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        card.setLayout(card_vlayout)
        self.cmd_stackedwidget.addWidget(card)
        # 添加关机-基础环境页面
        card = SimpleCardWidget()
        card_vlayout = QVBoxLayout()
        icon_widget = IconWidget(SIP.get("Python"))
        icon_widget.setFixedSize(150, 150)
        self.power_python_label_text = BodyLabel("没有选中的基础环境")
        self.power_python_path_label_text = BodyLabel("")
        card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        card_vlayout.addWidget(icon_widget, alignment=Qt.AlignHCenter)
        card_vlayout.addWidget(self.power_python_label_text, alignment=Qt.AlignHCenter)
        card_vlayout.addWidget(self.power_python_path_label_text, alignment=Qt.AlignHCenter)
        card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        card.setLayout(card_vlayout)
        self.cmd_stackedwidget.addWidget(card)
        # 添加关机-嵌入式环境页面
        card = SimpleCardWidget()
        card_vlayout = QVBoxLayout()
        icon_widget = IconWidget(self.ZIP_FOLDER_icon)
        icon_widget.setFixedSize(150, 150)
        self.power_emb_label_text = BodyLabel("没有选中的便携式环境")
        self.power_emb_path_label_text = BodyLabel("")
        self.power_start_script_path_label_text = BodyLabel("")
        card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        card_vlayout.addWidget(icon_widget, alignment=Qt.AlignHCenter)
        card_vlayout.addWidget(self.power_emb_label_text, alignment=Qt.AlignHCenter)
        card_vlayout.addWidget(self.power_emb_path_label_text, alignment=Qt.AlignHCenter)
        card_vlayout.addWidget(self.power_start_script_path_label_text, alignment=Qt.AlignHCenter)
        card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        card.setLayout(card_vlayout)
        self.cmd_stackedwidget.addWidget(card)

        # 图钉卡片
        self.pin_card = HorizontalFoldCard()
        pin_card_vlayout = QVBoxLayout()
        self.pin_card.setLayout(pin_card_vlayout)
        # 创建图钉列表
        self.pin_list = ListWidget()
        self.pin_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pin_list.customContextMenuRequested.connect(self.show_pin_list_menu)
        # 添加列表
        label = BodyLabel("图钉")
        label.setAlignment(Qt.AlignCenter)
        pin_card_vlayout.addWidget(label)
        pin_card_vlayout.addWidget(self.pin_list)

        # 嵌入主布局
        vlayout.addWidget(tree_card)
        vlayout.addWidget(cmd_venv_card)
        vlayout.addWidget(self.pin_card)

        # 更新表 自动
        self.update_venv_tree(True)

        # 更新图钉列表
        self.update_thumbtack_list()

    # 初始化控制台
    def init_console(self):
        # 嵌入垂直布局
        vlayout = QHBoxLayout(self.Console)

        # CMD环境控制台卡片
        cmd_venv_card = SimpleCardWidget()
        cmd_venv_card_vlayout = QVBoxLayout()
        cmd_venv_card.setLayout(cmd_venv_card_vlayout)
        cmd_venv_card.setMinimumWidth(600)  # 最小宽度
        cmd_venv_card.setMinimumWidth(800)  # 最大允许宽度

        # 创建CMD控制台子卡片
        cmd_console_card = SimpleCardWidget()
        cmd_console_card_vlayout = QVBoxLayout()
        cmd_console_card.setFixedWidth(50)  # 锁死宽度
        cmd_console_card.setLayout(cmd_console_card_vlayout)
        # 创建控制台按钮
        self.create_console_button = ToolButton()
        self.create_console_button.setIcon(self.SEND_FILL_icon)
        self.create_console_button.clicked.connect(self.console_on)
        cmd_console_card_vlayout.addWidget(self.create_console_button)
        # 销毁控制台按钮
        self.destroy_console_button = ToolButton()
        self.destroy_console_button.setIcon(self.BROOM_icon)
        self.destroy_console_button.clicked.connect(self.console_off)
        cmd_console_card_vlayout.addWidget(self.destroy_console_button)
        # 控制台列表按钮
        self.console_list_button = ToolButton()
        self.console_list_button.setIcon(FluentIcon.VIEW)
        self.console_list_button.clicked.connect(self.switch_console_list)
        cmd_console_card_vlayout.addWidget(self.console_list_button)
        # 手动更新按钮
        self.console_manual_update_button = ToolButton()
        self.console_manual_update_button.setIcon(FluentIcon.SYNC)
        self.console_manual_update_button.clicked.connect(self.manual_update_console)
        cmd_console_card_vlayout.addWidget(self.console_manual_update_button)
        # 禁用手动更新按钮
        self.console_manual_update_button.setEnabled(False)

        # 控制栏弹簧
        cmd_console_card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

        # 上一个终端按钮
        self.up_console_button = ToolButton()
        self.up_console_button.setIcon(FluentIcon.CARE_UP_SOLID)
        self.up_console_button.clicked.connect(self.up_console_item)
        cmd_console_card_vlayout.addWidget(self.up_console_button)
        # 下一个终端按钮
        self.down_console_button = ToolButton()
        self.down_console_button.setIcon(FluentIcon.CARE_DOWN_SOLID)
        self.down_console_button.clicked.connect(self.down_console_item)
        cmd_console_card_vlayout.addWidget(self.down_console_button)

        # 控制栏弹簧
        cmd_console_card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

        # 全屏按钮
        self.console_full_screen_button = ToolButton()
        self.console_full_screen_button.setIcon(FluentIcon.FIT_PAGE)
        self.console_full_screen_button.clicked.connect(self.full_screen_console)
        cmd_console_card_vlayout.addWidget(self.console_full_screen_button)
        self.console_full_screen_button.setEnabled(False)

        # 控制台堆叠窗口
        # 上下翻页堆叠控件
        if self.page_up_down_stacked_widget:
            self.console_stackedwidget = PageUpDownStackedWidget()
        # 上下弹出堆叠控件
        else:
            self.console_stackedwidget = PopUpAniUpDownStackedWidget()
        cmd_venv_card_vlayout.addWidget(self.console_stackedwidget)
        # 添加关机-虚拟环境页面
        card = SimpleCardWidget()
        card_vlayout = QVBoxLayout()
        icon_widget = IconWidget(MetaverseFluentIcon.Terminal)
        icon_widget.setFixedSize(150, 150)
        self.console_label_text = BodyLabel("没有激活的控制台")
        card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        card_vlayout.addWidget(icon_widget, alignment=Qt.AlignHCenter)
        card_vlayout.addWidget(self.console_label_text, alignment=Qt.AlignHCenter)
        card_vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        card.setLayout(card_vlayout)
        self.console_stackedwidget.addWidget(card)

        # 控制台列表卡片
        self.console_list_card = HorizontalFoldCard()
        tree_card_vlayout = QVBoxLayout()
        self.console_list_card.setLayout(tree_card_vlayout)
        self.console_list = ListWidget()  # 控制台列表
        self.console_list.clicked.connect(self.select_console_item)
        tree_card_vlayout.addWidget(BodyLabel("控制台列表"))  # 添加列表
        tree_card_vlayout.addWidget(self.console_list)

        # 嵌入主布局
        vlayout.addWidget(cmd_console_card)
        vlayout.addWidget(cmd_venv_card)
        vlayout.addWidget(self.console_list_card)

    # 初始化图钉
    def init_pin(self):
        # 嵌入垂直布局
        layout = QHBoxLayout(self.PIN_Manage)

        # 圆角表格列表控件
        self.pin_table = RoundedTableListWidget()

        # 设置行列
        self.pin_table.setColumnCount(1)
        self.pin_table.setRowCount(0)

        # 更新表格
        pin_json = JCP.get("config.json", ["pin"], [])  # 默认列表
        for key in pin_json:
            tool.table_add_row_1(self.pin_table, key)

        # 设置标头
        self.pin_table.setHorizontalHeaderLabels(['命令'])

        # 先全部按内容算
        header = self.pin_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # 自己平分剩余空间
        header.setSectionResizeMode(0, QHeaderView.Stretch)

        self.pin_table.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置policy
        # 连接右键菜单信号
        self.pin_table.customContextMenuRequested.connect(self.show_pin_table_menu)

        layout.addWidget(self.pin_table)

    # 初始化预设脚本
    def init_preset_scripts(self):
        # 嵌入垂直布局
        layout = QHBoxLayout(self.PresetScripts_Manage)

        # 圆角表格列表控件
        self.preset_scripts_table = RoundedTableListWidget()

        # 设置行列
        self.preset_scripts_table.setColumnCount(4)
        self.preset_scripts_table.setRowCount(0)

        # 更新表格
        preset_scripts_json = JCP.get("config.json", ["preset_scripts"], {})  # 默认空集合
        for value, key in preset_scripts_json.items():
            tool.table_add_row_4(self.preset_scripts_table, key["name"], key["description"], key["older"],
                                 str(key["parameters_dict"]), value)

        # 设置标头
        self.preset_scripts_table.setHorizontalHeaderLabels(['名称', '描述', '原始命令', '参数字典'])

        # 先全部按内容算
        header = self.preset_scripts_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # 最后一二列平分剩余空间
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.preset_scripts_table.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置policy
        # 连接右键菜单信号
        self.preset_scripts_table.customContextMenuRequested.connect(self.show_preset_scripts_table_menu)

        layout.addWidget(self.preset_scripts_table)

    # 初始化配置
    def init_config(self):
        # 嵌入垂直布局
        layout = QHBoxLayout(self.ConfigFile_Manage)

        # 圆角表格列表控件
        self.config_table = RoundedTableListWidget()

        # 设置行列
        self.config_table.setColumnCount(2)
        self.config_table.setRowCount(0)

        # 更新表格
        venv_json = JCP.get("config.json", ["config"], {})  # 默认空集合
        for value, key in venv_json.items():
            tool.table_add_row_2(self.config_table, key["name"], str(key["older_list"]), value)

        # 设置标头
        self.config_table.setHorizontalHeaderLabels(['名称', '命令列表'])

        # 先全部按内容算
        header = self.config_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # 最后一列平分剩余空间
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.config_table.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置policy
        # 连接右键菜单信号
        self.config_table.customContextMenuRequested.connect(self.show_config_table_menu)

        layout.addWidget(self.config_table)

    # 初始化虚拟环境
    def init_venv(self):
        # 嵌入垂直布局
        layout = QHBoxLayout(self.Venv)

        # 圆角表格列表控件
        self.venv_table = RoundedTableListWidget()

        # 设置行列
        self.venv_table.setColumnCount(7)
        self.venv_table.setRowCount(0)

        # 更新表格
        config_json = JCP.get("config.json", ["venv"], {})  # 默认空集合
        for value, key in config_json.items():
            tool.table_add_row_7(self.venv_table, key["name"], key["version"], key["dir"], key["cfg_file"],
                                 key['start_parameter'], key['python'], str(key["include-system-site-packages"]), value)

        # 设置标头
        self.venv_table.setHorizontalHeaderLabels(
            ['名称', '版本', '环境路径', '配置路径', '启动参数', '基础环境路径', '继承'])

        # 先全部按内容算
        header = self.venv_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # 四列平分剩余空间
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)

        self.venv_table.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置policy
        # 连接右键菜单信号
        self.venv_table.customContextMenuRequested.connect(self.show_venv_table_menu)

        layout.addWidget(self.venv_table)

    # 初始化便携式环境
    def init_emb(self):
        # 嵌入垂直布局
        layout = QHBoxLayout(self.EmbEnv)

        # 圆角表格列表控件
        self.emb_table = RoundedTableListWidget()

        # 设置行列
        self.emb_table.setColumnCount(5)
        self.emb_table.setRowCount(0)

        # 更新表格
        emb_json = JCP.get("config.json", ["emb"], {})  # 默认空集合
        for value, key in emb_json.items():
            tool.table_add_row_5(self.emb_table, key["name"], key["version"], key["dir"], key["start_script"],
                                 str(key["pth"]), value)

        # 设置标头
        self.emb_table.setHorizontalHeaderLabels(['名称', '版本', '环境路径', '启动脚本路径', '解锁'])

        # 先全部按内容算
        header = self.emb_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # 第三列吃掉剩余空间
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        self.emb_table.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置policy
        # 连接右键菜单信号
        self.emb_table.customContextMenuRequested.connect(self.show_emb_table_menu)

        layout.addWidget(self.emb_table)

    # 初始化基础环境
    def init_python(self):
        # 嵌入垂直布局
        layout = QHBoxLayout(self.BaseEnv)

        # 圆角表格列表控件
        self.python_table = RoundedTableListWidget()

        # 设置行列
        self.python_table.setColumnCount(4)
        self.python_table.setRowCount(0)

        # 更新表格
        python_json = JCP.get("config.json", ["python"], {})  # 默认空集合
        for value, key in python_json.items():
            tool.table_add_row_4(self.python_table, key["name"], key["version"], key["dir"], key["path"], value)

        # 设置标头
        self.python_table.setHorizontalHeaderLabels(['名称', '版本', '环境路径', '解释器'])

        # 先全部按内容算
        header = self.python_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # 两列平分剩余空间
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.python_table.setContextMenuPolicy(Qt.CustomContextMenu)  # 设置policy
        # 连接右键菜单信号
        self.python_table.customContextMenuRequested.connect(self.show_python_table_menu)

        layout.addWidget(self.python_table)

    # 初始化创建
    def init_created(self):
        # 嵌入垂直布局
        created_vlayout = QVBoxLayout(self.Created)

        # 导航卡片
        card = SimpleCardWidget()  # 简单卡片
        navigation_hBoxLayout = QHBoxLayout()  # 水平布局
        card.setLayout(navigation_hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        created_vlayout.addWidget(card)  # 嵌入到布局
        # 创建导航栏
        self.create_navigation = Pivot()  # 简单卡片
        self.create_navigation.addItem('虚拟环境', "虚拟环境")
        self.create_navigation.addItem('便携式环境', "便携式环境")
        self.create_navigation.addItem('基础环境', "基础环境")
        self.create_navigation.addItem('配置文件', "配置文件")
        self.create_navigation.addItem('预设脚本', "预设脚本")
        self.create_navigation.addItem('图钉', "图钉")
        self.create_navigation.setCurrentItem('虚拟环境')
        self.create_navigation.setFixedWidth(500)
        self.create_navigation.currentItemChanged.connect(self.created_stacked_update)
        navigation_hBoxLayout.addWidget(self.create_navigation)  # 添加

        # 堆叠创建窗口
        self.created_stacked = PageLeftRightStackedWidget()
        created_vlayout.addWidget(self.created_stacked)  # 嵌入到布局

        # 创建虚拟环境
        card = SimpleCardWidget()
        layout = QVBoxLayout()
        card.setLayout(layout)
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        title_layout = QHBoxLayout() # 标题布局
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        ico_widget = IconWidget(FluentIcon.IOT) # 图标
        ico_widget.setFixedSize(24,24)
        title_layout.addWidget(ico_widget)
        title_layout.addWidget(TitleLabel("创建虚拟环境"))
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        layout.addLayout(title_layout) # 添加标题布局
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        # 分段导航栏
        segmented = SegmentedWidget()
        segmented.addItem("现有","现有")
        segmented.addItem("新建","新建")
        segmented.addItem("配置","配置")
        segmented.setCurrentItem("现有") # 默认选中
        segmented.currentItemChanged.connect(self.segmented_stacked_update)
        layout.addWidget(segmented,alignment=Qt.AlignHCenter)
        # 子堆叠窗口
        self.segmented_venv_stacked = PopUpAniStackedWidget()
        layout.addWidget(self.segmented_venv_stacked)
        # 现有卡片
        existence_card = SimpleCardWidget()
        existence_card_layout = QVBoxLayout()
        existence_card.setLayout(existence_card_layout)
        venv_name_layout = QHBoxLayout() # 环境名称布局
        venv_name_layout.addWidget(BodyLabel("环境名称:"))
        self.venv_dir_name = LineEdit() # 行输入框
        self.venv_dir_name.setPlaceholderText("venv")
        venv_name_layout.addWidget(self.venv_dir_name)
        existence_card_layout.addLayout(venv_name_layout)
        venv_dir_layout = QHBoxLayout() # 环境目录布局
        venv_dir_layout.addWidget(BodyLabel("环境文件:"))
        self.venv_dir_line = LineEdit() # 行输入框
        self.venv_dir_line.setPlaceholderText("pyvenv.cfg")
        self.venv_dir_line.textChanged.connect(self.update_existence_start_parameter)
        venv_dir_layout.addWidget(self.venv_dir_line)
        self.venv_dir_button = ToolButton(FluentIcon.FOLDER) # 图标按钮
        self.venv_dir_button.clicked.connect(self.open_add_venv_window)
        venv_dir_layout.addWidget(self.venv_dir_button)
        existence_card_layout.addLayout(venv_dir_layout) # 添加子布局到父布局
        start_parameter_layout = QHBoxLayout() # 启动参数布局
        start_parameter_layout.addWidget(BodyLabel("启动参数:"))
        self.start_parameter_line = LineEdit() # 行输入框
        start_parameter_layout.addWidget(self.start_parameter_line)
        existence_card_layout.addLayout(start_parameter_layout) # 添加子布局到父布局
        button_layout = QHBoxLayout() # 按钮布局
        self.add_existence_venv = PrimaryPushButton("添加")# 添加现有按钮
        self.add_existence_venv.setFixedSize(100,30)
        self.add_existence_venv.clicked.connect(self.add_venv)
        self.reset_existence_venv = PushButton("重置")# 重置现有按钮
        self.reset_existence_venv.setFixedSize(100,30)
        self.reset_existence_venv.clicked.connect(lambda :(self.venv_dir_line.setText(""), self.start_parameter_line.setText(""),self.venv_dir_name.setText(""))) # 复合表达式
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))# 水平居中弹簧
        button_layout.addWidget(self.add_existence_venv)
        button_layout.addWidget(self.reset_existence_venv)
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))# 水平居中弹簧
        existence_card_layout.addLayout(button_layout)
        existence_card_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))# 底部弹簧
        self.segmented_venv_stacked.addWidget(existence_card) # 添加现有页
        # 新建卡片
        new_card = SimpleCardWidget()
        new_card_external_layout = QVBoxLayout() # 外部布局
        new_card_layout = QGridLayout() # 格栅布局
        new_card.setLayout(new_card_external_layout)
        new_card_external_layout.addLayout(new_card_layout) # 外部布局添加格栅布局
        self.venv_loca_name = LineEdit() # 行输入框
        self.venv_loca_name.setPlaceholderText("venv")
        new_card_layout.addWidget(BodyLabel("环境名称:"),0,0)
        new_card_layout.addWidget(self.venv_loca_name,0,1,1,2)
        self.venv_loca_line = LineEdit() # 行输入框
        self.venv_loca_line.setPlaceholderText(".venvs/venv")
        self.venv_loca_line.textChanged.connect(self.update_new_start_parameter) # 更新命令
        self.venv_loca_button = ToolButton(FluentIcon.FOLDER) # 图标按钮
        self.venv_loca_button.clicked.connect(self.open_install_venv_window)
        new_card_layout.setColumnStretch(1, 1) # 伸缩 第一列吃掉剩下空间
        new_card_layout.addWidget(BodyLabel("环境位置:"),1,0)
        new_card_layout.addWidget(self.venv_loca_line,1,1)
        new_card_layout.addWidget(self.venv_loca_button,1,2)
        self.base_python_box = ComboBox() # 下拉框
        self.base_python_box.clicked.connect(lambda :self.update_python_combox(self.base_python_box)) # 下拉列表点击信号
        self.base_python_box.activated.connect(lambda :self.base_python_box.setText(self.base_python_box.currentData())) # 选中信号
        self.base_python_box.activated.connect(self.update_venv_command) # 选中信号
        new_card_layout.addWidget(BodyLabel("基础解释器:"),2,0)
        new_card_layout.addWidget(self.base_python_box,2,1,1,2)
        self.inherits_global_site_software_packages_box = CheckBox() # 继承全局站点软件包 复选框
        self.inherits_global_site_software_packages_box.setText("继承全局站点软件包")
        self.inherits_global_site_software_packages_box.stateChanged.connect(lambda state: self.venv_command_batch(state,"--system-site-packages"))
        new_card_layout.addWidget(self.inherits_global_site_software_packages_box,3,0,1,3)  # 跨行
        self.try_using_symbolic_links_box = CheckBox() # 尝试使用符号链接 复选框
        self.try_using_symbolic_links_box.setText("尝试使用符号链接")
        self.try_using_symbolic_links_box.stateChanged.connect(lambda s:self.forced_file_copying_box.setEnabled(not s))
        self.try_using_symbolic_links_box.stateChanged.connect(lambda state: self.venv_command_batch(state,"--symlinks"))
        new_card_layout.addWidget(self.try_using_symbolic_links_box,4,0,1,3)  # 跨行
        self.forced_file_copying_box = CheckBox() # 强制复制文件 复选框
        self.forced_file_copying_box.setText("强制复制文件")
        self.forced_file_copying_box.stateChanged.connect(lambda s:self.try_using_symbolic_links_box.setEnabled(not s))
        self.forced_file_copying_box.stateChanged.connect(lambda state: self.venv_command_batch(state,"--copies"))
        new_card_layout.addWidget(self.forced_file_copying_box,5,0,1,3)  # 跨行
        self.clear_existing_directories_box = CheckBox() # 清空已存在目录 复选框
        self.clear_existing_directories_box.setText("清空已存在目录")
        self.clear_existing_directories_box.stateChanged.connect(lambda state: self.venv_command_batch(state,"--clear"))
        new_card_layout.addWidget(self.clear_existing_directories_box,6,0,1,3)  # 跨行
        self.upgrade_package_box = CheckBox() # 升级软件包 复选框
        self.upgrade_package_box.setText("升级软件包")
        self.upgrade_package_box.stateChanged.connect(lambda state: self.venv_command_batch(state,"--upgrade"))
        new_card_layout.addWidget(self.upgrade_package_box,7,0,1,3)  # 跨行
        self.skip_installing_pip_box = CheckBox() # 跳过安装pip 复选框
        self.skip_installing_pip_box.setText("跳过安装pip")
        self.skip_installing_pip_box.stateChanged.connect(lambda s:self.skip_installing_pip_mutual_exclusion(s))
        self.skip_installing_pip_box.stateChanged.connect(lambda state: self.venv_command_batch(state,"--without-pip"))
        new_card_layout.addWidget(self.skip_installing_pip_box,8,0,1,3)  # 跨行
        self.custom_prompts_prefix_box = CheckBox() # 自定义提示符前缀 复选框
        self.custom_prompts_prefix_box.setText("自定义提示符前缀")
        self.custom_prompts_prefix_box.stateChanged.connect(lambda s:self.prompts_prefix_line.setEnabled(s))
        self.custom_prompts_prefix_box.stateChanged.connect(self.update_venv_command)
        new_card_layout.addWidget(self.custom_prompts_prefix_box,9,0,1,3)  # 跨行
        self.prompts_prefix_line = LineEdit() # 行输入框
        self.prompts_prefix_line.setPlaceholderText("venv")
        self.prompts_prefix_line.setEnabled(False)
        self.prompts_prefix_line.textChanged.connect(self.update_venv_command)
        self.venv_startup_parameters_line = LineEdit() # 行输入框
        new_card_layout.addWidget(BodyLabel("提示符前缀:"),10,0) # 跨行
        new_card_layout.addWidget(self.prompts_prefix_line,10,1,1,3) # 跨行
        new_card_layout.addWidget(BodyLabel("启动参数:"),11,0) # 跨行
        new_card_layout.addWidget(self.venv_startup_parameters_line,11,1,1,3) # 跨行
        new_card_layout.addWidget(BodyLabel("创建命令:"),12,0)
        self.created_parameter_line = LineEdit() # 行输入框
        self.created_parameter_line.setPlaceholderText("python -m venv")
        new_card_layout.addWidget(self.created_parameter_line, 12, 1, 1, 2)  # 跨行
        button_layout = QHBoxLayout() # 按钮布局
        self.created_new_venv = PrimaryPushButton("创建")# 添加现有按钮
        self.created_new_venv.setFixedSize(100,30)
        self.created_new_venv.clicked.connect(self.create_venv)
        self.reset_new_venv = PushButton("重置")# 重置现有按钮
        self.reset_new_venv.setFixedSize(100,30)
        self.reset_new_venv.clicked.connect(self.reset_venv)
        button_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Fixed))# 间隔调小 防止撑开主窗口
        button_layout.addWidget(self.created_new_venv)
        button_layout.addWidget(self.reset_new_venv)
        button_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Fixed))# 水平居中弹簧
        new_card_external_layout.addLayout(button_layout)
        new_card_external_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))  # 底部弹簧
        self.segmented_venv_stacked.addWidget(new_card) # 添加新建页
        # 配置卡片
        config_card = SimpleCardWidget()
        config_card_external_layout = QVBoxLayout() # 外部布局
        config_card_layout = QGridLayout() # 格栅布局
        config_card.setLayout(config_card_external_layout)
        config_card_external_layout.addLayout(config_card_layout) # 外部布局添加格栅布局
        self.config_venv_name = LineEdit() # 行输入框
        self.config_venv_name.setPlaceholderText("venv")
        config_card_layout.addWidget(BodyLabel("环境名称:"),0,0)
        config_card_layout.addWidget(self.config_venv_name,0,1,1,2)
        self.config_venv_Loca_line = LineEdit() # 行输入框
        self.config_venv_Loca_line.setPlaceholderText(".venvs/venv")
        self.config_venv_Loca_line.textChanged.connect(self.update_config_start_parameter)
        self.config_venv_Loca_button = ToolButton(FluentIcon.FOLDER) # 图标按钮
        self.config_venv_Loca_button.clicked.connect(self.open_install_config_venv_window)
        config_card_layout.setColumnStretch(1, 1) # 伸缩 第一列吃掉剩下空间
        config_card_layout.addWidget(BodyLabel("环境位置:"),1,0)
        config_card_layout.addWidget(self.config_venv_Loca_line,1,1)
        config_card_layout.addWidget(self.config_venv_Loca_button,1,2)
        self.config_base_python_box = ComboBox() # 下拉列表
        self.config_base_python_box.clicked.connect(lambda :self.update_config_python_combox(self.config_base_python_box)) # 下拉列表点击信号
        self.config_base_python_box.activated.connect(lambda :self.config_base_python_box.setText(self.config_base_python_box.currentData())) # 选中信号
        self.config_base_python_box.activated.connect(self.update_config_venv_command)  # 选中信号
        config_card_layout.addWidget(BodyLabel("基础解释器:"),2,0)
        config_card_layout.addWidget(self.config_base_python_box,2,1,1,2) # 跨行
        self.config_inherits_global_site_software_packages_box = CheckBox() # 继承全局站点软件包 复选框
        self.config_inherits_global_site_software_packages_box.setText("继承全局站点软件包")
        self.config_inherits_global_site_software_packages_box.stateChanged.connect(lambda state: self.config_venv_command_batch(state,"--system-site-packages"))
        self.config_clear_existing_directories_box = CheckBox() # 清空已存在目录 复选框
        self.config_clear_existing_directories_box.setText("清空已存在目录")
        self.config_clear_existing_directories_box.stateChanged.connect(lambda state: self.config_venv_command_batch(state,"--clear"))
        layout_box = QHBoxLayout() # 组合布局
        layout_box.addWidget(self.config_inherits_global_site_software_packages_box)
        layout_box.addWidget(self.config_clear_existing_directories_box)
        config_card_layout.addLayout(layout_box,3,0,1,2)  # 跨行
        self.config_forced_file_copying_box = CheckBox() # 强制复制文件 复选框
        self.config_forced_file_copying_box.setText("强制复制文件")
        self.config_forced_file_copying_box.stateChanged.connect(lambda s: self.config_try_using_symbolic_links_box.setEnabled(not s))
        self.config_forced_file_copying_box.stateChanged.connect(lambda state: self.config_venv_command_batch(state,"--copies"))
        self.config_try_using_symbolic_links_box = CheckBox() # 尝试使用符号链接 复选框
        self.config_try_using_symbolic_links_box.setText("尝试使用符号链接")
        self.config_try_using_symbolic_links_box.stateChanged.connect(lambda s: self.config_forced_file_copying_box.setEnabled(not s))
        self.config_try_using_symbolic_links_box.stateChanged.connect(lambda state: self.config_venv_command_batch(state,"--symlinks"))
        layout_box2 = QHBoxLayout() # 组合布局
        layout_box2.addWidget(self.config_forced_file_copying_box)
        layout_box2.addWidget(self.config_try_using_symbolic_links_box)
        config_card_layout.addLayout(layout_box2,4,0,1,2)  # 跨行
        self.config_upgrade_package_box = CheckBox() # 升级软件包 复选框
        self.config_upgrade_package_box.setText("升级软件包")
        self.config_upgrade_package_box.stateChanged.connect(lambda s: self.config_skip_installing_pip_box.setEnabled(not s))
        self.config_upgrade_package_box.stateChanged.connect(lambda state: self.config_venv_command_batch(state,"--upgrade"))
        layout_box3 = QHBoxLayout() # 组合布局
        layout_box3.addWidget(self.config_upgrade_package_box)
        self.config_skip_installing_pip_box = CheckBox() # 跳过安装pip 复选框
        self.config_skip_installing_pip_box.setText("跳过安装pip")
        self.config_skip_installing_pip_box.stateChanged.connect(lambda s: self.config_upgrade_package_box.setEnabled(not s))
        self.config_skip_installing_pip_box.stateChanged.connect(lambda state: self.config_venv_command_batch(state,"--without-pip"))
        layout_box3.addWidget(self.config_skip_installing_pip_box)
        config_card_layout.addLayout(layout_box3,5,0,1,2)  # 跨行
        self.config_created_using_CMD_instead_internal_creator_box = CheckBox() # 使用外部CMD创建而非内部创建器 复选框
        self.config_created_using_CMD_instead_internal_creator_box.setText("使用外部CMD创建而非内部创建器")
        self.config_created_using_CMD_instead_internal_creator_box.stateChanged.connect(lambda s:self.use_ext_CMD_dynamic_disabled(s))
        config_card_layout.addWidget(self.config_created_using_CMD_instead_internal_creator_box,6,0,1,2) # 跨行
        self.config_keep_CMD_open_after_creation_box = CheckBox() # 使用外部CMD创建而非内部创建器 复选框
        self.config_keep_CMD_open_after_creation_box.setText("CMD创建后保持打开")
        self.config_keep_CMD_open_after_creation_box.setEnabled(False)
        config_card_layout.addWidget(self.config_keep_CMD_open_after_creation_box, 7, 0, 1, 2)  # 跨行
        self.config_custom_prompts_prefix_box = CheckBox() # 自定义提示符前缀 复选框
        self.config_custom_prompts_prefix_box.setText("自定义提示符前缀")
        self.config_custom_prompts_prefix_box.stateChanged.connect(lambda s:self.config_prompts_prefix_line.setEnabled(s))
        self.config_custom_prompts_prefix_box.stateChanged.connect(self.update_config_venv_command)
        config_card_layout.addWidget(self.config_custom_prompts_prefix_box,8,0,1,2)  # 跨行
        self.config_prompts_prefix_line = LineEdit() # 行输入框
        self.config_prompts_prefix_line.setPlaceholderText("venv")
        self.config_prompts_prefix_line.textChanged.connect(self.update_config_venv_command)
        config_card_layout.addWidget(BodyLabel("提示符前缀:"),9,0)
        config_card_layout.addWidget(self.config_prompts_prefix_line,9,1,1,2) # 跨行
        self.config_prompts_prefix_line.setEnabled(False)
        self.config_startup_parameters_line = LineEdit() # 行输入框
        config_card_layout.addWidget(BodyLabel("启动参数:"),10,0)
        config_card_layout.addWidget(self.config_startup_parameters_line,10,1,1,2) # 跨行
        self.config_created_parameter_line = LineEdit() # 行输入框
        self.config_created_parameter_line.setPlaceholderText("python -m venv")
        config_card_layout.addWidget(BodyLabel("创建命令:"),11,0)
        config_card_layout.addWidget(self.config_created_parameter_line,11,1,1,2) # 跨行
        self.config_file_box = ComboBox() # 下拉框
        self.config_file_box.clicked.connect(lambda :self.update_config_combox(self.config_file_box))
        self.config_file_box.activated.connect(lambda :self.config_file_box.setText(self.config_file_box.currentData()))
        config_card_layout.addWidget(BodyLabel("配置文件:"),12,0)
        config_card_layout.addWidget(self.config_file_box,12,1,1,2) # 跨行
        button_layout = QHBoxLayout() # 按钮布局
        self.created_and_config_venv = PrimaryPushButton("创建并配置")# 添加创建并配置按钮
        self.created_and_config_venv.setFixedSize(100,30)
        self.created_and_config_venv.clicked.connect(self.config_create_venv)
        self.config_only_created_venv = PushButton("仅创建")# 添加创建并配置按钮
        self.config_only_created_venv.setFixedSize(100,30)
        self.config_only_created_venv.clicked.connect(self.only_create_venv)
        self.reset_config_venv_button = PushButton("重置")# 重置配置按钮
        self.reset_config_venv_button.setFixedSize(100,30)
        self.reset_config_venv_button.clicked.connect(self.reset_config_venv)
        button_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Fixed))# 水平居中弹簧
        button_layout.addWidget(self.created_and_config_venv)
        button_layout.addWidget(self.config_only_created_venv)
        button_layout.addWidget(self.reset_config_venv_button)
        button_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Fixed))# 水平居中弹簧
        config_card_external_layout.addLayout(button_layout)
        config_card_external_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))  # 底部弹簧
        self.segmented_venv_stacked.addWidget(config_card) # 添加配置页
        self.created_stacked.addWidget(card) # 添页

        # 添加便携式环境
        card = SimpleCardWidget()
        layout = QVBoxLayout()
        card.setLayout(layout)
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        title_layout = QHBoxLayout() # 标题布局
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        ico_widget = IconWidget() # 图标
        ico_widget.setIcon(FluentIcon.ZIP_FOLDER)
        ico_widget.setFixedSize(24,24)
        title_layout.addWidget(ico_widget)
        title_layout.addWidget(TitleLabel("添加便携式环境"))
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        layout.addLayout(title_layout) # 添加标题布局
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        add_card = SimpleCardWidget()
        add_card_layout_base = QVBoxLayout()
        add_card_layout = QGridLayout() # 格栅布局
        add_card_layout_base.addLayout(add_card_layout)
        add_card.setLayout(add_card_layout_base)
        add_card_layout.addWidget(BodyLabel("嵌入包路径:"),0,0)
        self.add_emb_path_line = LineEdit()
        self.add_emb_path_line.setPlaceholderText("python-embed.zip")
        self.add_emb_path_button = ToolButton(FluentIcon.FOLDER)  # 图标按钮
        self.add_emb_path_button.clicked.connect(self.open_add_emb_window)
        add_card_layout.addWidget(self.add_emb_path_line,0,1)
        add_card_layout.addWidget(self.add_emb_path_button,0,2)
        add_card_layout.addWidget(BodyLabel("安装位置:"),1,0)
        self.add_emb_install_path_line = LineEdit()
        self.add_emb_install_path_line.setPlaceholderText(".embs/emb")
        self.add_emb_install_path_line.textChanged.connect(lambda text:self.custom_pip_acquisition_line.setText(f'curl https://bootstrap.pypa.io/get-pip.py -o "{text}/get-pip.py"'))
        self.add_emb_install_path_button = ToolButton(FluentIcon.FOLDER)  # 图标按钮
        self.add_emb_install_path_button.clicked.connect(self.open_install_emb_window)
        add_card_layout.addWidget(self.add_emb_install_path_line,1,1)
        add_card_layout.addWidget(self.add_emb_install_path_button,1,2)
        self.unlock_library_box = CheckBox() # 解锁第三方库 复选框
        self.unlock_library_box.setText("解锁第三方库")
        self.unlock_library_box.toggled.connect(lambda c:self.emb_batch("解锁第三方库",c))
        self.unlock_library_box.stateChanged.connect(lambda s:self.unlock_pth_dynamic_disabled(s))
        add_card_layout.addWidget(self.unlock_library_box,2,0,1,3) # 跨列
        self.create_startup_script_box = CheckBox() # 创建启动脚本 复选框
        self.create_startup_script_box.setText("创建启动脚本")
        self.create_startup_script_box.toggled.connect(lambda c:self.emb_batch("创建启动脚本",c))
        add_card_layout.addWidget(self.create_startup_script_box,3,0,1,3)
        self.creat_CMD_box = CheckBox() # 使用外部CMD创建 复选框
        self.creat_CMD_box.setText("使用外部CMD创建")
        self.creat_CMD_box.toggled.connect(lambda c:self.emb_batch("使用外部CMD创建",c)) # 双连接
        self.creat_CMD_box.toggled.connect(lambda s:self.CMD_dynamic_disabled(s))
        add_card_layout.addWidget(self.creat_CMD_box,4,0,1,3)
        self.creat_CMD_open_box = CheckBox() # CMD创建后保持打开 复选框
        self.creat_CMD_open_box.setText("CMD创建后保持打开")
        self.creat_CMD_open_box.toggled.connect(lambda c:self.emb_batch("CMD创建后保持打开",c))
        add_card_layout.addWidget(self.creat_CMD_open_box,5,0,1,3)
        self.creat_CMD_open_box.setEnabled(False)
        self.automatically_obtain_install_pip_box = CheckBox() # 自动获取pip 复选框
        self.automatically_obtain_install_pip_box.setText("自动获取pip并安装")
        self.automatically_obtain_install_pip_box.toggled.connect(lambda c:self.emb_batch("自动获取pip并安装",c))
        self.automatically_obtain_install_pip_box.stateChanged.connect(lambda s:self.automatic_acquisition_dynamic_disabled(s))
        self.automatically_obtain_install_pip_box.setEnabled(False) # 临时禁用
        add_card_layout.addWidget(self.automatically_obtain_install_pip_box,6,0,1,3)
        self.custom_pip_acquisition_box = CheckBox()
        self.custom_pip_acquisition_box.setText("自定义获取pip")
        self.custom_pip_acquisition_box.toggled.connect(lambda c:self.emb_batch("自定义获取pip",c))
        self.custom_pip_acquisition_box.stateChanged.connect(lambda s:self.custom_get_dynamic_disabled(s))
        self.custom_pip_acquisition_box.setEnabled(False) # 临时禁用
        add_card_layout.addWidget(self.custom_pip_acquisition_box,7,0,1,3)
        add_card_layout.addWidget(BodyLabel("pip获取命令:"),8,0)
        self.custom_pip_acquisition_line = LineEdit() # 自动安装pip 复选框
        self.custom_pip_acquisition_line.setText("curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py")
        self.custom_pip_acquisition_line.setPlaceholderText("curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py")
        self.custom_pip_acquisition_line.setEnabled(False)
        add_card_layout.addWidget(self.custom_pip_acquisition_line,8,1,1,3)
        self.custom_install_pip_box = CheckBox() # 自动安装pip 复选框
        self.custom_install_pip_box.setText("自定义安装pip")
        self.custom_install_pip_box.toggled.connect(lambda c:self.emb_batch("自定义安装pip",c))
        self.custom_install_pip_box.stateChanged.connect(lambda s:self.custom_install_dynamic_disabled(s))
        self.custom_install_pip_box.setEnabled(False) # 临时禁用
        add_card_layout.addWidget(self.custom_install_pip_box,9,0,1,3)
        add_card_layout.addWidget(BodyLabel("引导脚本位置:"),10,0)
        self.custom_install_pip_line = LineEdit() # 自动安装pip 复选框
        self.custom_install_pip_line.setPlaceholderText("C:\get-pip.py")
        self.custom_install_pip_line.setEnabled(False)
        add_card_layout.addWidget(self.custom_install_pip_line,10,1)
        self.custom_install_pip_path_button = ToolButton(FluentIcon.FOLDER)  # 图标按钮
        self.custom_install_pip_path_button.clicked.connect(self.open_add_get_pip_window)
        self.custom_install_pip_path_button.setEnabled(False)
        add_card_layout.addWidget(self.custom_install_pip_path_button,10,2)
        button_layout = QHBoxLayout() # 按钮布局
        self.unpack_activate_button = PrimaryPushButton("解包并激活")
        self.unpack_activate_button.setFixedSize(100,30)
        self.unpack_activate_button.clicked.connect(self.unpack_activate_emb)
        self.unpack_button = PushButton("仅解包")
        self.unpack_button.setFixedSize(100,30)
        self.unpack_button.clicked.connect(self.emb_unpack)
        self.reset_emb_button = PushButton("重置")
        self.reset_emb_button.setFixedSize(100,30)
        self.reset_emb_button.clicked.connect(self.reset_emb)
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中间隔弹簧
        button_layout.addWidget(self.unpack_activate_button)
        button_layout.addWidget(self.unpack_button)
        button_layout.addWidget(self.reset_emb_button)
        button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中弹簧
        add_card_layout_base.addLayout(button_layout)
        add_card_layout_base.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))  # 底部弹簧
        layout.addWidget(add_card)
        self.created_stacked.addWidget(card) # 添页

        # 添加基础环境
        card = SimpleCardWidget()
        layout = QVBoxLayout()
        card.setLayout(layout)
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        title_layout = QHBoxLayout() # 标题布局
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        ico_widget = IconWidget() # 图标
        ico_widget.setIcon(SIP.get("Python"))
        ico_widget.setFixedSize(24,24)
        title_layout.addWidget(ico_widget)
        title_layout.addWidget(TitleLabel("添加基础环境"))
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        layout.addLayout(title_layout) # 添加标题布局
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        add_card = SimpleCardWidget()
        add_card_layout_base = QVBoxLayout()
        add_card_layout = QHBoxLayout()
        add_card_layout_base.addLayout(add_card_layout)
        add_card.setLayout(add_card_layout_base)
        add_card_layout.addWidget(BodyLabel("解释器路径:"))
        self.add_python_path_line = LineEdit()
        self.add_python_path_line.setPlaceholderText("python.exe")
        self.add_python_path_button = ToolButton(FluentIcon.FOLDER)  # 图标按钮
        self.add_python_path_button.clicked.connect(self.open_add_python_window)
        add_card_layout.addWidget(self.add_python_path_line)
        add_card_layout.addWidget(self.add_python_path_button)
        button_layout = QHBoxLayout() # 按钮布局
        self.add_python_button = PrimaryPushButton("添加")
        self.add_python_button.setFixedSize(100,30)
        self.add_python_button.clicked.connect(self.add_python)
        self.reset_python_button = PushButton("重置")
        self.reset_python_button.setFixedSize(100,30)
        self.reset_python_button.clicked.connect(lambda :self.add_python_path_line.setText(""))
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中间隔弹簧
        button_layout.addWidget(self.add_python_button)
        button_layout.addWidget(self.reset_python_button)
        button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中弹簧
        add_card_layout_base.addLayout(button_layout)
        add_card_layout_base.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))  # 底部弹簧
        layout.addWidget(add_card)
        self.created_stacked.addWidget(card) # 添页

        # 创建配置文件
        card = SimpleCardWidget()
        layout = QVBoxLayout()
        card.setLayout(layout)
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        title_layout = QHBoxLayout() # 标题布局
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        ico_widget = IconWidget() # 图标
        ico_widget.setIcon(FluentIcon.DOCUMENT)
        ico_widget.setFixedSize(24,24)
        title_layout.addWidget(ico_widget)
        title_layout.addWidget(TitleLabel("新建配置文件"))
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        layout.addLayout(title_layout) # 添加标题布局
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        add_card = SimpleCardWidget()
        add_card_layout_base = QVBoxLayout()
        add_card_layout = QHBoxLayout()
        add_card.setLayout(add_card_layout_base)
        add_card_name_layout = QHBoxLayout()
        add_card_name_layout.addWidget(BodyLabel("名称:"))
        self.add_config_name_line = LineEdit() # 输入框
        self.add_config_name_line.setPlaceholderText("myconfig")
        self.add_config_name_line.setValidator(OperatorValidator(self.add_config_name_line,self)) # 设置验证器
        add_card_name_layout.addWidget(self.add_config_name_line)
        add_card_layout_base.addLayout(add_card_name_layout)
        add_card_layout.addWidget(BodyLabel("命令:"))
        self.add_config_older_line = LineEdit() # 命令输入框
        self.add_config_older_line.setPlaceholderText("pip list")
        add_card_layout.addWidget(self.add_config_older_line)
        self.add_config_older_line.setValidator(PromotionValidator(self.add_config_older_line,self)) # 设置正则验证器
        self.add_config_older_line.textEdited.connect(self.update_maximum_limit)
        self.one_older_max_label = BodyLabel("0/4000")
        add_card_layout.addWidget(self.one_older_max_label)
        self.add_config_older_button = PushButton("添加") # 按钮
        self.add_config_older_button.clicked.connect(self.add_config_older)
        add_card_layout.addWidget(self.add_config_older_button)
        self.card_config_older_text = TextEdit() # 命令卡片
        self.card_config_older_text.setReadOnly(True) # 半禁用
        add_card_layout_base.addLayout(add_card_layout)
        add_card_layout_base.addWidget(self.card_config_older_text)
        button_layout = QHBoxLayout() # 按钮布局
        self.create_config_older_button = PrimaryPushButton("创建")
        self.create_config_older_button.setFixedSize(100,30)
        self.create_config_older_button.clicked.connect(self.create_config)
        self.reset_config_older_button = PushButton("重置")
        self.reset_config_older_button.setFixedSize(100,30)
        self.reset_config_older_button.clicked.connect(self.reset_config_older)
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中间隔弹簧
        button_layout.addWidget(self.create_config_older_button)
        button_layout.addWidget(self.reset_config_older_button)
        button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中弹簧
        layout.addWidget(add_card)
        add_card_layout_base.addLayout(button_layout)
        self.created_stacked.addWidget(card) # 添页

        # 创建预设脚本
        card = SimpleCardWidget()
        layout = QVBoxLayout()
        card.setLayout(layout)
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        title_layout = QHBoxLayout() # 标题布局
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        ico_widget = IconWidget() # 图标
        ico_widget.setIcon(FluentIcon.QUICK_NOTE)
        ico_widget.setFixedSize(24,24)
        title_layout.addWidget(ico_widget)
        title_layout.addWidget(TitleLabel("新建预设脚本"))
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        layout.addLayout(title_layout) # 添加标题布局
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        comm_card = SimpleCardWidget()
        comm_layout = QVBoxLayout()
        comm_card.setLayout(comm_layout)
        layout_1 = QHBoxLayout()
        self.preset_scripts_name_line = LineEdit()
        self.preset_scripts_name_line.setPlaceholderText("mypreset")
        self.preset_scripts_name_line.setValidator(OperatorValidator(self.preset_scripts_name_line,self)) # 设置验证器
        layout_1.addWidget(BodyLabel("预设名称:"))
        layout_1.addWidget(self.preset_scripts_name_line)
        comm_layout.addLayout(layout_1)
        layout_2 = QHBoxLayout()
        self.preset_scripts_description_line = LineEdit()
        self.preset_scripts_description_line.setPlaceholderText("这个快捷脚本没有预设描述")
        layout_2.addWidget(BodyLabel("预设描述:"))
        layout_2.addWidget(self.preset_scripts_description_line)
        comm_layout.addLayout(layout_2)
        layout_3 = QHBoxLayout()
        self.preset_scripts_line = LineEdit()
        self.preset_scripts_line.setPlaceholderText("pip install %library")
        self.preset_scripts_line.setValidator(PromotionPlaceholderValidator(self.preset_scripts_line,self)) # 设置正则验证器
        self.preset_scripts_line.textChanged.connect(self.update_placeholder_list)
        layout_3.addWidget(BodyLabel("脚本命令:"))
        layout_3.addWidget(self.preset_scripts_line)
        self.preset_scripts_one_older_max_label = BodyLabel("0/2000")
        layout_3.addWidget(self.preset_scripts_one_older_max_label)
        comm_layout.addLayout(layout_3)
        self.preset_scripts_scrollArea = SingleDirectionScrollArea(orient=Qt.Vertical)  # 竖直方向
        self.preset_scripts_scrollArea.setWidgetResizable(True)  # 内部控件可调整大小
        self.preset_scripts_scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preset_scripts_scrollArea_card = SimpleCardWidget()
        self.preset_scripts_layout = QVBoxLayout()
        self.preset_scripts_layout.setAlignment(Qt.AlignTop) # 顶层布局策略
        self.preset_scripts_layout.addWidget(BodyLabel(f"所需0个参数")) # 默认文本
        self.preset_scripts_scrollArea_card.setLayout(self.preset_scripts_layout)
        # 滚动画布嵌入视图
        self.preset_scripts_scrollArea.setWidget(self.preset_scripts_scrollArea_card)
        self.preset_scripts_scrollArea.enableTransparentBackground() # 滚动区域全面透明
        comm_layout.addWidget(self.preset_scripts_scrollArea)
        layout.addWidget(comm_card)
        button_layout = QHBoxLayout() # 按钮布局
        self.create_preset_scripts_button = PrimaryPushButton("创建")
        self.create_preset_scripts_button.setFixedSize(100,30)
        self.create_preset_scripts_button.clicked.connect(self.create_preset_scripts)
        self.reset_preset_scripts_button = PushButton("重置")
        self.reset_preset_scripts_button.setFixedSize(100,30)
        self.reset_preset_scripts_button.clicked.connect(self.reset_preset_scripts)
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中间隔弹簧
        button_layout.addWidget(self.create_preset_scripts_button)
        button_layout.addWidget(self.reset_preset_scripts_button)
        button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中弹簧
        comm_layout.addLayout(button_layout)

        self.created_stacked.addWidget(card) # 添页

        # 创建图钉
        card = SimpleCardWidget()
        layout = QVBoxLayout()
        card.setLayout(layout)
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        title_layout = QHBoxLayout() # 标题布局
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        ico_widget = IconWidget() # 图标
        ico_widget.setIcon(FluentIcon.PIN)
        ico_widget.setFixedSize(24,24)
        title_layout.addWidget(ico_widget)
        title_layout.addWidget(TitleLabel("新建图钉"))
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        layout.addLayout(title_layout) # 添加标题布局
        # 标题间隔弹簧
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        pin_card = SimpleCardWidget()
        pin_layout = QVBoxLayout()
        pin_comm_layout = QHBoxLayout()
        pin_card.setLayout(pin_layout)
        self.pin_comm_line = LineEdit()
        self.pin_comm_line.setPlaceholderText("pip -help")
        self.pin_comm_line.setValidator(PromotionValidator(self.pin_comm_line,self)) # 设置正则验证器
        self.pin_comm_line.textEdited.connect(self.update_maximum_limit_pin)
        pin_comm_layout.addWidget(BodyLabel("图钉命令:"))
        pin_comm_layout.addWidget(self.pin_comm_line)
        self.pin_comm_one_older_max_label = BodyLabel("0/1000")
        pin_comm_layout.addWidget(self.pin_comm_one_older_max_label)
        pin_layout.addLayout(pin_comm_layout)
        button_layout = QHBoxLayout() # 按钮布局
        self.create_pin_comm_button = PrimaryPushButton("创建")
        self.create_pin_comm_button.setFixedSize(100,30)
        self.create_pin_comm_button.clicked.connect(self.create_pin_comm)
        self.reset_pin_comm_button = PushButton("重置")
        self.reset_pin_comm_button.setFixedSize(100,30)
        self.reset_pin_comm_button.clicked.connect(self.reset_pin_comm)
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中间隔弹簧
        button_layout.addWidget(self.create_pin_comm_button)
        button_layout.addWidget(self.reset_pin_comm_button)
        button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中弹簧
        pin_layout.addLayout(button_layout)
        pin_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))  # 底部弹簧
        layout.addWidget(pin_card)
        self.created_stacked.addWidget(card) # 添页

    # 初始化下载
    def init_download(self):
        # 嵌入垂直布局
        download_vlayout = QVBoxLayout(self.Download)

        # 内容卡片
        card = SimpleCardWidget()  # 简单卡片
        vBoxLayout = QVBoxLayout()  # 水平布局
        card.setLayout(vBoxLayout)  # 设置卡片布局
        download_vlayout.addWidget(card)  # 嵌入到布局

        # 标题间隔弹簧
        vBoxLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        title_layout = QHBoxLayout() # 标题布局
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        ico_widget = IconWidget() # 图标
        ico_widget.setIcon(MetaverseFluentIcon.DownloadList)
        ico_widget.setFixedSize(24,24)
        title_layout.addWidget(ico_widget)
        title_layout.addWidget(TitleLabel("下载"))
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed)) # 居中弹簧
        vBoxLayout.addLayout(title_layout) # 添加标题布局
        # 标题间隔弹簧
        vBoxLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 内容卡片
        card = SimpleCardWidget()
        card_layout = QVBoxLayout()

        card.setLayout(card_layout)
        download_version_layout = QHBoxLayout() # 下载版本布局
        download_version_layout.addWidget(BodyLabel("版本:"))
        self.download_version_combox = EditableComboBox()  # 可编辑下拉框
        download_version_layout.addWidget(self.download_version_combox,QSizePolicy.Expanding) # 吃掉剩下
        self.download_version_update_button = ToolButton()
        self.download_version_update_button.setIcon(FluentIcon.SYNC)
        self.download_version_update_button.clicked.connect(self.update_download_version)
        download_version_layout.addWidget(self.download_version_update_button)
        card_layout.addLayout(download_version_layout)
        download_file_layout = QHBoxLayout() # 下载文件布局
        download_file_layout.addWidget(BodyLabel("文件:"))
        self.download_file_combox = EditableComboBox()  # 可编辑下拉框
        self.download_file_combox.textChanged.connect(self.update_download_direct_link)
        download_file_layout.addWidget(self.download_file_combox,QSizePolicy.Expanding) # 吃掉剩下
        self.download_file_update_button = ToolButton()
        self.download_file_update_button.setIcon(FluentIcon.SYNC)
        self.download_file_update_button.clicked.connect(self.update_download_file)
        download_file_layout.addWidget(self.download_file_update_button)
        card_layout.addLayout(download_file_layout)
        direct_link_layout = QHBoxLayout() # 直链布局
        direct_link_layout.addWidget(BodyLabel("直链:"))
        self.direct_link_line = LineEdit()  # 可编辑下拉框
        direct_link_layout.addWidget(self.direct_link_line,QSizePolicy.Expanding) # 吃掉剩下
        card_layout.addLayout(direct_link_layout)
        button_layout = QHBoxLayout() # 按钮布局
        self.add_download_list = PrimaryPushButton("添加到下载列表")# 添加现有按钮
        self.add_download_list.setFixedSize(130,30)
        self.add_download_list.clicked.connect(self.update_download_queue)
        self.installation_download_now = PushButton("立即下载")# 添加现有按钮
        self.installation_download_now.setFixedSize(100,30)
        self.installation_download_now.clicked.connect(self.download_now)
        self.reset_existence_venv = PushButton("重置")# 重置现有按钮
        self.reset_existence_venv.setFixedSize(100,30)
        self.reset_existence_venv.clicked.connect(self.reset_download)
        self.reset_existence_venv.clicked.connect(lambda :(self.venv_dir_line.setText(""), self.start_parameter_line.setText(""))) # 复合表达式
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))# 水平居中弹簧
        button_layout.addWidget(self.add_download_list)
        button_layout.addWidget(self.installation_download_now)
        button_layout.addWidget(self.reset_existence_venv)
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))# 水平居中弹簧
        card_layout.addLayout(button_layout)
        card_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))# 底部弹簧
        vBoxLayout.addWidget(card) # 添加现有页

    # 初始化链接
    def init_link(self):
        # 嵌入垂直布局
        link_vlayout = QVBoxLayout(self.Link)

        # 内容卡片
        card = SimpleCardWidget()  # 简单卡片
        vBoxLayout = QVBoxLayout()  # 水平布局
        card.setLayout(vBoxLayout)  # 设置卡片布局
        link_vlayout.addWidget(card)  # 嵌入到布局

        # 标题间隔弹簧
        vBoxLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        title_layout = QHBoxLayout()  # 标题布局
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中弹簧
        ico_widget = IconWidget()  # 图标
        ico_widget.setIcon(MetaverseFluentIcon.Link)
        ico_widget.setFixedSize(24, 24)
        title_layout.addWidget(ico_widget)
        title_layout.addWidget(TitleLabel("链接"))
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中弹簧
        vBoxLayout.addLayout(title_layout)  # 添加标题布局
        # 标题间隔弹簧
        vBoxLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 分段导航栏
        segmented = SegmentedWidget()
        segmented.addItem("直链", "直链")
        segmented.addItem("索引", "索引")
        segmented.addItem("网站", "网站")
        segmented.setCurrentItem("直链")  # 默认选中
        segmented.currentItemChanged.connect(self.segmented_stacked_update)
        vBoxLayout.addWidget(segmented, alignment=Qt.AlignHCenter)

        # 子堆叠窗口
        self.segmented_download_stacked = PopUpAniStackedWidget()
        vBoxLayout.addWidget(self.segmented_download_stacked)

        # 现有卡片
        existence_card = SimpleCardWidget()
        existence_card_layout = QVBoxLayout()
        existence_card.setLayout(existence_card_layout)
        venv_dir_layout = QHBoxLayout()  # 环境目录布局
        venv_dir_layout.addWidget(BodyLabel("环境文件:"))
        self.venv_dir_line = LineEdit()  # 行输入框
        self.venv_dir_line.setPlaceholderText("pyvenv.cfg")
        self.venv_dir_line.textChanged.connect(self.update_existence_start_parameter)
        venv_dir_layout.addWidget(self.venv_dir_line)
        self.venv_dir_button = ToolButton(FluentIcon.FOLDER)  # 图标按钮
        self.venv_dir_button.clicked.connect(self.open_add_venv_window)
        venv_dir_layout.addWidget(self.venv_dir_button)
        existence_card_layout.addLayout(venv_dir_layout)  # 添加子布局到父布局
        start_parameter_layout = QHBoxLayout()  # 启动参数布局
        start_parameter_layout.addWidget(BodyLabel("启动参数:"))
        self.start_parameter_line = LineEdit()  # 行输入框
        start_parameter_layout.addWidget(self.start_parameter_line)
        existence_card_layout.addLayout(start_parameter_layout)  # 添加子布局到父布局
        button_layout = QHBoxLayout()  # 按钮布局
        self.add_existence_venv = PrimaryPushButton("添加")  # 添加现有按钮
        self.add_existence_venv.setFixedSize(100, 30)
        self.add_existence_venv.clicked.connect(self.add_venv)
        self.reset_existence_venv = PushButton("重置")  # 重置现有按钮
        self.reset_existence_venv.setFixedSize(100, 30)
        self.reset_existence_venv.clicked.connect(
            lambda: (self.venv_dir_line.setText(""), self.start_parameter_line.setText("")))  # 复合表达式
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 水平居中弹簧
        button_layout.addWidget(self.add_existence_venv)
        button_layout.addWidget(self.reset_existence_venv)
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 水平居中弹簧
        existence_card_layout.addLayout(button_layout)
        existence_card_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))  # 底部弹簧
        self.segmented_download_stacked.addWidget(existence_card)  # 添加现有页

    # 初始化安装
    def init_installation(self):
        # 嵌入垂直布局
        installation_vlayout = QVBoxLayout(self.Installation)

        # 内容卡片
        card = SimpleCardWidget()  # 简单卡片
        vBoxLayout = QVBoxLayout()  # 水平布局
        card.setLayout(vBoxLayout)  # 设置卡片布局
        installation_vlayout.addWidget(card)  # 嵌入到布局

        # 标题间隔弹簧
        vBoxLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))
        title_layout = QHBoxLayout()  # 标题布局
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中弹簧
        ico_widget = IconWidget()  # 图标
        ico_widget.setIcon(MetaverseFluentIcon.Installation)
        ico_widget.setFixedSize(24, 24)
        title_layout.addWidget(ico_widget)
        title_layout.addWidget(TitleLabel("安装"))
        title_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 居中弹簧
        vBoxLayout.addLayout(title_layout)  # 添加标题布局
        # 标题间隔弹簧
        vBoxLayout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 分段导航栏
        segmented = SegmentedWidget()
        segmented.addItem("静默安装", "静默安装")
        segmented.addItem("批量安装", "批量安装")
        segmented.setCurrentItem("静默安装")  # 默认选中
        segmented.currentItemChanged.connect(self.segmented_stacked_update)
        vBoxLayout.addWidget(segmented, alignment=Qt.AlignHCenter)

        # 子堆叠窗口
        self.segmented_download_stacked = PopUpAniStackedWidget()
        vBoxLayout.addWidget(self.segmented_download_stacked)

        # 现有卡片
        existence_card = SimpleCardWidget()
        existence_card_layout = QVBoxLayout()
        existence_card.setLayout(existence_card_layout)
        venv_dir_layout = QHBoxLayout()  # 环境目录布局
        venv_dir_layout.addWidget(BodyLabel("环境文件:"))
        self.venv_dir_line = LineEdit()  # 行输入框
        self.venv_dir_line.setPlaceholderText("pyvenv.cfg")
        self.venv_dir_line.textChanged.connect(self.update_existence_start_parameter)
        venv_dir_layout.addWidget(self.venv_dir_line)
        self.venv_dir_button = ToolButton(FluentIcon.FOLDER)  # 图标按钮
        self.venv_dir_button.clicked.connect(self.open_add_venv_window)
        venv_dir_layout.addWidget(self.venv_dir_button)
        existence_card_layout.addLayout(venv_dir_layout)  # 添加子布局到父布局
        start_parameter_layout = QHBoxLayout()  # 启动参数布局
        start_parameter_layout.addWidget(BodyLabel("启动参数:"))
        self.start_parameter_line = LineEdit()  # 行输入框
        start_parameter_layout.addWidget(self.start_parameter_line)
        existence_card_layout.addLayout(start_parameter_layout)  # 添加子布局到父布局
        button_layout = QHBoxLayout()  # 按钮布局
        self.add_existence_venv = PrimaryPushButton("添加")  # 添加现有按钮
        self.add_existence_venv.setFixedSize(100, 30)
        self.add_existence_venv.clicked.connect(self.add_venv)
        self.reset_existence_venv = PushButton("重置")  # 重置现有按钮
        self.reset_existence_venv.setFixedSize(100, 30)
        self.reset_existence_venv.clicked.connect(lambda: (self.venv_dir_line.setText(""), self.start_parameter_line.setText("")))  # 复合表达式
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 水平居中弹簧
        button_layout.addWidget(self.add_existence_venv)
        button_layout.addWidget(self.reset_existence_venv)
        button_layout.addItem(QSpacerItem(20, 50, QSizePolicy.Expanding, QSizePolicy.Fixed))  # 水平居中弹簧
        existence_card_layout.addLayout(button_layout)
        existence_card_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding))  # 底部弹簧
        self.segmented_download_stacked.addWidget(existence_card)  # 添加现有页

    # 初始化设置
    def init_setting(self):
        # 嵌入垂直布局
        self.setting_vlayout = QVBoxLayout(self.setting)
        # 标题布局
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 10, 0, 0)
        title_layout.addWidget(TitleLabel("设置"))
        self.setting_vlayout.addLayout(title_layout)

        # 由动画实现的平滑滚动区域代替
        if self.smooth_scrolling_area:
            # 平滑滚动画布
            self.setting_scrollArea = SmoothScrollArea()
        # 由平滑滚动区域代替
        else:
            # 滚动画布
            self.setting_scrollArea = SingleDirectionScrollArea(orient=Qt.Vertical)  # 竖直方向
        self.setting_scrollArea.setWidgetResizable(True)  # 内部控件可调整大小
        self.setting_scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setting_scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")  # 滚动区域透明

        # 设置视图
        self.setting_view = QWidget()
        self.setting_view.setStyleSheet("QWidget{background: transparent}")  # 视图透明
        self.setting_view_layout = QVBoxLayout(self.setting_view)  # 视图布局

        # 主题标题
        self.setting_view_layout.addWidget(BodyLabel("主题"))
        # 主题卡片
        card = SimpleCardWidget()  # 简单卡片
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.PALETTE)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("主题模式"))  # 文字标签
        contentLabel = CaptionLabel("设置配色方案")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        theme_model_combox = ComboBox()  # 下拉框
        theme_model_combox.setFixedWidth(120)
        theme_model_combox.addItems(["明亮", "黑暗", "自动"])
        theme_model_combox.setCurrentText(self.twist_theme_map[JCP.get("config.json", ["setting","theme_model"],"LIGHT")])# 默认选中
        theme_model_combox.currentTextChanged.connect(self.update_theme_model) # 等待初始化后绑定信号
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(theme_model_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 强调色卡片
        card = SimpleCardWidget()  # 简单卡片
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.HIGHTLIGHT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("强调色"))  # 文字标签
        contentLabel = CaptionLabel("设置主题强调色")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.select_color_button = NoMaskColorPickerButton(QColor(self.theme_color), '强调色', self,enableAlpha=True)  # 颜色选择器按钮
        self.select_color_button.setFixedWidth(120)
        self.select_color_button.colorChanged.connect(lambda color: self.update_theme_color(color.name()))
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.select_color_button)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 恢复默认强调色卡片
        card = SimpleCardWidget()  # 简单卡片
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.HIGHTLIGHT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("恢复默认强调色"))  # 文字标签
        contentLabel = CaptionLabel("恢复当前主题默认强调色")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        button = PushButton("恢复默认")
        button.setFixedWidth(120)
        button.clicked.connect(self.restore_default_color)
        vBoxLayout.addWidget(contentLabel)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(button)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 云母卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.TRANSPARENT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("云母效果"))  # 文字标签
        contentLabel = CaptionLabel("窗口和表面显示半透明")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.mica_effect_switch = SwitchButton()  # 强制刷新按钮
        self.mica_effect_switch.setChecked(self.mica_effect)
        self.mica_effect_switch.checkedChanged.connect(lambda key: self.update_mica_effect(key))
        self.mica_effect_switch.setFixedWidth(80)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.mica_effect_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 懒加载卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.LEAF)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("懒加载"))  # 文字标签
        contentLabel = CaptionLabel("延时加载完整主题")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.lazy_switch = SwitchButton()  # 强制刷新按钮
        self.lazy_switch.setChecked(self.lazy)
        self.lazy_switch.checkedChanged.connect(lambda key: self.update_lazy(key))
        self.lazy_switch.setFixedWidth(80)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.lazy_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 强制刷新标题
        self.setting_view_layout.addWidget(BodyLabel("强制刷新"))
        # 强制刷新卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.UPDATE)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("CMD强制刷新"))  # 文字标签
        contentLabel = CaptionLabel("切换CMD页面时启用强制刷新进行重绘")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.refresh_CMD_switch = SwitchButton()  # 强制刷新按钮
        self.refresh_CMD_switch.setChecked(self.mandatory_update_CMD_switch)
        self.refresh_CMD_switch.checkedChanged.connect(lambda key: self.refresh_CMD_update(key))
        self.refresh_CMD_switch.setFixedWidth(80)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.refresh_CMD_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 手动刷新卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.UPDATE)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("启用CMD手动刷新"))  # 文字标签
        contentLabel = CaptionLabel("允许手动进行CMD重绘")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.manual_CMD_switch = SwitchButton()  # 强制刷新按钮
        self.manual_CMD_switch.setChecked(self.enable_manual_update_CMD_switch)
        self.manual_CMD_switch.checkedChanged.connect(lambda key: self.update_manual_CMD(key))
        self.manual_CMD_switch.setFixedWidth(80)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.manual_CMD_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # CMD嵌入标题
        self.setting_view_layout.addWidget(BodyLabel("嵌入式CMD"))
        # CMD延时嵌入时长卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("CMD延时嵌入时长"))  # 文字标签
        contentLabel = CaptionLabel("防止CMD嵌入过快引发异常")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.themem_model_combox = ComboBox()  # 下拉框
        self.themem_model_combox.setFixedWidth(120)
        self.themem_model_combox.addItems(["0ms", "50ms", "100ms", "250ms", "500ms"])
        self.themem_model_combox.setCurrentText(self.delay_cmd)
        self.themem_model_combox.activated.connect(self.update_delay)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.themem_model_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # CMD自动进入环境卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("CMD自动进入环境"))  # 文字标签
        contentLabel = CaptionLabel("启动CMD自动进入当前虚拟环境")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.auto_enter_venv_switch = SwitchButton()  # 颜色选择器按钮
        self.auto_enter_venv_switch.setFixedWidth(80)
        self.auto_enter_venv_switch.setChecked(self.auto_enter_venv)
        self.auto_enter_venv_switch.checkedChanged.connect(self.update_auto_enter_venv)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.auto_enter_venv_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # CMD关机保护卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("CMD关机保护"))  # 文字标签
        contentLabel = CaptionLabel("关闭CMD时提醒是否关闭")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.wallpaper_switch = SwitchButton()  # 颜色选择器按钮
        self.wallpaper_switch.setFixedWidth(80)
        self.wallpaper_switch.setChecked(self.shutdown_protection_switch)
        self.wallpaper_switch.checkedChanged.connect(lambda key: self.shutdown_protection_update(key))
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.wallpaper_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # CMD生命监控频率卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("CMD监控频率"))  # 文字标签
        contentLabel = CaptionLabel("CMD生命周期监控频率")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.cmd_frequency_combox = ComboBox()  # 下拉框
        self.cmd_frequency_combox.setFixedWidth(120)
        self.cmd_frequency_combox.addItems(["0.5s", "1.0s", "2.0s", "5.0s"])
        self.cmd_frequency_combox.setCurrentText(self.frequency_cmd)
        self.cmd_frequency_combox.activated.connect(self.update_frequency)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.cmd_frequency_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 回调时长卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("回调时长"))  # 文字标签
        contentLabel = CaptionLabel("自动进入环境回调时长")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.pullback_duration_combox = ComboBox()  # 下拉框
        self.pullback_duration_combox.setFixedWidth(120)
        self.pullback_duration_combox.addItems(["0ms","10ms", "50ms", "100ms", "250ms","500ms"])
        self.pullback_duration_combox.setCurrentText(self.pullback_duration)
        self.pullback_duration_combox.activated.connect(self.update_auto_enter_venv_pullback_duration)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.pullback_duration_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # CMD被动关机卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("CMD被动关机"))  # 文字标签
        contentLabel = CaptionLabel("当有操作需要关闭CMD时是否自动决定")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.CMD_passive_shutdown_button = SwitchButton()  # 下拉框
        self.CMD_passive_shutdown_button.setFixedWidth(80)
        self.CMD_passive_shutdown_button.setChecked(self.CMD_passive_shutdown)
        self.CMD_passive_shutdown_button.checkedChanged.connect(self.update_CMD_passive_shutdown)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.CMD_passive_shutdown_button)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # CMD全屏卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("启用CMD全屏"))  # 文字标签
        contentLabel = CaptionLabel("允许CMD全屏独占显示")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.full_screen_CMD_switch = SwitchButton()  # 强制刷新按钮
        self.full_screen_CMD_switch.setChecked(self.enable_cmd_full_screen_switch)
        self.full_screen_CMD_switch.checkedChanged.connect(lambda key: self.update_full_screen_CMD(key))
        self.full_screen_CMD_switch.setFixedWidth(80)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.full_screen_CMD_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # CMD自动配置模式卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("CMD自动配置模式"))  # 文字标签
        contentLabel = CaptionLabel("内部创建器自动配置时调用的CMD")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.auto_config_model_combox = ComboBox()  # 下拉框
        self.auto_config_model_combox.setFixedWidth(120)
        self.auto_config_model_combox.addItems(["虚拟环境","控制台"])
        self.auto_config_model_combox.setCurrentText(self.auto_config_model)
        self.auto_config_model_combox.activated.connect(self.update_auto_config_model)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.auto_config_model_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 虚拟环境配置命令延时回调模式卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("虚拟环境配置回调时长"))  # 文字标签
        contentLabel = CaptionLabel("虚拟环境自动配置命令的延时回调时长")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.venv_config_callback_duration_combox = ComboBox()  # 下拉框
        self.venv_config_callback_duration_combox.setFixedWidth(120)
        self.venv_config_callback_duration_combox.addItems(["同步","50ms","100ms","200ms","500ms","1000ms"])
        self.venv_config_callback_duration_combox.setCurrentText(self.venv_config_callback_duration)
        self.venv_config_callback_duration_combox.activated.connect(self.update_venv_config_callback_duration)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.venv_config_callback_duration_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 允许虚拟环境配置叠加回调时长叠加卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("允许虚拟环境配置叠加回调时长"))  # 文字标签
        contentLabel = CaptionLabel("允许虚拟环境自动配置命令同步叠加延时回调时长")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.overlay_callback_duration_switch = SwitchButton()
        self.overlay_callback_duration_switch.setChecked(self.allow_overlay_callback_duration)
        self.overlay_callback_duration_switch.checkedChanged.connect(lambda key: self.update_allow_overlay_callback_duration(key))
        self.overlay_callback_duration_switch.setFixedWidth(80)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.overlay_callback_duration_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 控制台配置命令延时回调模式卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.COMMAND_PROMPT)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("控制台配置回调时长"))  # 文字标签
        contentLabel = CaptionLabel("控制台自动配置命令的延时回调时长")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.console_config_callback_duration_combox = ComboBox()  # 下拉框
        self.console_config_callback_duration_combox.setFixedWidth(120)
        self.console_config_callback_duration_combox.addItems(["50ms","100ms","200ms","500ms","1000ms"])
        self.console_config_callback_duration_combox.setCurrentText(self.console_config_callback_duration)
        self.console_config_callback_duration_combox.activated.connect(self.update_console_config_callback_duration)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.console_config_callback_duration_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 缩放标题
        self.setting_view_layout.addWidget(BodyLabel("缩放"))
        # 启用DPI缩放卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.ZOOM)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("开启DPI缩放"))  # 文字标签
        contentLabel = CaptionLabel("开启高DPI感知缩放")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.dpi_zoom_switch = SwitchButton()  # 开关按钮
        self.dpi_zoom_switch.setChecked(self.activated_dpi_zoom_switch)
        self.dpi_zoom_switch.setFixedWidth(80)
        self.dpi_zoom_switch.checkedChanged.connect(lambda key: self.update_dpi_zoom(key))
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.dpi_zoom_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 启用非整数缩放卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.ZOOM)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("启用非整数缩放"))  # 文字标签
        contentLabel = CaptionLabel("支持高DPI感知非整数缩放比")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.dpi_non_int_zoom_switch = SwitchButton()  # 开关按钮
        self.dpi_non_int_zoom_switch.setChecked(self.activated_dpi_non_int_zoom_switch)
        self.dpi_non_int_zoom_switch.setFixedWidth(80)
        self.dpi_non_int_zoom_switch.checkedChanged.connect(lambda key: self.update_dpi_non_int_zoom(key))
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.dpi_non_int_zoom_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 启用非整数缩放卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.ZOOM)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("启用高DPI像素映射"))  # 文字标签
        contentLabel = CaptionLabel("启用高DPI图像资源自动适配")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.high_DPI_pixel_mapping_switch = SwitchButton()  # 开关按钮
        self.high_DPI_pixel_mapping_switch.setChecked(self.high_DPI_pixel_mapping)
        self.high_DPI_pixel_mapping_switch.setFixedWidth(80)
        self.high_DPI_pixel_mapping_switch.checkedChanged.connect(lambda key: self.update_high_DPI_pixel_mapping(key))
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.high_DPI_pixel_mapping_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 窗口标题
        self.setting_view_layout.addWidget(BodyLabel("窗口"))
        # 启动时全屏卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.FULL_SCREEN)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("启动时全屏"))  # 文字标签
        contentLabel = CaptionLabel("启动时默认展开全屏")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.full_screen_startup_switch = SwitchButton()  # 开关按钮
        self.full_screen_startup_switch.setChecked(self.full_screen_startup_init_switch)
        self.full_screen_startup_switch.setFixedWidth(80)
        self.full_screen_startup_switch.checkedChanged.connect(lambda key: self.full_screen_startup(key))
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.full_screen_startup_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 启动后全屏卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.FULL_SCREEN)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("启动后全屏"))  # 文字标签
        contentLabel = CaptionLabel("启动后默认展开全屏")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.full_screen_after_startup_switch = SwitchButton()  # 开关按钮
        self.full_screen_after_startup_switch.setChecked(self.full_screen_after_startup_init_switch)
        self.full_screen_after_startup_switch.setFixedWidth(80)
        self.full_screen_after_startup_switch.checkedChanged.connect(lambda key: self.full_screen_after_startup(key))
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.full_screen_after_startup_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 启动后最大化卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.MINIMIZE)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("启动后最大化"))  # 文字标签
        contentLabel = CaptionLabel("启动后默认最大化窗口")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.maximize_after_startup_switch = SwitchButton()  # 开关按钮
        self.maximize_after_startup_switch.setChecked(self.maximize_after_startup_init_switch)
        self.maximize_after_startup_switch.setFixedWidth(80)
        self.maximize_after_startup_switch.checkedChanged.connect(lambda key: self.maximize_after_startup(key))
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.maximize_after_startup_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 启动页面动画标题
        self.setting_view_layout.addWidget(BodyLabel("启动页面"))
        # 设置启动页面动画时长卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        self.startup_animation_iconWidget = IconWidget()  # 启动动画图标界面
        self.startup_animation_iconWidget.setFixedSize(24, 24)
        self.update_set_startup_animation_duration_ico() # 更新图标
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("启动页面动画时长"))  # 文字标签
        contentLabel = CaptionLabel("程序初始化时的启动页面动画时长")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.startup_animation_duration_combox = ComboBox()  # 下拉框
        self.startup_animation_duration_combox.setFixedWidth(150)
        self.startup_animation_duration_combox.addItems(self.startup_animation_high+self.startup_animation_medium+self.startup_animation_off)
        self.startup_animation_duration_combox.setCurrentText(self.startup_animation_duration)
        self.startup_animation_duration_combox.activated.connect(lambda index:self.update_startup_animation_duration(index))
        hBoxLayout.addWidget(self.startup_animation_iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.startup_animation_duration_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 设置启动页面动画时长卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        self.startup_animation_iconWidget = IconWidget()  # 启动动画图标界面
        self.startup_animation_iconWidget.setFixedSize(24, 24)
        self.update_set_startup_ico_size_ico() # 更新图标
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("启动页面图标大小"))  # 文字标签
        contentLabel = CaptionLabel("程序初始化时的启动页面图标大小")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.startup_ico_size_combox = ComboBox()  # 下拉框
        self.startup_ico_size_combox.setFixedWidth(150)
        self.startup_ico_size_combox.addItems(self.startup_ico_list)
        self.startup_ico_size_combox.setCurrentText(self.startup_ico_size)
        self.startup_ico_size_combox.activated.connect(lambda index:self.update_startup_ico_size(index))
        hBoxLayout.addWidget(self.startup_animation_iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.startup_ico_size_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 下载标题
        self.setting_view_layout.addWidget(BodyLabel("下载"))
        # 关闭便携式环境的脱控通知卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.DOWNLOAD)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("下载路径"))  # 文字标签
        self.downloads_path_contentLabel = CaptionLabel(self.downloads_path)  # 字幕标签
        self.downloads_path_contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(self.downloads_path_contentLabel)
        button = PushButton("选择路径")
        button.setFixedWidth(120)
        button.clicked.connect(self.update_download_path)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(button)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 通知标题
        self.setting_view_layout.addWidget(BodyLabel("通知"))
        # 关闭便携式环境的脱控通知卡片
        card = LayoutSwitchButtonSettingCard(FluentIcon.RINGER, "关闭便携式环境的脱控通知", "关闭在创建便携式环境时的脱离控制通知")
        card.setChecked(self.close_emb_out_control_notification_switch)
        card.checkedChanged.connect(self.close_emb_out_control_notification)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 关闭自动决定下的CMD被动关机通知卡片
        card = LayoutSwitchButtonSettingCard(FluentIcon.RINGER, "关闭CMD被动关机通知", "关闭自动决定下的CMD被动关机通知")
        card.setChecked(self.disable_auto_CMD_passive_shutdown_notification)
        card.checkedChanged.connect(self.close_auto_CMD_passive_shutdown_notification)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 提示标题
        self.setting_view_layout.addWidget(BodyLabel("提示"))
        # 关闭虚拟环境开机提示
        card = LayoutSwitchButtonSettingCard(MetaverseFluentIcon.Tip, "关闭虚拟环境开机提示", "关闭虚拟环境开机时的提示")
        card.setChecked(self.close_venv_power_on_tip_switch)
        card.checkedChanged.connect(self.close_venv_power_on_tip)
        self.setting_view_layout.addWidget(card)
        # 关闭虚拟环境关机提示
        card = LayoutSwitchButtonSettingCard(MetaverseFluentIcon.Tip, "关闭虚拟环境关机提示", "关闭虚拟环境关机时的提示")
        card.setChecked(self.close_venv_power_out_tip_switch)
        card.checkedChanged.connect(self.close_venv_power_out_tip)
        self.setting_view_layout.addWidget(card)
        # 关闭控制台激活提示
        card = LayoutSwitchButtonSettingCard(MetaverseFluentIcon.Tip, "关闭控制台激活提示", "关闭控制台激活时的提示")
        card.setChecked(self.close_console_activation_tip_switch)
        card.checkedChanged.connect(self.close_console_activation_tip)
        self.setting_view_layout.addWidget(card)
        # 关闭控制台销毁提示
        card = LayoutSwitchButtonSettingCard(MetaverseFluentIcon.Tip, "关闭控制台销毁提示", "关闭控制台销毁时的提示")
        card.setChecked(self.close_console_destroy_tip_switch)
        card.checkedChanged.connect(self.close_console_destroy_tip)
        self.setting_view_layout.addWidget(card)
        # 关闭控制台切换提示
        card = LayoutSwitchButtonSettingCard(MetaverseFluentIcon.Tip, "关闭控制台切换提示", "关闭控制台切换时的提示")
        card.setChecked(self.close_console_switch_tip_switch)
        card.checkedChanged.connect(self.close_console_switch_tip)
        self.setting_view_layout.addWidget(card)

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 音效标题
        self.setting_view_layout.addWidget(BodyLabel("音效"))
        # 开启音效卡片
        card = LayoutSwitchButtonSettingCard(FluentIcon.VOLUME, "开启音效", "特定操作下触发提示音")
        card.setChecked(self.play_sound)
        card.checkedChanged.connect(self.update_play_sound)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 禁用警告音效卡片
        card = LayoutSwitchButtonSettingCard(FluentIcon.VOLUME, "禁用警告音效", "禁止触发警告音效")
        card.setChecked(self.play_sound_warning)
        card.checkedChanged.connect(self.update_play_sound_warning)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 禁用操作完成音效卡片
        card = LayoutSwitchButtonSettingCard(FluentIcon.VOLUME, "禁用操作完成音效", "禁止触发操作完成音效")
        card.setChecked(self.play_sound_operation_completed)
        card.checkedChanged.connect(self.update_play_sound_operation_completed)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 禁用下载完成音效卡片
        card = LayoutSwitchButtonSettingCard(FluentIcon.VOLUME, "禁用下载完成音效", "禁止触发下载完成音效")
        card.setChecked(self.play_sound_download_complete)
        card.checkedChanged.connect(self.update_play_sound_download_complete)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 禁用提示音效卡片
        card = LayoutSwitchButtonSettingCard(FluentIcon.VOLUME, "禁用重要提示音效","禁止触发重要提示音效")
        card.setChecked(self.play_sound_important_tip)
        card.checkedChanged.connect(self.update_play_sound_important_tip)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 控件标题
        self.setting_view_layout.addWidget(BodyLabel("控件"))
        # 平滑滚动区域卡片
        card = LayoutSwitchButtonSettingCard(FluentIcon.TILES, "平滑滚动区域","由平滑滚动区域代替设置界面的滚动区域")
        card.setChecked(self.smooth_scrolling_area)
        card.checkedChanged.connect(self.update_smooth_scrolling_area)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 上下翻页堆叠部件卡片
        card = LayoutSwitchButtonSettingCard(FluentIcon.TILES, "上下翻页堆叠部件", "由上下翻页堆叠部件代替控制台界面的堆叠部件")
        card.setChecked(self.page_up_down_stacked_widget)
        card.checkedChanged.connect(self.update_page_up_down_stacked_widget)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 修复标题
        self.setting_view_layout.addWidget(BodyLabel("修复"))
        # 窗口过渡时长卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.DEVELOPER_TOOLS)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("窗口过渡时长"))  # 文字标签
        contentLabel = CaptionLabel("修复Win7窗口过渡与任务栏图标异常")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.transition_duration_combox = ComboBox()  # 下拉框
        self.transition_duration_combox.setFixedWidth(150)
        self.transition_duration_combox.addItems(["0ms","10ms","20ms","30ms"])
        self.transition_duration_combox.setCurrentText(self.transition_duration)
        self.transition_duration_combox.activated.connect(self.update_transition_duration)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.transition_duration_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 启动页面过渡时长卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.DEVELOPER_TOOLS)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("启动页面过渡时长"))  # 文字标签
        contentLabel = CaptionLabel("修复Win7启动页面窗口过渡")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.startup_animation_transition_duration_combox = ComboBox()  # 下拉框
        self.startup_animation_transition_duration_combox.setFixedWidth(150)
        self.startup_animation_transition_duration_combox.addItems(["0ms","10ms","20ms","30ms"])
        self.startup_animation_transition_duration_combox.setCurrentText(self.startup_animation_transition_duration)
        self.startup_animation_transition_duration_combox.activated.connect(self.update_startup_animation_transition_duration)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.startup_animation_transition_duration_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # CMD坐标空间模式卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.DEVELOPER_TOOLS)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("CMD坐标空间模式"))  # 文字标签
        contentLabel = CaptionLabel("修复CMD大小支持DPI")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.CMD_coordinate_space_mode_combox = ComboBox()  # 下拉框
        self.CMD_coordinate_space_mode_combox.setFixedWidth(150)
        self.CMD_coordinate_space_mode_combox.addItems(["逻辑像素模式","物理像素模式"])
        self.CMD_coordinate_space_mode_combox.setCurrentText(self.CMD_coordinate_space_mode)
        self.CMD_coordinate_space_mode_combox.activated.connect(self.update_CMD_coordinate_space_mode)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.CMD_coordinate_space_mode_combox)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 修复标题
        self.setting_view_layout.addWidget(BodyLabel("紧急修复"))
        # CMD坐标空间模式卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.VPN)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("禁止创建原生控件同级窗口"))  # 文字标签
        contentLabel = CaptionLabel("紧急修复FluentWindow窗口拉伸与Dialog和MessageBox焦点统一")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        self.prohibit_creating_native_control_windows_same_level_switch = SwitchButton()  # 开关按钮
        self.prohibit_creating_native_control_windows_same_level_switch.setChecked(self.prohibit_creating_native_control_windows_same_level)
        self.prohibit_creating_native_control_windows_same_level_switch.setFixedWidth(80)
        self.prohibit_creating_native_control_windows_same_level_switch.checkedChanged.connect(lambda key: self.update_prohibit_creating_native_control_windows_same_level(key))
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        hBoxLayout.addWidget(self.prohibit_creating_native_control_windows_same_level_switch)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 关于标题
        self.setting_view_layout.addWidget(BodyLabel("关于"))
        # CMD卡片
        card = LayoutSettingCard(FluentIcon.COMMAND_PROMPT, "CMD", f"实验性嵌入式CMD {self.CMD_Version}")
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # QFluentWidgets卡片
        card = LayoutSettingCard(QIcon(":/qfluentwidgets/images/logo.png"), "QFluentWidgets", f"版本 v{QFW__version__}")
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # PyQt5卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(MetaverseFluentIcon.Qt)  # 图标界面
        iconWidget.setFixedSize(24, 18)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("PyQt5"))  # 文字标签
        contentLabel = CaptionLabel(f"版本 v{QT__version__}")  # 字幕标签
        contentLabel.setTextColor("#606060", "#d2d2d2")
        vBoxLayout.addWidget(contentLabel)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # Python卡片
        card = LayoutSettingCard(SIP.get("Python"), "Python", f"版本 v{self.Python__version__}")
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 工具包卡片
        card = LayoutSettingCard(FluentIcon.INFO, "MetaverseSDK", f"版本 v{SDK__version__}")
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 关于卡片
        card = LayoutSettingCard(FluentIcon.INFO,"版本",f"VEM 虚拟环境管理器 {self.VEM_Version}")
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # 归属于卡片
        card = LayoutSettingCard(FluentIcon.INFO,"归属于","STD Studio Metaverse 4")
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口
        # Github卡片
        card = LayoutHyperlinkSettingCard(FluentIcon.GITHUB,"GitHub","前往VEM仓库","前往","https://github.com/H-009/Virtual-Environment-Manager")
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 间隔弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Fixed))

        # 配置标题
        self.setting_view_layout.addWidget(BodyLabel("配置"))
        # 配置文件卡片
        card = SimpleCardWidget()
        hBoxLayout = QHBoxLayout()  # 水平布局
        hBoxLayout.setContentsMargins(20, 10, 10, 10)
        hBoxLayout.setSpacing(15)
        iconWidget = IconWidget(FluentIcon.SETTING)  # 图标界面
        iconWidget.setFixedSize(24, 24)
        vBoxLayout = QVBoxLayout()  # 垂直布局
        vBoxLayout.setSpacing(0)
        vBoxLayout.addWidget(BodyLabel("配置文件"))  # 文字标签
        self.hyperlink_file_label = HyperlinkFileLabel('编辑 config.json') #文件超链接标签按钮
        self.hyperlink_file_label.set_file_path("config.json")
        self.hyperlink_file_label.set_text_color(self.theme_color)
        self.hyperlink_file_label.setFont(getFont(14, weight=QFont.Normal)) # 加入字体管理系统
        vBoxLayout.addWidget(self.hyperlink_file_label)
        hBoxLayout.addWidget(iconWidget)  # 添加到布局
        hBoxLayout.addLayout(vBoxLayout)
        card.setLayout(hBoxLayout)  # 设置卡片布局
        card.setFixedHeight(70)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 强制退出卡片
        card = LayoutDangerButtonSettingCard(FluentIcon.SETTING,"强制退出","放弃本次保存强制退出程序","强制退出")
        card.clickedChanged.connect(self.force_quit)
        self.setting_view_layout.addWidget(card)  # 添加卡片到滚动窗口

        # 底部弹簧
        self.setting_view_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        # 滚动画布嵌入视图
        self.setting_scrollArea.setWidget(self.setting_view)
        # 嵌入滚动画布
        self.setting_vlayout.addWidget(self.setting_scrollArea)