import os

from qtpy.QtCore import Signal, QSize, QPropertyAnimation, Qt, QTimer, QEasingCurve, Property, QRectF
from qtpy.QtGui import QPainter, QColor, QCursor, QIcon, QImage, QPixmap, QMouseEvent
from qtpy.QtWidgets import QFrame, QSizePolicy, QPushButton


# 导航栏按钮
class NavigationBarButton(QFrame):
    """带下边框动画的按钮"""
    clicked = Signal()  # 点击事件信号

    def __init__(self, text="按钮", parent=None):
        super().__init__(parent)        # 设置固定最大最小策略
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # 设置最小/最大尺寸
        self.setMinimumSize(QSize(90, 50))  # 最小尺寸
        self.setMaximumSize(QSize(90, 50))  # 最大尺寸

        self.text = str(text) if text is not None else "按钮"

        # 基本属性
        self._border_width = 0
        self._border_x = 0
        self._is_pressed = False
        self._hovered = False
        self._enabled = True
        self._is_locked = False

        # 动画参数
        self._hover_max_width = 120
        self._default_width = 30
        self._exit_duration = 300
        self._interrupt_duration = 150
        self._press_duration = 100
        self._lock_duration = 200

        # 动画状态
        self._pending_animations = []
        self._is_unlocking = False
        self._is_lock_animating = False
        self._is_in_press_sequence = False
        self._press_sequence_step = 0
        self._border_width_before_disable = 0
        self._was_hovered_before_disable = False
        self._unlock_complete = False
        self._unlock_complete_time = 0

        # 动画对象
        self.width_anim = QPropertyAnimation(self, b"borderWidth")
        self.pos_anim = QPropertyAnimation(self, b"borderX")
        self.setupAnimations()

        # 鼠标设置
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 定时器
        self._mouse_leave_timer = QTimer()
        self._mouse_leave_timer.setSingleShot(True)
        self._mouse_leave_timer.timeout.connect(self.check_mouse_really_left)

        # 启用状态恢复定时器
        self._enable_restore_timer = QTimer()
        self._enable_restore_timer.setSingleShot(True)
        self._enable_restore_timer.timeout.connect(self.perform_enable_animation)

        # 解锁完成后禁用悬停的定时器
        self._unlock_grace_timer = QTimer()
        self._unlock_grace_timer.setSingleShot(True)
        self._unlock_grace_timer.timeout.connect(self.clear_unlock_grace)

        # 动画完成回调
        self.width_anim.finished.connect(self.on_width_animation_finished)
        self.pos_anim.finished.connect(self.on_position_animation_finished)

    def setupAnimations(self):
        """设置动画参数"""
        self.width_anim.setDuration(250)
        self.width_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.pos_anim.setDuration(300)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def interrupt_animations(self):
        """中断所有动画"""
        if self.width_anim.state() == QPropertyAnimation.State.Running:
            self.width_anim.stop()
        if self.pos_anim.state() == QPropertyAnimation.State.Running:
            self.pos_anim.stop()

    def clear_pending_animations(self):
        """清空待处理动画队列"""
        self._pending_animations.clear()

    def add_pending_animation(self, anim_type, start_value, end_value, duration):
        """添加待处理动画"""
        self._pending_animations.append({
            'type': anim_type,
            'start_value': start_value,
            'end_value': end_value,
            'duration': duration
        })

    def process_pending_animations(self):
        """处理待处理动画"""
        if not self._pending_animations or not self._enabled:
            return

        if self._pending_animations:
            anim_data = self._pending_animations.pop(0)
            if anim_data['type'] == 'width':
                self.animate_width_change(anim_data['start_value'], anim_data['end_value'], anim_data['duration'])

    def animate_position_change(self, start_value, end_value, duration=None):
        """位置动画"""
        self.interrupt_animations()
        actual_duration = duration or 300
        self.pos_anim.setDuration(actual_duration)
        self.pos_anim.setStartValue(max(-(self.width() // 2), min(start_value, self.width() // 2)))
        self.pos_anim.setEndValue(max(-(self.width() // 2), min(end_value, self.width() // 2)))
        self.pos_anim.start()

    def animate_border_to_center_fast(self):
        """快速居中边框"""
        target_x = 0
        if abs(self._border_x - target_x) > 1:
            self.animate_position_change(self._border_x, target_x, 80)
        else:
            self._border_x = target_x
            self.update()

    def on_width_animation_finished(self):
        """宽度动画完成处理"""
        if self._pending_animations and self._enabled and not self._is_unlocking:
            QTimer.singleShot(10, self.process_pending_animations)

        # 处理按下序列完成
        if self._is_in_press_sequence and not self._is_unlocking:
            self.handle_press_sequence_completion()
        elif self._is_in_press_sequence and self._is_unlocking:
            # 解锁过程中重置按下序列
            self._is_in_press_sequence = False
            self._press_sequence_step = 0

        # 锁定动画结束后清空动画队列
        if self._is_lock_animating and not self._is_unlocking:
            self.clear_pending_animations()

        self._is_lock_animating = False

    def on_position_animation_finished(self):
        """位置动画完成处理"""
        pass

    def handle_press_sequence_completion(self):
        """处理按下序列完成"""
        if not self._is_in_press_sequence:
            return

        # 如果在解锁过程中，不处理按下序列
        if self._is_unlocking:
            return

        self._press_sequence_step += 1

        if self._press_sequence_step == 1:
            # 按下动画完成
            pass
        elif self._press_sequence_step == 2:
            # 释放动画完成
            self._is_in_press_sequence = False
            self._press_sequence_step = 0

            # 只有在锁定状态下才调整到默认宽度
            if self._is_locked and self._border_width != self._default_width:
                self.animate_width_change(self._border_width, self._default_width, 150)

    def unlock_with_animation(self):
        """解锁动画"""
        if not self._is_locked or not self._enabled:
            return

        self._is_unlocking = True
        self._unlock_complete = False
        # 解锁过程中重置按下序列
        self._is_in_press_sequence = False
        self._press_sequence_step = 0

        cursor_pos = self.mapFromGlobal(self.cursor().pos())
        mouse_inside = self.rect().contains(cursor_pos)

        # 解锁前清空动画队列
        self.clear_pending_animations()
        self._pending_animations.clear()

        # 窄边框淡出到0
        self.animate_width_change(self._border_width, 0, 500)

        # 延迟后执行解锁完成逻辑
        QTimer.singleShot(600, lambda: self.execute_after_unlock(mouse_inside))

    def execute_after_unlock(self, mouse_inside):
        """解锁后动画"""
        if not self._is_unlocking:
            return

        self._is_locked = False
        self._is_unlocking = False
        self._unlock_complete = True
        self._hovered = False
        self._is_pressed = False
        self._unlock_complete_time = 0

        # 确保边框为0
        if self._border_width > 0:
            self._border_width = 0

        # 立即更新显示
        self.update()

        # 设置解锁完成后的宽容期（300ms内不响应悬停）
        self._unlock_grace_timer.start(300)

    def clear_unlock_grace(self):
        """清除解锁宽容期"""
        self._unlock_complete = False

    def perform_lock_transition(self, start_width, target_width):
        """执行锁定过渡"""
        self._is_lock_animating = True

        # 锁定前清空动画队列
        self.clear_pending_animations()

        if self._is_in_press_sequence:
            self._is_in_press_sequence = False

        self.animate_width_change(start_width, target_width, self._lock_duration)

    def perform_enable_animation(self):
        """执行启用动画"""
        if not self._enabled:
            return

        if self._border_width_before_disable > 0:
            # 从0淡入到禁用前的宽度
            self.animate_border_to_center_fast()
            self.animate_width_change(0, self._border_width_before_disable, 400)
            # 重置禁用前的宽度记录
            self._border_width_before_disable = 0

    # ==================== 公共方法 ====================
    def setLocked(self, locked):
        """设置锁定状态"""
        if locked == self._is_locked:
            return

        if locked and (self.width_anim.state() == QPropertyAnimation.State.Running or
                       self.pos_anim.state() == QPropertyAnimation.State.Running):
            # 动画完成后锁定
            self._is_locked = True
        else:
            if locked:
                self._is_locked = True
                self._is_pressed = False
                self._hovered = False
                self._unlock_complete = False

                # 锁定状态下清空动画队列
                self.clear_pending_animations()

                if self._border_width != self._default_width:
                    self.perform_lock_transition(self._border_width, self._default_width)
            else:
                self.unlock_with_animation()

        self.update()

    def is_locked(self):
        """获取锁定状态"""
        return self._is_locked

    def is_enabled(self):
        """获取启用状态"""
        return self._enabled

    def setEnabled(self, enabled):
        """设置启用状态"""
        if enabled is None:
            enabled = True

        old_enabled = self._enabled
        self._enabled = bool(enabled)
        super().setEnabled(self._enabled)

        if old_enabled and not self._enabled:
            # 启用变禁用：记录当前状态
            self._was_hovered_before_disable = self._hovered
            self._border_width_before_disable = self._border_width

            # 如果有边框，执行禁用动画
            if self._border_width > 0:
                self.animate_width_change(self._border_width, 0, 300)

            # 禁用时清空动画队列
            self.clear_pending_animations()

        elif not old_enabled and self._enabled:
            # 禁用变启用：延迟启动恢复动画
            self.interrupt_animations()
            self._hovered = False
            self._is_pressed = False
            self._unlock_complete = False

            # 启用时清空动画队列
            self.clear_pending_animations()

            # 延迟执行启用动画
            self._enable_restore_timer.start(100)

        self.update()

    # ==================== 属性定义 ====================
    @Property(int)
    def borderWidth(self):
        return self._border_width

    @borderWidth.setter
    def borderWidth(self, value):
        if value is None:
            return
        width_val = self.width() or 1
        self._border_width = max(0, min(int(value), width_val))
        self.update()

    @Property(int)
    def borderX(self):
        return self._border_x

    @borderX.setter
    def borderX(self, value):
        if value is None:
            return
        width_val = self.width() or 1
        max_offset = max(1, width_val // 2)
        self._border_x = max(-max_offset, min(int(value), max_offset))
        self.update()

    def get_border_rect(self):
        """获取边框矩形"""
        total_width = max(1, self.width() or 1)
        if total_width <= 0:
            return QRectF(0, 0, 0, 0)

        button_center = total_width // 2
        border_center = button_center + self._border_x
        half_border = max(1, self._border_width // 2)
        left_pos = max(0, min(int(border_center - half_border), int(total_width - self._border_width)))
        height_val = max(1, self.height() or 1)

        return QRectF(
            left_pos,
            max(0, height_val - 8),
            0 if self._border_width <= 0 else self._border_width,
            max(1, 4)
        )

    # ==================== 鼠标事件 ====================
    def enterEvent(self, event):
        if event:
            self._mouse_leave_timer.stop()

        # 解锁过程中或解锁完成后的宽容期内，不处理悬停事件
        if self._is_unlocking or self._unlock_complete or self._is_lock_animating:
            if event:
                super().enterEvent(event)
            return

        if self._enabled and not self._is_pressed and not self._is_locked:
            self._hovered = True
            if self._pending_animations:
                self.process_pending_animations()
            else:
                # 只在非锁定状态下显示宽边框
                target_width = self._hover_max_width
                self.animate_width_change(self._border_width, target_width, 200)

        if event:
            super().enterEvent(event)

    def leaveEvent(self, event):
        if event:
            self._mouse_leave_timer.stop()

        if self._is_unlocking or self._is_lock_animating:
            if event:
                super().leaveEvent(event)
            return

        if self._enabled and (self._hovered or self._border_width > 0):
            if self._is_locked:
                self._hovered = False
                self._is_pressed = False
            else:
                self.interrupt_and_exit_animation()

        self._mouse_leave_timer.start(30)
        if event:
            super().leaveEvent(event)

    def check_mouse_really_left(self):
        """检查鼠标是否真的离开"""
        if not self._enabled or self._is_unlocking or self._is_lock_animating:
            return

        cursor_pos = self.mapFromGlobal(self.cursor().pos())
        if not self.rect().contains(cursor_pos):
            self._hovered = False
            self._is_pressed = False

            if not self._is_locked and self._border_width > 0:
                self.animate_border_to_center()
                self.animate_width_change(self._border_width, 0, self._exit_duration)

    def mouseMoveEvent(self, event: QMouseEvent):
        # 解锁过程中或解锁完成后的宽容期内，不处理鼠标移动事件
        if self._is_unlocking or self._unlock_complete or self._is_lock_animating:
            super().mouseMoveEvent(event)
            return

        if self.rect().contains(event.pos()) and not self._hovered and self._enabled and not self._is_locked:
            self._hovered = True
            self._is_pressed = False
            if self._pending_animations:
                self.process_pending_animations()
            else:
                # 只在非锁定状态下显示宽边框
                target_width = self._hover_max_width
                self.animate_width_change(self._border_width, target_width, 200)
        elif not self.rect().contains(event.pos()) and self._hovered:
            self.leaveEvent(None)

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if self._is_unlocking or self._unlock_complete or self._is_lock_animating:
            super().mousePressEvent(event)
            return

        if event and event.button() == Qt.MouseButton.LeftButton and self._enabled:
            self._is_pressed = True
            self._hovered = True
            self._is_in_press_sequence = True
            self._press_sequence_step = 0

            # 计算目标宽度
            if self._is_locked:
                target_width = max(10, self._default_width - 5)
            else:
                target_width = self._default_width

            if self._pending_animations:
                self.add_pending_animation('width', self._border_width, target_width, self._press_duration)
            else:
                self.animate_width_change(self._border_width, target_width, self._press_duration)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self._is_unlocking or self._unlock_complete or self._is_lock_animating:
            super().mouseReleaseEvent(event)
            return

        if event and event.button() == Qt.MouseButton.LeftButton and self._is_pressed and self._enabled:
            self._is_pressed = False
            if self.rect().contains(event.pos()):
                if not self._is_locked:
                    self.clicked.emit()

                if self._hovered and self._is_in_press_sequence:
                    if self._pending_animations:
                        self._pending_animations.clear()

                    if self._is_locked:
                        target_width = self._default_width
                    else:
                        target_width = self._hover_max_width

                    self.animate_border_to_center()
                    self.animate_width_change(self._border_width, target_width, 250)
                else:
                    self._is_in_press_sequence = False

        super().mouseReleaseEvent(event)

    # ==================== 动画方法 ====================
    def animate_width_change(self, start_value, end_value, duration=None):
        """宽度动画"""
        if start_value is None or end_value is None:
            return

        if not self._enabled:
            self.add_pending_animation('width', start_value, end_value, duration or 250)
            return

        self.interrupt_animations()

        actual_duration = duration or 250
        self.width_anim.setDuration(actual_duration)
        self.width_anim.setStartValue(max(0, int(start_value)))
        self.width_anim.setEndValue(max(0, int(end_value)))

        if end_value > start_value:
            self.width_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        else:
            self.width_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.width_anim.start()

    def animate_border_to_center(self):
        """边框居中"""
        target_x = 0
        if abs(self._border_x - target_x) > 1:
            if not self._enabled:
                self.add_pending_animation('position', self._border_x, target_x, 150)
                return
            self.animate_position_change(self._border_x, target_x, 150)
        else:
            self._border_x = target_x
            self.update()

    def interrupt_and_exit_animation(self):
        """中断并退出动画"""
        self.interrupt_animations()

        if self._border_width > 0:
            if not self._enabled:
                self.add_pending_animation('position', self._border_x, 0, 80)
                self.add_pending_animation('width', self._border_width, 0, self._interrupt_duration)
                return

            self.animate_border_to_center_fast()
            self.animate_width_change(self._border_width, 0, self._interrupt_duration)

    # ==================== 绘制方法 ====================
    def paintEvent(self, event):
        """绘制按钮"""
        if self.width() <= 0 or self.height() <= 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制背景
        if self._enabled:
            if self._is_pressed or self._is_in_press_sequence:
                bg_color = QColor(34, 34, 34)
            elif self._hovered:
                bg_color = QColor(54, 54, 54)
            elif self._is_locked and not self._is_unlocking and not self._is_in_press_sequence:
                bg_color = QColor(40, 40, 40)
            else:
                bg_color = QColor(44, 44, 44)
            painter.fillRect(self.rect(), bg_color)

        # 绘制文字
        if not self._enabled:
            text_color = QColor(150, 150, 150)
        else:
            if self._is_unlocking or self._is_in_press_sequence:
                text_color = QColor(255, 255, 255)
            else:
                text_color = QColor(255, 255, 255) if not self._is_locked else QColor(200, 200, 200)
        painter.setPen(text_color)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)

        # 绘制边框
        if self._enabled:
            if self._is_locked and not self._is_unlocking and not self._is_in_press_sequence:
                self.draw_locked_border(painter)
            elif self._hovered or self._is_pressed or self._border_width > 0 or self._is_unlocking or self._is_in_press_sequence:
                self.draw_border(painter)

    def draw_border(self, painter):
        """绘制正常边框"""
        border_rect = self.get_border_rect()

        if self._is_pressed or self._is_in_press_sequence:
            border_color = QColor(0, 150, 210)
        elif self._hovered or self._border_width > 0 or self._is_unlocking:
            if self._is_unlocking:
                border_color = QColor(0, 200, 255)
            else:
                border_color = QColor(0, 190, 240)
        else:
            return

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(border_color)
        corner_radius = max(2, border_rect.height() // 2)
        painter.drawRoundedRect(border_rect, corner_radius, corner_radius)

    def draw_locked_border(self, painter):
        """绘制锁定边框"""
        border_width = self._default_width
        total_width = max(1, self.width() or 1)
        left_pos = (total_width - border_width) // 2
        height_val = max(1, self.height() or 1)

        border_rect = QRectF(
            left_pos,
            max(0, height_val - 8),
            border_width,
            max(1, 4)
        )

        border_color = QColor(0, 150, 210)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(border_color)
        corner_radius = max(2, border_rect.height() // 2)
        painter.drawRoundedRect(border_rect, corner_radius, corner_radius)

    # ==================== 公共方法 ====================
    def reset_to_default(self):
        """重置到默认状态"""
        if not self._enabled:
            return
        self.interrupt_animations()
        self._hovered = False
        self._is_pressed = False
        self._is_unlocking = False
        self._is_in_press_sequence = False
        self._unlock_complete = False
        self._border_width_before_disable = 0
        self._was_hovered_before_disable = False
        self._pending_animations.clear()
        self.animate_width_change(self._border_width, 0, 250)

# 动画图标按钮
class AnimatedIconButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 初始化状态变量
        self._state = "normal"
        self._mouse_pressed_on_button = False
        self._current_opacity = 1.0
        self._current_darken_factor = 0.0

        # 动画状态跟踪
        self._pending_animation = None
        self._animation_in_progress = False
        self._last_mouse_position = None

        # 创建延迟状态检查定时器
        self._state_check_timer = QTimer()
        self._state_check_timer.setSingleShot(True)
        self._state_check_timer.timeout.connect(self._check_final_state)

        # 保存原始图标
        self._original_icon = self.icon()

        # 创建动画对象
        self._create_animations()

        # 初始化设置
        self.update_button_appearance()

    def _create_animations(self):
        """创建动画对象"""
        # 创建透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"currentOpacity")
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 创建变暗因子动画
        self.darken_animation = QPropertyAnimation(self, b"currentDarkenFactor")
        self.darken_animation.setDuration(150)
        self.darken_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 连接动画完成信号
        self.darken_animation.finished.connect(self._on_darken_animation_finished)
        self.opacity_animation.finished.connect(self._on_opacity_animation_finished)

    def _on_darken_animation_finished(self):
        """变暗动画完成后的处理"""
        self._animation_in_progress = False

        # 动画完成后检查最终状态
        self._state_check_timer.start(50)

        # 检查是否有待执行的动画
        if self._pending_animation is not None:
            target_state, target_darken = self._pending_animation
            self._pending_animation = None
            self._state = target_state
            self.start_darken_animation(target_darken)
        else:
            self.update_button_appearance()

    def _on_opacity_animation_finished(self):
        """透明度动画完成后的处理"""
        self.update_button_appearance()

    def _check_final_state(self):
        """检查并应用最终状态，确保状态同步"""
        # 如果鼠标不在按钮上且没有按下，应该是normal状态
        if (not self._mouse_pressed_on_button and
                not self._is_mouse_over_button() and
                self._state != "normal"):
            self._state = "normal"
            target_darken = self.get_target_darken_factor()
            if abs(self._current_darken_factor - target_darken) > 0.01:
                self.start_darken_animation(target_darken)

    def _is_mouse_over_button(self):
        """更可靠的鼠标位置检测"""
        try:
            global_pos = QCursor.pos()
            local_pos = self.mapFromGlobal(global_pos)
            return self.rect().contains(local_pos)
        except:
            return self.underMouse()

    def enterEvent(self, event):
        """重写鼠标进入事件"""
        if self._state == "disabled":
            super().enterEvent(event)
            return

        # 取消状态检查定时器
        self._state_check_timer.stop()

        # 如果当前是normal状态，才切换到hover状态
        if self._state == "normal" and not self._mouse_pressed_on_button:
            self._state = "hover"
            target_darken = self.get_target_darken_factor()
            self.start_darken_animation(target_darken)
            if self._current_opacity < 1.0:
                self.start_opacity_animation(1.0)

        super().enterEvent(event)

    def leaveEvent(self, event):
        """重写鼠标离开事件"""
        if self._state == "disabled":
            super().leaveEvent(event)
            return

        # 只有在hover或pressed状态且没有按下时才计划切换到normal状态
        if (self._state in ["hover", "pressed"] and
                not self._mouse_pressed_on_button):
            self._state_check_timer.start(10)

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """重写鼠标按下事件"""
        if self._state == "disabled":
            super().mousePressEvent(event)
            return

        # 取消状态检查定时器
        self._state_check_timer.stop()

        if event.button() == Qt.MouseButton.LeftButton:
            self._state = "pressed"
            self._mouse_pressed_on_button = True
            target_darken = self.get_target_darken_factor()
            self.start_darken_animation(target_darken)
            if self._current_opacity < 1.0:
                self.start_opacity_animation(1.0)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """重写鼠标释放事件"""
        if self._state == "disabled":
            super().mouseReleaseEvent(event)
            return

        # 取消状态检查定时器
        self._state_check_timer.stop()

        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_pressed_on_button = False

            # 立即检查鼠标位置来确定状态
            if self._is_mouse_over_button():
                self._state = "hover"
            else:
                self._state = "normal"

            target_darken = self.get_target_darken_factor()
            self.start_darken_animation(target_darken)

        super().mouseReleaseEvent(event)

    def setEnabled(self, enabled):
        """重写setEnabled方法"""
        super().setEnabled(enabled)
        self.set_disabled_state(not enabled)

    def setIcon(self, icon):
        """重写setIcon方法"""
        self._original_icon = icon
        super().setIcon(icon)
        # 立即更新外观
        self.update_button_appearance()

    @Property(float)
    def currentOpacity(self):
        return self._current_opacity

    @currentOpacity.setter
    def currentOpacity(self, value):
        self._current_opacity = max(0.0, min(1.0, value))
        self.update_button_appearance()

    @Property(float)
    def currentDarkenFactor(self):
        return self._current_darken_factor

    @currentDarkenFactor.setter
    def currentDarkenFactor(self, value):
        self._current_darken_factor = max(0.0, min(1.0, value))
        self.update_button_appearance()

    def update_button_appearance(self):
        """更新按钮的外观"""
        icon = self._original_icon
        if icon.isNull():
            super().setIcon(QIcon())
            return

        self.apply_icon_animation(icon)

    def apply_icon_animation(self, icon):
        """对图标应用动画效果"""
        icon_size = self.iconSize()
        if icon_size.isEmpty():
            icon_size = QSize(16, 16)

        try:
            pixmap = icon.pixmap(icon_size)
            if pixmap.isNull():
                pixmap = icon.pixmap(QSize(16, 16))
                if pixmap.isNull():
                    return

            # 应用变暗效果
            if self._current_darken_factor > 0:
                pixmap = self.darken_pixmap(pixmap, self._current_darken_factor)

            # 应用透明度效果
            if self._current_opacity < 1.0:
                pixmap = self.apply_opacity_to_pixmap(pixmap, self._current_opacity)

            new_icon = QIcon(pixmap)
            super().setIcon(new_icon)
            self.setIconSize(icon_size)

        except Exception as e:
            print(f"应用图标动画时出错: {e}")
            super().setIcon(icon)

    def get_target_darken_factor(self):
        """根据当前状态返回目标变暗因子"""
        if self._state == "disabled":
            return 0.6
        elif self._state == "pressed":
            return 0.3
        elif self._state == "hover":
            return 0.15
        else:
            return 0.0

    def start_darken_animation(self, target_darken_factor):
        """启动变暗因子动画"""
        if abs(self._current_darken_factor - target_darken_factor) < 0.01:
            return

        if self._animation_in_progress:
            self._pending_animation = (self._state, target_darken_factor)
            return

        self._animation_in_progress = True
        self.darken_animation.stop()
        self.darken_animation.setStartValue(self._current_darken_factor)
        self.darken_animation.setEndValue(target_darken_factor)
        self.darken_animation.start()

    def start_opacity_animation(self, target_opacity):
        """启动透明度动画"""
        if abs(self._current_opacity - target_opacity) < 0.01:
            return

        self.opacity_animation.stop()
        self.opacity_animation.setStartValue(self._current_opacity)
        self.opacity_animation.setEndValue(target_opacity)
        self.opacity_animation.start()

    def set_disabled_state(self, disabled):
        """设置按钮的禁用状态"""
        self._state_check_timer.stop()

        if disabled:
            self._state = "disabled"
            self.start_darken_animation(0.6)
            self.start_opacity_animation(0.7)
        else:
            if self._is_mouse_over_button():
                self._state = "hover"
            else:
                self._state = "normal"

            target_darken = self.get_target_darken_factor()
            self.start_darken_animation(target_darken)
            self.start_opacity_animation(1.0)

    def darken_pixmap(self, pixmap, factor):
        """对QPixmap应用变暗效果"""
        if factor <= 0:
            return pixmap
        if factor >= 1.0:
            factor = 0.9

        image = pixmap.toImage()
        result_image = QImage(image.size(), QImage.Format.Format_ARGB32_Premultiplied)

        for x in range(image.width()):
            for y in range(image.height()):
                color = image.pixelColor(x, y)
                if color.alpha() > 0:
                    r = int(color.red() * (1 - factor))
                    g = int(color.green() * (1 - factor))
                    b = int(color.blue() * (1 - factor))
                    a = color.alpha()

                    darkened_color = QColor(r, g, b, a)
                    result_image.setPixelColor(x, y, darkened_color)
                else:
                    result_image.setPixelColor(x, y, color)

        return QPixmap.fromImage(result_image)

    def apply_opacity_to_pixmap(self, pixmap, opacity):
        """对QPixmap应用透明度效果"""
        if opacity >= 1.0:
            return pixmap

        result_pixmap = QPixmap(pixmap.size())
        result_pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(result_pixmap)
        painter.setOpacity(opacity)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return result_pixmap

    def darken_hex_color(self, hex_color, factor):
        """对十六进制颜色应用变暗效果"""
        if factor == 0:
            return hex_color

        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c * 2 for c in hex_color)

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))

        return f"#{r:02x}{g:02x}{b:02x}"

    def lighten_hex_color(self, hex_color, factor):
        """对十六进制颜色应用变亮效果"""
        if factor == 0:
            return hex_color

        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c * 2 for c in hex_color)

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))

        return f"#{r:02x}{g:02x}{b:02x}"

# 动画按钮
class AnimatedButton(QPushButton):
    """
    单类实现的动画按钮
    特性：
    1. 悬停/按下/禁用状态平滑颜色过渡
    2. 传入颜色参数 自定义圆角 动画时长
    """

    def __init__(self, text="",
                 normal_color=QColor(52, 152, 219),
                 hover_color=QColor(41, 128, 185),
                 pressed_color=QColor(28, 110, 164),
                 disabled_color=QColor(189, 195, 199),
                 corner_radius=4,
                 parent=None):
        super().__init__(text, parent)

        # 基础配置
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(40)

        # 颜色配置
        self._normal_color = normal_color
        self._hover_color = hover_color
        self._pressed_color = pressed_color
        self._disabled_color = disabled_color
        self._border_radius = corner_radius

        # 状态变量
        self._current_color = self._normal_color
        self._current_opacity = 1.0
        self._state = "normal"
        self._mouse_pressed_on_button = False

        # 保存原始方法
        self._original_enter = self.enterEvent
        self._original_leave = self.leaveEvent
        self._original_press = self.mousePressEvent
        self._original_release = self.mouseReleaseEvent
        self._original_set_enabled = self.setEnabled

        # 初始化
        self._init_animations()
        self._connect_events()
        self.set_button_style()

    def _init_animations(self):
        """初始化动画对象"""
        # 颜色动画
        self.color_animation = QPropertyAnimation(self, b"currentColor")
        self.color_animation.setDuration(200)
        self.color_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._hover_color_animation = QPropertyAnimation(self, b"currentColor")
        self._hover_color_animation.setDuration(25)
        self._hover_color_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._pressed_color_animation = QPropertyAnimation(self, b"currentColor")
        self._pressed_color_animation.setDuration(50)
        self._pressed_color_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._pressed_release_color_animation = QPropertyAnimation(self, b"currentColor")
        self._pressed_release_color_animation.setDuration(150)
        self._pressed_release_color_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"currentOpacity")
        self.opacity_animation.setDuration(100)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def _connect_events(self):
        """连接事件处理"""
        # 重写事件方法
        self.enterEvent = self.handle_enter
        self.leaveEvent = self.handle_leave
        self.mousePressEvent = self.handle_press
        self.mouseReleaseEvent = self.handle_release

        # 覆盖setEnabled方法
        def wrapped_set_enabled(enabled):
            self._original_set_enabled(enabled)
            self.set_disabled_state(not enabled)

        self.setEnabled = wrapped_set_enabled

    # ========== 属性绑定 ==========
    @Property(QColor)
    def currentColor(self):
        return self._current_color

    @currentColor.setter
    def currentColor(self, value):
        self._current_color = value
        self.set_button_style()

    @Property(float)
    def currentOpacity(self):
        return self._current_opacity

    @currentOpacity.setter
    def currentOpacity(self, value):
        self._current_opacity = value
        self.set_button_style()

    # ========== 公开接口 ==========
    def set_animation_duration(self, normal=200, hover=25, pressed=50, release=150):
        """设置各状态动画时长"""
        self.color_animation.setDuration(normal)
        self._hover_color_animation.setDuration(hover)
        self._pressed_color_animation.setDuration(pressed)
        self._pressed_release_color_animation.setDuration(release)

    def set_corner_radius(self, radius):
        """设置圆角半径"""
        self._border_radius = radius
        self.set_button_style()

    def set_disabled_state(self, disabled):
        """设置禁用状态"""
        if disabled:
            self._state = "disabled"
            self.color_animation.stop()
            self.color_animation.setStartValue(self._current_color)
            self.color_animation.setEndValue(self._disabled_color)
            self.color_animation.start()
        else:
            # 恢复到对应状态
            if self._mouse_pressed_on_button:
                target = self._pressed_color
                self._state = "pressed"
            elif self.underMouse():
                target = self._hover_color
                self._state = "hover"
            else:
                target = self._normal_color
                self._state = "normal"

            self.color_animation.stop()
            self.color_animation.setStartValue(self._current_color)
            self.color_animation.setEndValue(target)
            self.color_animation.start()

    # ========== 样式设置 ==========
    def set_button_style(self):
        """设置按钮样式"""
        r, g, b, a = self._current_color.getRgb()
        combined_alpha = (a / 255.0) * self._current_opacity

        qss = f"""
        QPushButton {{
            background-color: rgba({r}, {g}, {b}, {combined_alpha});
            border-radius: {self._border_radius}px;
            border: none;
            color: white;
            padding: 8px 16px;
        }}
        QPushButton:disabled {{
            color: #888888;
        }}
        """
        self.setStyleSheet(qss)

    # ========== 事件处理 ==========
    def handle_enter(self, event):
        if self._state == "disabled":
            self._original_enter(event)
            return

        if not self._mouse_pressed_on_button and self._state != "hover":
            self._state = "hover"
            self._hover_color_animation.stop()
            self._hover_color_animation.setStartValue(self._current_color)
            self._hover_color_animation.setEndValue(self._hover_color)
            self._hover_color_animation.start()
        self._original_enter(event)

    def handle_leave(self, event):
        if self._state == "disabled":
            self._original_leave(event)
            return

        if not self._mouse_pressed_on_button and self._state != "normal":
            self._state = "normal"
            self.color_animation.stop()
            self.color_animation.setStartValue(self._current_color)
            self.color_animation.setEndValue(self._normal_color)
            self.color_animation.start()
        self._original_leave(event)

    def handle_press(self, event):
        if self._state == "disabled" or event.button() != Qt.MouseButton.LeftButton:
            self._original_press(event)
            return

        self._state = "pressed"
        self._mouse_pressed_on_button = True
        self._pressed_color_animation.stop()
        self._pressed_color_animation.setStartValue(self._current_color)
        self._pressed_color_animation.setEndValue(self._pressed_color)
        self._pressed_color_animation.start()
        self._original_press(event)

    def handle_release(self, event):
        if self._state == "disabled" or event.button() != Qt.MouseButton.LeftButton:
            self._original_release(event)
            return

        self._mouse_pressed_on_button = False
        if self.underMouse():
            self._state = "hover"
            self._pressed_release_color_animation.stop()
            self._pressed_release_color_animation.setStartValue(self._current_color)
            self._pressed_release_color_animation.setEndValue(self._hover_color)
            self._pressed_release_color_animation.start()
        else:
            self._state = "normal"
            self.color_animation.stop()
            self.color_animation.setStartValue(self._current_color)
            self.color_animation.setEndValue(self._normal_color)
            self.color_animation.start()
        self._original_release(event)