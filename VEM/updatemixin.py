from __future__ import annotations

import os
import re
import sys

import psutil
from MetaverseSDK.MetaverseAPI.Url import UrlBuilder
from MetaverseSDK.MetaverseAPI.UrlKey import ContributorKey, RepoKey
from MetaverseSDK.MetaverseTool.Config.JsonConfigPool import JCP
from MetaverseSDK.MetaverseUI.MCore.MAnimation.MWidgetAnimation import MissionBallAnimation
from MetaverseSDK.MetaverseUI.MCore.MPool.MBaseSoundPool import BSP
from MetaverseSDK.MetaverseUI.MCore.MPool.MSvgIconPool import SIP
from MetaverseSDK.MetaverseUI.MCore.MThread.MNetWorker import GetPythonVersions, GetPythonFile, GetGitHubReleaseThread
from MetaverseSDK.MetaverseUI.MFluentWidgets.MIndeterminateProgressBarDialog import IndeterminateProgressBarDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QHBoxLayout, QTreeWidgetItem, QListWidgetItem, QFileDialog
from packaging.version import Version
from qfluentwidgets import InfoBarPosition, InfoBar, FluentIcon, Dialog, BodyLabel, SimpleCardWidget, EditableComboBox, \
    StateToolTip

from typing import TYPE_CHECKING

import tool
from Dialog import DetailsConfigDialog, DetailsPresetScriptsDialog, DetailsPinDialog, DetailsPythonDialog, \
    DetailsEmbDialog, DetailsVenvDialog

from MetaverseSDK.MetaverseUI.MFluentWidgets.MDialog import DangerCountdownDialog, TextEditDialog, ReleaseDialog

if TYPE_CHECKING:
    from VEM import MainUI
    _MixinBase = MainUI   # 类型检查时 MainUI
else:
    _MixinBase = object   # 运行时 object

class UpdateMixin(_MixinBase):
    # 更新设置启动动画时长
    def update_set_startup_animation_duration_ico(self):
        # 慢
        if self.startup_animation_duration in self.startup_animation_off:
            self.startup_animation_iconWidget.setIcon(FluentIcon.SPEED_OFF)
        # 中
        elif self.startup_animation_duration in self.startup_animation_medium:
            self.startup_animation_iconWidget.setIcon(FluentIcon.SPEED_MEDIUM)
        # 快
        elif self.startup_animation_duration in self.startup_animation_high:
            self.startup_animation_iconWidget.setIcon(FluentIcon.SPEED_HIGH)

    # 更新设置启动图标大小
    def update_set_startup_ico_size_ico(self):
        # 小
        if self.startup_ico_size == "小-80px":
            self.startup_animation_iconWidget.setIcon(FluentIcon.SPEED_OFF)
        # 中
        elif self.startup_ico_size == "中-120px":
            self.startup_animation_iconWidget.setIcon(FluentIcon.SPEED_MEDIUM)
        # 快
        elif self.startup_ico_size == "大-240px":
            self.startup_animation_iconWidget.setIcon(FluentIcon.SPEED_HIGH)

    # 更新启动动画时长
    def update_startup_animation_duration(self, index):
        duration = self.startup_animation_off[0]  # 默认
        # 快
        if index == 0:
            duration = self.startup_animation_high[0]
        elif index == 1:
            duration = self.startup_animation_high[1]
        elif index == 2:
            duration = self.startup_animation_high[2]
        elif index == 3:
            duration = self.startup_animation_high[3]
        # 中
        elif index == 4:
            duration = self.startup_animation_medium[0]
        elif index == 5:
            duration = self.startup_animation_medium[1]
        elif index == 6:
            duration = self.startup_animation_medium[2]
        # 慢
        elif index == 7:
            duration = self.startup_animation_off[0]
        elif index == 8:
            duration = self.startup_animation_off[1]
        elif index == 9:
            duration = self.startup_animation_off[2]
        elif index == 10:
            duration = self.startup_animation_off[3]

        self.startup_animation_duration = duration
        JCP.update("config.json",["setting","startup_animation_duration"], duration)
        InfoBar.info(
            title="通知",
            content=f"启动页面动画时长切为 {duration}",
            parent=self,
            position=InfoBarPosition.TOP
        )

        # 更新图标
        self.update_set_startup_animation_duration_ico()

    # 更新启动图标大小
    def update_startup_ico_size(self, index):
        duration = self.startup_ico_list[0]  # 默认
        # 快
        if index == 0:
            duration = self.startup_ico_list[0]
        elif index == 1:
            duration = self.startup_ico_list[1]
        elif index == 2:
            duration = self.startup_ico_list[2]

        self.startup_ico_size = duration
        JCP.update("config.json", ["setting","startup_ico_size"], duration)
        InfoBar.info(
            title="通知",
            content=f"启动页面图标大小切为 {duration}",
            parent=self,
            position=InfoBarPosition.TOP
        )

        # 更新图标
        self.update_set_startup_ico_size_ico()

    # 启用DPI缩放
    def update_dpi_zoom(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="DPI感知已开启 重启应用生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","DPI_zoom"], True)
        else:
            InfoBar.info(
                title="已关闭",
                content="DPI感知已关闭 重启应用生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","DPI_zoom"], False)

    # 启用非整数缩放
    def update_dpi_non_int_zoom(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="非整数缩放已开启 重启应用生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","DPI_non_int_zoom"], True)
        else:
            InfoBar.info(
                title="已关闭",
                content="非整数缩放已关闭 重启应用生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","DPI_non_int_zoom"], False)

    # 启用高DPI像素映射
    def update_high_DPI_pixel_mapping(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="高DPI像素映射已开启 重启应用生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","high_DPI_pixel_mapping"], True)
        else:
            InfoBar.info(
                title="已关闭",
                content="高DPI像素映射已关闭 重启应用生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","high_DPI_pixel_mapping"], False)

    # 启动时全屏
    def full_screen_startup(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="启动时全屏已开启 下次启动时生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","full_screen_startup"], True)

            # 临时阻塞信号
            self.full_screen_after_startup_switch.blockSignals(True)
            self.maximize_after_startup_switch.blockSignals(True)
            # 互斥
            self.full_screen_after_startup_switch.setChecked(False)
            JCP.update("config.json", ["setting","full_screen_after_startup"], False)
            self.maximize_after_startup_switch.setChecked(False)
            JCP.update("config.json", ["setting","maximize_after_startup"], False)
            # 释放阻塞
            self.full_screen_after_startup_switch.blockSignals(False)
            self.maximize_after_startup_switch.blockSignals(False)
        else:
            InfoBar.info(
                title="已关闭",
                content="启动时全屏已关闭 下次启动时生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","full_screen_startup"], False)

    # 启动后全屏
    def full_screen_after_startup(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="启动后全屏已开启 下次启动时生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","full_screen_after_startup"], True)

            # 临时阻塞信号
            self.full_screen_startup_switch.blockSignals(True)
            self.maximize_after_startup_switch.blockSignals(True)
            # 互斥
            self.full_screen_startup_switch.setChecked(False)
            JCP.update("config.json", ["setting","full_screen_startup"], False)
            self.maximize_after_startup_switch.setChecked(False)
            JCP.update("config.json", ["setting","maximize_after_startup"], False)
            # 释放阻塞
            self.full_screen_startup_switch.blockSignals(False)
            self.maximize_after_startup_switch.blockSignals(False)
        else:
            InfoBar.info(
                title="已关闭",
                content="启动后全屏已关闭 下次启动时生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","full_screen_after_startup"], False)

    # 启动后最大化
    def maximize_after_startup(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="启动后最大化已开启 下次启动时生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","maximize_after_startup"], True)

            # 临时阻塞信号
            self.full_screen_after_startup_switch.blockSignals(True)
            self.full_screen_startup_switch.blockSignals(True)
            # 互斥
            self.full_screen_after_startup_switch.setChecked(False)
            JCP.update("config.json", ["setting","full_screen_after_startup"], False)
            self.full_screen_startup_switch.setChecked(False)
            JCP.update("config.json", ["setting","full_screen_startup"], False)
            # 释放阻塞
            self.full_screen_after_startup_switch.blockSignals(False)
            self.full_screen_startup_switch.blockSignals(False)
        else:
            InfoBar.info(
                title="已关闭",
                content="启动后最大化已关闭 下次启动时生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","maximize_after_startup"], False)

    # 更新环境树状表
    def update_venv_tree(self,auto=False):
        try:
            # 手动模式
            if not auto:
                # cmd存活
                if self.cmd_obj_dict != {}:
                    # 被动关机决定
                    if not self.CMD_passive_shutdown:
                        # 播放音效 重要提示音效未禁用
                        if self.play_sound and not self.play_sound_important_tip:
                            self.sound_important_tip.play()
                        dialog = Dialog("当前操作完成 但仍有CMD正在工作","环境列表不会刷新 是否关闭全部CMD刷新？"
                                        "\n强制关闭会丢失当前全部的工作进度 并且不会保留任何工作数据", self)
                        # 强制关闭
                        if dialog.exec():
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

                            # 回到选择页
                            item = self.venv_tree.currentItem()
                            self.cmd_stackedwidget.setCurrentIndex(0)
                            self.power_label_text.setText("没有选中的虚拟环境")
                            self.switch_power_bool = True
                            # 移出键
                            del self.cmd_obj_dict[item.text(0)]
                            # 更新图标
                            self.cmd_power_button.setIcon(self.PLAY_SOLID_icon)
                            item.setIcon(0, self.POWER_BUTTON_icon)

                            InfoBar.success(
                                "完成",
                                "所有CMD已被强制关机 列表更新成功",
                                parent=self,
                                position=InfoBarPosition.TOP,
                                duration=1500
                            )
                        else:
                            InfoBar.warning(
                                "警告",
                                "环境列表未能完成更新",
                                parent = self,
                                position = InfoBarPosition.TOP
                            )
                            return
                    # 静默决定
                    else:
                        # 自动决定下的CMD被动关机通知
                        if not self.disable_auto_CMD_passive_shutdown_notification:
                            # 提前显示 防止同一时间冲突
                            InfoBar.info(
                                "提示",
                                "所有CMD已被强制关机",
                                parent=self,
                                position=InfoBarPosition.TOP,
                                duration=1500
                            )

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

                        # 回到选择页
                        item = self.venv_tree.currentItem()
                        self.cmd_stackedwidget.setCurrentIndex(0)
                        self.power_label_text.setText("没有选中的虚拟环境")
                        self.switch_power_bool = True
                        # 移出键
                        del self.cmd_obj_dict[item.text(0)]
                        # 更新图标
                        self.cmd_power_button.setIcon(self.PLAY_SOLID_icon)
                        item.setIcon(0, self.POWER_BUTTON_icon)
                # 常规
                else:
                    # 重置
                    self.cmd_stackedwidget.setCurrentIndex(0)
                    self.power_label_text.setText("没有选中的虚拟环境")

            self.venv_tree.clear() # 清空

            # 读取虚拟环境配置
            venv_envs = JCP.get("config.json",["venv"])
            venv_item = [] # 基础环境列表
            # 如果不为空或没有项目
            if venv_envs:
                self.venv_tree_item = QTreeWidgetItem(['venv']) # 创建树枝
                for version, info in venv_envs.items():
                    # 设置数据
                    item = QTreeWidgetItem([info["name"]])
                    item.setIcon(0, self.POWER_BUTTON_icon)
                    item.setData(0, Qt.UserRole, {
                        "type": "venv",
                        "name": info["name"],
                        "python": info["python"],
                        "cfg_file": info["cfg_file"],
                        "dir": info["dir"],
                        "start_parameter": info["start_parameter"],
                        "include-system-site-packages": info["include-system-site-packages"],
                        "version": info["version"],
                    })
                    venv_item.append(item)
                self.venv_tree_item.addChildren(venv_item)
                self.venv_tree.addTopLevelItem(self.venv_tree_item)

            # 读取便携式环境配置
            emb_envs = JCP.get("config.json",["emb"])
            emb_item = [] # 基础环境列表
            # 如果不为空或没有项目
            if emb_envs:
                self.emb_tree_item = QTreeWidgetItem(['emb']) # 创建树枝
                for version, info in emb_envs.items():
                    # 设置数据
                    item = QTreeWidgetItem([info["name"]])
                    item.setIcon(0, self.ZIP_FOLDER_icon)
                    item.setData(0, Qt.UserRole, {
                        "type": "emb",
                        "name": info["name"],
                        "dir": info["dir"],
                        "pth": info["pth"],
                        "start_script": info["start_script"],
                        "version": info["version"]
                    })
                    emb_item.append(item)
                self.emb_tree_item.addChildren(emb_item)
                self.venv_tree.addTopLevelItem(self.emb_tree_item)

            # 读取基础环境配置
            python_envs = JCP.get("config.json",["python"])
            python_item = [] # 基础环境列表
            # 如果不为空或没有项目
            if python_envs:
                self.python_tree_item = QTreeWidgetItem(['python']) # 创建树枝
                for version, info in python_envs.items():
                    # 设置数据
                    item = QTreeWidgetItem([info["name"]])
                    item.setIcon(0, SIP.get("Python"))
                    item.setData(0, Qt.UserRole, {
                        "type": "python",
                        "name": info["name"],
                        "path": info["path"],
                        "dir": info["dir"],
                        "version": info["version"]
                    })
                    python_item.append(item)
                self.python_tree_item.addChildren(python_item)
                self.venv_tree.addTopLevelItem(self.python_tree_item)

            self.venv_tree.expandAll()  # 展开全部树
        except Exception as a:
            print(a)

    # 更新图钉列表
    def update_thumbtack_list(self):
        self.pin_list.clear() # 清理
        pin_list = JCP.get("config.json",["pin"],[]) # 默认空列表

        # 添加列表项
        for stand in pin_list:
            item = QListWidgetItem(stand)
            self.pin_list.addItem(item)
        self.pin_list.itemClicked.connect(self.apply_commands)

    # 关闭便携式环境的脱控通知
    def close_emb_out_control_notification(self, key):
        self.close_emb_out_control_notification_switch = key
        JCP.update("config.json", ["setting","close_emb_out_control_notification_switch"], key)

    # 关闭自动决定下的CMD被动关机通知
    def close_auto_CMD_passive_shutdown_notification(self, key):
        self.disable_auto_CMD_passive_shutdown_notification = key
        JCP.update("config.json", ["setting","disable_auto_CMD_passive_shutdown_notification"],key)

    # 关闭虚拟环境开机提示
    def close_venv_power_on_tip(self, key):
        self.close_venv_power_on_tip_switch = key
        JCP.update("config.json", ["setting","close_venv_power_on_tip_switch"], key)

    # 关闭虚拟环境关机提示
    def close_venv_power_out_tip(self, key):
        self.close_venv_power_out_tip_switch = key
        JCP.update("config.json", ["setting","close_venv_power_out_tip_switch"], key)

    # 关闭控制台激活提示
    def close_console_activation_tip(self, key):
        self.close_console_activation_tip_switch = key
        JCP.update("config.json", ["setting","close_console_activation_tip_switch"], key)

    # 关闭控制台销毁提示
    def close_console_destroy_tip(self, key):
        self.close_console_destroy_tip_switch = key
        JCP.update("config.json", ["setting","close_console_destroy_tip_switch"], key)

    # 关闭控制台切换提示
    def close_console_switch_tip(self, key):
        self.close_console_switch_tip_switch = key
        JCP.update("config.json", ["setting","close_console_switch_tip_switch"], key)

    # 更新强制刷新CMD
    def refresh_CMD_update(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="强制刷新CMD已开启 重启CMD生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            self.mandatory_update_CMD_switch = True
            JCP.update("config.json", ["setting","refresh_CMD"], True)

        else:
            InfoBar.info(
                title="已关闭",
                content="强制刷新CMD已关闭 重启CMD生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            self.mandatory_update_CMD_switch = False
            JCP.update("config.json", ["setting","refresh_CMD"], False)

    # 更新手动刷新CMD
    def update_manual_CMD(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="手动刷新CMD已开启",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.enable_manual_update_CMD_switch = True
            JCP.update("config.json", ["setting","manual_CMD"], True)
            # 如果电源按钮未禁用 则启用
            if self.cmd_power_button.isEnabled():
                self.manual_update_button.setEnabled(True)

        else:
            InfoBar.info(
                title="已关闭",
                content="手动刷新CMD已关闭",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.enable_manual_update_CMD_switch = False
            JCP.update("config.json", ["setting","manual_CMD"], False)
            # 立即禁用
            self.manual_update_button.setEnabled(False)

    # 更新CMD全屏
    def update_full_screen_CMD(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="CMD全屏已开启",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.enable_cmd_full_screen_switch = True
            JCP.update("config.json", ["setting","full_screen_CMD"], True)
            # 如果电源按钮未禁用 则启用
            if self.cmd_power_button.isEnabled():
                self.cmd_full_screen_button.setEnabled(True)

        else:
            InfoBar.info(
                title="已关闭",
                content="CMD全屏已关闭",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.enable_cmd_full_screen_switch = False
            JCP.update("config.json", ["setting","full_screen_CMD"], False)
            # 立即禁用
            self.cmd_full_screen_button.setEnabled(False)

    # 更新云母效果
    def update_mica_effect(self,key):
        self.setMicaEffectEnabled(key)
        JCP.update("config.json", ["setting","mica_effect"], key)
        self.mica_effect = key

    # 更新懒加载
    def update_lazy(self,key):
        JCP.update("config.json", ["setting","lazy"], key)
        self.lazy = key

    # 更新现有启动参数
    def update_existence_start_parameter(self,text):
        name_text = os.path.dirname(text)
        # 文件夹不为空时更新
        if name_text != "":
            if name_text.endswith("/") or name_text.endswith("\\"):  # 以/\结尾
                self.start_parameter_line.setText(name_text + "Scripts/activate")
            else:
                self.start_parameter_line.setText(name_text + "/Scripts/activate")
        # 否则重置
        else:
            self.start_parameter_line.setText("")

    # 更新新建启动参数
    def update_new_start_parameter(self,text):
        # 不为空
        if text != "":
            if text.endswith("/") or text.endswith("\\"): # 以/\结尾
                self.venv_startup_parameters_line.setText(text+"Scripts/activate")
            else:
                self.venv_startup_parameters_line.setText(text+"/Scripts/activate")

        # 否则重置
        else:
            self.venv_startup_parameters_line.setText("")

        # 最后刷新 防止停滞
        # 刷新命令
        self.update_venv_command()

    # 更新延时嵌入时长
    def update_delay(self,index):
        if index == 0:
            self.delay_cmd = "0ms"
        elif index == 1:
            self.delay_cmd = "50ms"
        elif index == 2:
            self.delay_cmd = "100ms"
        elif index == 3:
            self.delay_cmd = "250ms"
        elif index == 4:
            self.delay_cmd = "500ms"
        JCP.update("config.json", ["setting","delay"], self.delay_cmd)
        InfoBar.success(
            title="成功",
            content=f"延时时长切为 {self.delay_cmd} 重启CMD生效",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=1500
        )

    # 更新监控频率
    def update_frequency(self,index):
        if index == 0:
            self.frequency_cmd = "0.5s" # 使用监控频率自己的变量
        elif index == 1:
            self.frequency_cmd= "1.0s"
        elif index == 2:
            self.frequency_cmd = "2.0s"
        elif index == 3:
            self.frequency_cmd = "5.0s"
        JCP.update("config.json", ["setting","frequency"], self.frequency_cmd)
        InfoBar.success(
            title="成功",
            content=f"监控频率切为 {self.frequency_cmd} 重启CMD生效",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=1500
        )

    # 更新关机保护
    def shutdown_protection_update(self,key):
        self.shutdown_protection_switch = key
        JCP.update("config.json", ["setting","shutdown_protection"], key)

    # 更新全屏保护
    def full_screen_update(self,key):
        self.full_screen_switch = key
        JCP.update("config.json", ["setting","full_screen"], key)

    # 更新自动进入环境
    def update_auto_enter_venv(self,key):
        self.auto_enter_venv = key
        JCP.update("config.json", ["setting","auto_enter_venv"], key)

    # 更新自动进入环境回调时长
    def update_auto_enter_venv_pullback_duration(self,index):
        if index == 0:
            self.pullback_duration = "0ms"
        elif index == 1:
            self.pullback_duration = "10ms"
        elif index == 2:
            self.pullback_duration = "50ms"
        elif index == 3:
            self.pullback_duration = "100ms"
        elif index == 4:
            self.pullback_duration = "250ms"
        elif index == 5:
            self.pullback_duration = "500ms"
        JCP.update("config.json", ["setting","pullback_duration"], self.pullback_duration)

    # CMD被动关机决定
    def update_CMD_passive_shutdown(self,key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="被动关机将自动决定",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.CMD_passive_shutdown = True
            JCP.update("config.json", ["setting","CMD_passive_shutdown"], True)

        else:
            dialog = Dialog("是否切换手动模式?","请注意\n切换为手动模式后 决定窗口可能会频繁弹出",self)
            if dialog.exec():
                InfoBar.info(
                    title="已关闭",
                    content="被动关机将手动决定",
                    parent=self,
                    position=InfoBarPosition.TOP
                )
                self.CMD_passive_shutdown = False
                JCP.update("config.json", ["setting","CMD_passive_shutdown"], False)
            else:
                self.CMD_passive_shutdown_button.blockSignals(True)
                self.CMD_passive_shutdown_button.setChecked(True)
                self.CMD_passive_shutdown_button.blockSignals(False)

    # 更新CMD自动配置模式
    def update_auto_config_model(self,index):
        if index == 0:
            self.auto_config_model = "虚拟环境"
        elif index == 1:
            self.auto_config_model = "控制台"
        JCP.update("config.json", ["setting","auto_config_model"], self.auto_config_model)

    # 更新虚拟环境回调时长
    def update_venv_config_callback_duration(self,index):
        if index == 0:
            self.venv_config_callback_duration = "sync"
        elif index == 1:
            self.venv_config_callback_duration = "50ms"
        elif index == 2:
            self.venv_config_callback_duration = "100ms"
        elif index == 3:
            self.venv_config_callback_duration = "200ms"
        elif index == 4:
            self.venv_config_callback_duration = "500ms"
        elif index == 5:
            self.venv_config_callback_duration = "1000ms"
        JCP.update("config.json", ["setting","venv_config_callback_duration"], self.venv_config_callback_duration)

    # 更新虚拟环境回调时长
    def update_console_config_callback_duration(self,index):
        if index == 0:
            self.console_config_callback_duration = "50ms"
        elif index == 1:
            self.console_config_callback_duration = "100ms"
        elif index == 2:
            self.console_config_callback_duration = "200ms"
        elif index == 3:
            self.console_config_callback_duration = "500ms"
        elif index == 4:
            self.console_config_callback_duration = "1000ms"
        JCP.update("config.json", ["setting","console_config_callback_duration"], self.console_config_callback_duration)

    # 更新允许配置叠加回调时长
    def update_allow_overlay_callback_duration(self,key):
        if key:
            InfoBar.info(
                title="已开启",
                content="允许配置叠加回调时长",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.allow_overlay_callback_duration = True
            JCP.update("config.json", ["setting","allow_overlay_callback_duration"], True)
        else:
            InfoBar.info(
                title="已关闭",
                content="禁止叠加回调时长",
                parent=self,
                position=InfoBarPosition.TOP
            )
            self.allow_overlay_callback_duration = False
            JCP.update("config.json", ["setting","allow_overlay_callback_duration"], False)

    # 更新最大上限
    def update_maximum_limit(self,text):
        if len(text) < 4000:
            self.add_config_older_button.setEnabled(True)
            self.one_older_max_label.setTextColor(QColor(255,255,255),QColor(255,255,255))
        if len(text) >= 4000:
            self.add_config_older_button.setEnabled(False)
            self.one_older_max_label.setTextColor(QColor(255,0,0),QColor(255,0,0))
        self.one_older_max_label.setText(str(len(text))+"/4000")

    # 更新占位符列表
    def update_placeholder_list(self,text):
        # 更新最大上限-预设脚本
        if len(text) < 2000:
            self.switch_preset_scripts_max_bool = True
            self.preset_scripts_one_older_max_label.setTextColor(QColor(255,255,255),QColor(255,255,255))
        if len(text) >= 2000:
            self.switch_preset_scripts_max_bool = False
            self.preset_scripts_one_older_max_label.setTextColor(QColor(255,0,0),QColor(255,0,0))
        self.preset_scripts_one_older_max_label.setText(str(len(text))+"/2000")

        # 清空
        while self.preset_scripts_layout.count():
            item = self.preset_scripts_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.preset_scripts_dict = {} # 清空字典

        seen = set() # 排除集
        self.num_label = BodyLabel(f"所需{0}个参数")
        self.preset_scripts_layout.addWidget(self.num_label)

        # 获取所有占位符
        matches = re.findall(r'%([A-Za-z0-9_]+)', text)
        for comm in matches:
            if comm not in seen:
                seen.add(comm) # 添加排除
                self.num_label.setText(f"所需{len(seen)}个参数")
                key = "%"+comm
                widget = SimpleCardWidget()
                widget.setFixedHeight(50)
                layout = QHBoxLayout()
                widget.setLayout(layout)
                label = BodyLabel(key)
                label.setMaximumWidth(1500) # 最大长度1500
                layout.addWidget(label)
                type_label = BodyLabel("内部类型:")
                type_label.setFixedWidth(60)
                layout.addWidget(type_label)
                combox = EditableComboBox()
                combox.setMaximumWidth(150)
                combox.addItems(["str","int","bool","date","path","enum"])
                self.preset_scripts_dict[key] = 'str' # 设置默认类型
                combox.currentTextChanged.connect(lambda v,k=key:self.update_placeholder_dict(k,v)) # 使用参数冻结连接
                layout.addWidget(combox)
                type2_label = BodyLabel("→str")
                type2_label.setFixedWidth(30)
                layout.addWidget(type2_label)
                self.preset_scripts_layout.addWidget(widget)

    # 更新占位符字典
    def update_placeholder_dict(self,key,value):
        self.preset_scripts_dict[key] = value # 更新字典

    # 更新最大上限-图钉
    def update_maximum_limit_pin(self,text):
        if len(text) < 1000:
            self.switch_pin_comm_max_bool = True
            self.pin_comm_one_older_max_label.setTextColor(QColor(255,255,255),QColor(255,255,255))
        if len(text) >= 1000:
            self.switch_pin_comm_max_bool = False
            self.pin_comm_one_older_max_label.setTextColor(QColor(255,0,0),QColor(255,0,0))
        self.pin_comm_one_older_max_label.setText(str(len(text))+"/1000")

    # 更新音效
    def update_play_sound(self, key):
        self.play_sound = key
        JCP.update("config.json", ["setting","play_sound"], key)

    # 更新警告音效
    def update_play_sound_warning(self, key):
        self.play_sound_warning = key
        JCP.update("config.json", ["setting","play_sound_warning"], key)

    # 更新操作完成音效
    def update_play_sound_operation_completed(self, key):
        self.play_sound_operation_completed = key
        JCP.update("config.json", ["setting","play_sound_operation_completed"], key)

    # 更新下载完成音效
    def update_play_sound_download_complete(self, key):
        self.play_sound_download_complete = key
        JCP.update("config.json", ["setting","play_sound_download_complete"], key)

    # 更新提示音效
    def update_play_sound_important_tip(self, key):
        self.play_sound_important_tip = key
        JCP.update("config.json", ["setting","play_sound_important_tip"], key)

    # 更新动画实现的平滑滚动区域
    def update_smooth_scrolling_area(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="将由平滑滚动区域代替滚动区域 重启生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","smooth_scrolling_area"], True)

        else:
            InfoBar.info(
                title="已关闭",
                content="将由滚动区域代替平滑滚动区域 重启生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            JCP.update("config.json", ["setting","smooth_scrolling_area"], False)

    # 更新上下翻页堆叠部件
    def update_page_up_down_stacked_widget(self, key):
        # 开启
        if key:
            InfoBar.info(
                title="已开启",
                content="将由上下翻页堆叠部件代替上下弹出堆叠部件 重启生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )

        else:
            InfoBar.info(
                title="已关闭",
                content="将由上下弹出堆叠部件代替上下翻页堆叠部件 重启生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
        JCP.update("config.json", ["setting","page_up_down_stacked_widget"], key)

    # 更新基础环境
    def update_python(self):
        self.python_table.setRowCount(0)

        # 更新表格
        python_json = JCP.get("config.json",["python"])
        for value,key in python_json.items():
            tool.table_add_row_4(self.python_table, key["name"], key["version"], key["dir"], key["path"],value)

        # 更新环境树
        self.update_venv_tree()

    # 更新便携式环境
    def update_emb(self):
        self.emb_table.setRowCount(0)

        # 更新表格
        emb_json = JCP.get("config.json",["emb"])
        for value,key in emb_json.items():
            tool.table_add_row_5(self.emb_table, key["name"], key["version"],key["dir"],key["start_script"],str(key["pth"]),value)

        # 更新环境树
        self.update_venv_tree()

    # 更新虚拟环境
    def update_venv(self):
        self.venv_table.setRowCount(0)

        # 更新表格
        venv_json = JCP.get("config.json",["venv"])
        for value,key in venv_json.items():
            tool.table_add_row_7(self.venv_table, key["name"], key["version"],key["dir"],key["cfg_file"],
                                 key['start_parameter'],key['python'],str(key["include-system-site-packages"]),value)

        # 更新环境树
        self.update_venv_tree()

    # 更新图钉
    def update_pin(self):
        self.pin_table.setRowCount(0)

        # 更新表格
        pin_json = JCP.get("config.json",["pin"],[]) # 默认列表
        for key in pin_json:
            tool.table_add_row_1(self.pin_table, key)

        self.update_thumbtack_list() #更新图钉列表

    # 更新预设脚本
    def update_preset_scripts(self):
        self.preset_scripts_table.setRowCount(0)

        preset_scripts_json = JCP.get("config.json",["preset_scripts"],{}) # 默认空集合
        for value,key in preset_scripts_json.items():
            tool.table_add_row_4(self.preset_scripts_table, key["name"], key["description"],key["older"],str(key["parameters_dict"]),value)

    # 更新配置文件
    def update_config(self):
        self.config_table.setRowCount(0)

        config_json = JCP.get("config.json",["config"],{}) # 默认空集合
        for value,key in config_json.items():
            tool.table_add_row_2(self.config_table, key["name"], str(key["older_list"]),value)

    # 更新配置基础环境下拉列表
    def update_config_python_combox(self,box):
        box.clear()

        for row in range(self.python_table.rowCount()):
            item_col0 = self.python_table.item(row, 0)  # 第1列
            item_col3 = self.python_table.item(row, 3)  # 第4列

            if item_col3 is not None and item_col0 is not None:
                box.addItem(f"{item_col0.text()}    {item_col3.text()}", SIP.get("Python"),userData=item_col3.text())

        box.setCurrentIndex(-1) # 取消选中

        # 更新命令
        self.update_config_venv_command()

    # 更新配置文件下拉列表
    def update_config_combox(self,box):
        box.clear()

        for row in range(self.config_table.rowCount()):
            item_col0 = self.config_table.item(row, 0)  # 第1列

            if item_col0 is not None:
                # 存储的父级
                box.addItem(item_col0.text(), FluentIcon.DOCUMENT,userData=item_col0.data(Qt.UserRole))

        box.setCurrentIndex(-1) # 取消选中

    # 更新配置启动参数
    def update_config_start_parameter(self, text):
        # 不为空
        if text != "":
            if text.endswith("/") or text.endswith("\\"):  # 以/\结尾
                self.config_startup_parameters_line.setText(text + "Scripts/activate")
            else:
                self.config_startup_parameters_line.setText(text + "/Scripts/activate")

        # 否则重置
        else:
            self.config_startup_parameters_line.setText("")

        # 最后刷新 防止停滞
        # 刷新命令
        self.update_config_venv_command()

    # 刷新配置虚拟环境命令
    def update_config_venv_command(self):
        # 选中基础解释器
        if self.config_base_python_box.text() != "":
            # 基础命令
            if not self.config_custom_prompts_prefix_box.isChecked():
                base = f'"{self.config_base_python_box.text()}" -m venv "{self.config_venv_Loca_line.text()}"'
            else:
                base = f'"{self.config_base_python_box.text()}" -m venv "{self.config_venv_Loca_line.text()}" --prompt "{self.config_prompts_prefix_line.text()}"' # 提示符命令
            # 将列表元素用空格连接
            params_str = ' '.join(self.config_python_batch_list)
            full_cmd = f"{base} {params_str}" if params_str else base

            self.config_created_parameter_line.setText(full_cmd)
        # 否则清空
        else:
            self.config_created_parameter_line.setText("")

    # 基础环境详情
    def details_python(self):
        # 获取当前所在行第0列item
        item = self.python_table.item(self.python_table.currentRow(), 0)
        # 获取json
        json_data = JCP.get("config.json",["python",item.data(Qt.UserRole)])

        dialog = DetailsPythonDialog("详情",SIP.get("Python"),
                                     "Python 基础环境",
                                     f"环境名称 {json_data['name']}",
                                     f"解释器版本 {json_data['version']}",
                                     f"环境路径 {json_data['dir']}",
                                     f"解释器路径 {json_data['path']}",self)
        if dialog.exec():
            # 销毁
            dialog.accept()
            dialog.deleteLater()

    # 便携式环境详情
    def details_emb(self):
        # 获取当前所在行第0列item
        item = self.emb_table.item(self.emb_table.currentRow(), 0)
        # 获取json
        json_data = JCP.get("config.json",["emb",item.data(Qt.UserRole)])

        dialog = DetailsEmbDialog("详情",self.ZIP_FOLDER_icon,
                                                           "Python Emb便携式环境",
                                                           f"环境名称 {json_data['name']}",
                                                           f"解释器版本 {json_data['version']}",
                                                           f"环境路径 {json_data['dir']}",
                                                           f"启动脚本路径 {json_data['start_script']}",
                                                           f"第三方库解锁 {json_data['pth']}",self)
        if dialog.exec():
            # 销毁
            dialog.accept()
            dialog.deleteLater()

    # 虚拟环境详情
    def details_venv(self):
        # 获取当前所在行第0列item
        item = self.venv_table.item(self.venv_table.currentRow(), 0)
        # 获取json
        json_data = JCP.get("config.json",["venv",item.data(Qt.UserRole)])

        dialog = DetailsVenvDialog("详情",self.IOT_icon,
                                                         "Python Venv虚拟环境",
                                                         f"环境名称 {json_data['name']}",
                                                         f"解释器版本 {json_data['version']}",
                                                         f"环境路径 {json_data['dir']}",
                                                         f"配置路径 {json_data['cfg_file']}",
                                                         f"启动参数 {json_data['start_parameter']}",
                                                         f"基础环境路径 {json_data['python']}",
                                                         f"继承全局包 {json_data['include-system-site-packages']}",self)
        if dialog.exec():
            # 销毁
            dialog.accept()
            dialog.deleteLater()

    # 图钉详情
    def details_pin(self):
        # 获取json
        json_data = JCP.get("config.json",["pin"])[self.pin_table.currentRow()]

        dialog = DetailsPinDialog("详情",FluentIcon.PIN,
                                 "VEM 图钉",
                                 f"图钉命令 {json_data}",self)
        if dialog.exec():
            # 销毁
            dialog.accept()
            dialog.deleteLater()

    # 预设脚本详情
    def details_preset_scripts(self):
        # 获取当前所在行第0列item
        item = self.preset_scripts_table.item(self.preset_scripts_table.currentRow(), 0)
        # 获取json
        json_data = JCP.get("config.json",["preset_scripts",item.data(Qt.UserRole)])

        dialog = DetailsPresetScriptsDialog("详情",FluentIcon.QUICK_NOTE,
                                                         "VEM 预设脚本",
                                                         f"预设名称 {json_data['name']}",
                                                         f"预设描述 {json_data['description']}",
                                                         f"原始命令 {json_data['older']}","参数字典",self)
        for t in json_data['parameters_dict']:
            dialog.textedit.append(f"{t} : {json_data['parameters_dict'][t]}")
        # 移动光标到文档最开头
        cursor = dialog.textedit.textCursor()
        cursor.setPosition(0)
        dialog.textedit.setTextCursor(cursor)
        if dialog.exec():
            # 销毁
            dialog.accept()
            dialog.deleteLater()

    # 配置文件详情
    def details_config(self):
        # 获取当前所在行第0列item
        item = self.config_table.item(self.config_table.currentRow(), 0)
        # 获取json
        json_data = JCP.get("config.json",["config",item.data(Qt.UserRole)])

        dialog = DetailsConfigDialog("详情",FluentIcon.DOCUMENT,
                                                         "VEM 配置文件",
                                                         f"配置名称 {json_data['name']}",
                                                         f"命令列表",self)
        for t in json_data['older_list']:
            dialog.textedit.append(t)
        # 移动光标到文档最开头
        cursor = dialog.textedit.textCursor()
        cursor.setPosition(0)
        dialog.textedit.setTextCursor(cursor)
        if dialog.exec():
            # 销毁
            dialog.accept()
            dialog.deleteLater()

    # 更新基础环境下拉列表
    def update_python_combox(self,box):
        box.clear()

        for row in range(self.python_table.rowCount()):
            item_col0 = self.python_table.item(row, 0)  # 第1列
            item_col3 = self.python_table.item(row, 3)  # 第4列

            if item_col3 is not None and item_col0 is not None:
                box.addItem(f"{item_col0.text()}    {item_col3.text()}", SIP.get("Python"),userData=item_col3.text())

        box.setCurrentIndex(-1) # 取消选中

        # 更新命令
        self.update_venv_command()

    # 更新CMD坐标空间模式
    def update_CMD_coordinate_space_mode(self,index):
        if index == 0:
            self.CMD_coordinate_space_mode = "逻辑像素模式"
        elif index == 1:
            self.CMD_coordinate_space_mode = "物理像素模式"
        JCP.update("config.json", ["setting","CMD_coordinate_space_mode"],self.CMD_coordinate_space_mode)
        InfoBar.info(
            title="通知",
            content=f"模式已切换为 {self.CMD_coordinate_space_mode} 重启CMD生效",
            parent=self,
            position=InfoBarPosition.TOP,
            duration=1500
        )

    # 更新窗口过渡时长
    def update_transition_duration(self,index):
        if index == 0:
            self.transition_duration = "0ms"
        elif index == 1:
            self.transition_duration = "10ms"
        elif index == 2:
            self.transition_duration = "20ms"
        elif index == 3:
            self.transition_duration = "30ms"
        JCP.update("config.json", ["setting","transition_duration"],self.transition_duration)
        InfoBar.info(
            title="通知",
            content=f"过渡时长换为 {self.transition_duration} 重启生效",
            parent=self,
            position=InfoBarPosition.TOP
        )

    # 更新窗口过渡时长
    def update_startup_animation_transition_duration(self,index):
        if index == 0:
            self.startup_animation_transition_duration = "0ms"
        elif index == 1:
            self.startup_animation_transition_duration = "10ms"
        elif index == 2:
            self.startup_animation_transition_duration = "20ms"
        elif index == 3:
            self.startup_animation_transition_duration = "30ms"
        JCP.update("config.json", ["setting","startup_animation_transition_duration"],self.startup_animation_transition_duration)
        InfoBar.info(
            title="通知",
            content=f"过渡时长换为 {self.startup_animation_transition_duration} 重启生效",
            parent=self,
            position=InfoBarPosition.TOP
        )

    # 更新禁止创建原生控件同级窗口
    def update_prohibit_creating_native_control_windows_same_level(self, key):
        # 关闭状态下
        if not key:
            # 危险倒计时消息框
            w = DangerCountdownDialog(
                title='您正在进行危险操作⚠️',
                content="""您当前的操作正在允许创建原生控件同级窗口!!\n允许创建原生控件后\n打开模态对话框和模态遮罩对话框会出现焦点残留
                            导致焦点丢失 并且导致窗口无法拉伸 必须关闭软件解决 并且会有数据丢失的风险
                            \n如果您是误触 请点击右下角取消按钮 继续禁用创建 \n 如果仍需继续允许 请等待左下角继续按钮倒计时结束后再点击""",
                parent=self,
                countdown_seconds=25,
                text="继续"
            )
            # 确认
            if w.exec():
                InfoBar.warning(
                    title="已关闭",
                    content="已允许创建原生控件同级窗口 重启生效",
                    parent=self,
                    position=InfoBarPosition.TOP,
                    duration=1500
                )
                # 关闭
                JCP.update("config.json", ["setting","prohibit_creating_native_control_windows_same_level"], False)
            # 取消
            else:
                # 临时阻塞信号
                self.prohibit_creating_native_control_windows_same_level_switch.blockSignals(True)  # 开始阻塞
                self.prohibit_creating_native_control_windows_same_level_switch.setChecked(True)
                self.prohibit_creating_native_control_windows_same_level_switch.blockSignals(False)  # 恢复信号

        else:
            InfoBar.info(
                title="已开启",
                content="已禁止创建原生控件同级窗口 重启生效",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=1500
            )
            # 开启
            JCP.update("config.json", ["setting","prohibit_creating_native_control_windows_same_level"], True)

    # 更新导航栏下载徽章
    def update_download_badge(self,m="+"):
        try:
            # 是否处于隐藏
            if self.downloadBadge.text() == "":
                self.downloadBadge.setText("1")
                # 取消隐藏 更新背景颜色 强制使用强调色
                self.downloadBadge.setCustomBackgroundColor(self.theme_color, self.theme_color)
            else:
                if m == "+":
                    self.downloadBadge.setText(str(int(self.downloadBadge.text())+1))
                elif m == "-":
                    self.downloadBadge.setText(str(int(self.downloadBadge.text())-1))

                # 是否同步隐藏
                if self.downloadBadge.text() == "0":
                    self.hide_download_badge()
                # 不处于隐藏时 背景更新交给更新强调色

            self.downloadBadge.adjustSize() # 强制刷新
        except Exception as a:
            print(a)

    # 更新下载队列
    def update_download_queue(self):
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
            url = self.direct_link_line.text()
            filename = self.download_file_combox.text()

            MissionBallAnimation(main_window=self,
                                 src_btn=self.add_download_list,
                                 dst_btn=self.navigationInterface_DownloadList,
                                 on_finished_callback=self.update_download_badge,
                                 color_auto=self.theme_color
                                 )
            # 添加到下载列表
            self.download_list.append(filename)
            self.download_manager_thread.add(url,filename)

            self.reset_download() # 重置

    # 更新下载路径
    def update_download_path(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "选择 下载位置",
            "C:/"
        )

        if path != '':
            InfoBar.success(title="成功",
                            content=f"下载位置已更新为 {path}",
                            parent=self,
                            position=InfoBarPosition.TOP,
                            duration=1500
                            )
            self.downloads_path = path
            self.downloads_path_contentLabel.setText(path) # 更新字幕标签
            JCP.update("config.json",["setting","downloads_path"],path)

    # 更新下载版本
    def update_download_version(self):
        dialog = IndeterminateProgressBarDialog("获取Python全部版本...", self)
        dialog.show()

        # 获取版本
        self.get_python_thread = GetPythonVersions(UrlBuilder.PythonAllVersions())
        self.get_python_thread.error.connect(lambda s: self.uninstall_venv_error(s, dialog, self.get_python_thread))
        self.get_python_thread.finished.connect(lambda v:self.update_download_version_list(dialog,self.get_python_thread,v))
        self.get_python_thread.start()

    # 更新下载版本列表
    def update_download_version_list(self,dialog,thread,v):
        dialog.accept()
        dialog.deleteLater()
        thread.deleteLater()

        self.download_version_combox.clear()
        self.download_version_combox.addItems(v)

        InfoBar.success(title="成功",
                      content="版本信息获取成功",
                      parent=self,
                      position=InfoBarPosition.TOP,
                      duration=1500
                      )


        # 播放音效 操作完成音效未禁用
        if self.play_sound and not self.play_sound_operation_completed:
            BSP.play("OperationCompleted")

    # 更新下载文件
    def update_download_file(self):
        version = self.download_version_combox.text()
        if version == "":
            InfoBar.error(title="错误",
                            content="版本为空",
                            parent=self,
                            position=InfoBarPosition.TOP,
                            duration=1500
                            )
        else:
            dialog = IndeterminateProgressBarDialog(f"获取Python {self.download_version_combox.text()} 全部文件...", self)
            dialog.show()

            # 获取版本
            self.get_python_file_thread = GetPythonFile(UrlBuilder.PythonVersionsAllFile(version))
            self.get_python_file_thread.error.connect(lambda s: self.uninstall_venv_error(s, dialog, self.get_python_file_thread))
            self.get_python_file_thread.finished.connect(lambda v:self.update_download_file_list(dialog,self.get_python_file_thread,v))
            self.get_python_file_thread.start()

    # 更新下载文件列表
    def update_download_file_list(self,dialog,thread,v):
        dialog.accept()
        dialog.deleteLater()
        thread.deleteLater()

        self.download_file_combox.clear()
        self.download_file_combox.addItems(v)

        InfoBar.success(title="成功",
                      content="文件信息获取成功",
                      parent=self,
                      position=InfoBarPosition.TOP,
                      duration=1500
                      )

        # 播放音效 操作完成音效未禁用

        try:
            if self.play_sound and not self.play_sound_operation_completed:
                BSP.play("OperationCompleted")

        except Exception as a:
            print(a)

    # 更新下载直链
    def update_download_direct_link(self):

        text = self.download_version_combox.text()
        text2 = self.download_file_combox.text()

        self.direct_link_line.setText(f"https://www.python.org/ftp/python/{text}/{text2}")

    # 强制退出
    def force_quit(self):
        w = DangerCountdownDialog(
            title='强制退出⚠️',
            content="""放弃保存本次配置并强制退出VEM""",
            parent=self,
            countdown_seconds=3,
            text="退出"
        )
        # 确认
        if w.exec():
            sys.exit()

    # 获取新版本
    def get_new_version(self):
        # 防止多次获取
        if self.github_release_thread is None:
            # 状态工具提示
            self.new_version_state_tooltip = StateToolTip("正在检查更新", "正在获取最新版本,请耐心等待...", self)
            self.new_version_state_tooltip.adjustSize()

            x = self.width() - self.new_version_state_tooltip.width() - 20

            self.new_version_state_tooltip.move(x, 55)
            self.new_version_state_tooltip.show()

            # 获取更新线程
            self.github_release_thread = GetGitHubReleaseThread(UrlBuilder.GithubRepoLatestRelease(ContributorKey.H009,RepoKey.VEM))
            self.github_release_thread.release_fetched.connect(self.get_new_version_success)
            self.github_release_thread.error_occurred.connect(self.get_new_version_error)
            self.github_release_thread.start()

    # 获取最新版本错误
    def get_new_version_error(self,error):
        try:
            InfoBar.error(title="错误",
                          content=error,
                          parent=self,
                          position=InfoBarPosition.TOP_RIGHT,
                          duration=2000
                          )
            # 销毁状态提示
            self.new_version_state_tooltip.setTitle("获取失败")
            self.new_version_state_tooltip.setContent("未找到任何版本")
            self.new_version_state_tooltip.setState(True)
            # 销毁线程
            self.github_release_thread.deleteLater()
            # 清空引用
            self.github_release_thread = None
        except Exception as a:
            print(a)

    # 获取最新版本成功
    def get_new_version_success(self,release):
        try:
            self.new_version_state_tooltip.setTitle("获取成功")
            self.new_version_state_tooltip.setState(True)

            # 播放音效 操作完成音效未禁用
            if self.play_sound and not self.play_sound_operation_completed:
                BSP.play("OperationCompleted")

            # 找到新版本
            if Version(self.VEM_Version) < Version(release["version"]):
                self.new_version_state_tooltip.setContent("找到新版本")

                dialog = ReleaseDialog(release,self)
                dialog.exec()

            # 当前为新版本
            else:
                self.new_version_state_tooltip.setContent("当前为新版本")

            # 销毁线程
            self.github_release_thread.deleteLater()
            # 清空引用
            self.github_release_thread = None
        except Exception as a:
            print(a)

    # 打开配置池
    def open_jcp_pool(self):
        w = TextEditDialog(
            title='配置池',
            content="查看在内存中的配置池",
            parent=self
        )

        w.line.setText(str(JCP.all()))
        w.line.setReadOnly(True)
        w.cancelButton.hide()
        w.line.setFixedSize(800,500)

        w.exec()

    # 打开CMD池
    def open_cmd_pool(self):
        w = TextEditDialog(
            title='CMD池',
            content="查看在内存中的CMD池",
            parent=self
        )

        w.line.setText(str(self.cmd_obj_dict)+"\n"+str(self.console_obj_dict))
        w.line.setReadOnly(True)
        w.cancelButton.hide()
        w.line.setFixedSize(800,500)

        w.exec()

    # 打开矢量图池
    def open_sip_pool(self):
        w = TextEditDialog(
            title='矢量图池',
            content="查看在内存中的矢量图池",
            parent=self
        )

        w.line.setText(str(SIP.older()))
        w.line.setReadOnly(True)
        w.cancelButton.hide()
        w.line.setFixedSize(800,500)

        w.exec()

    # 打开音效池
    def open_bsp_pool(self):
        w = TextEditDialog(
            title='音效池',
            content="查看在内存中的音效池",
            parent=self
        )

        w.line.setText(str(BSP.older()))
        w.line.setReadOnly(True)
        w.cancelButton.hide()
        w.line.setFixedSize(800,500)

        w.exec()

