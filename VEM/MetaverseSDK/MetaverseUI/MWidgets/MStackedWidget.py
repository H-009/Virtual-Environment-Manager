from typing import Optional
from functools import partial

from PyQt5.QtWidgets import QSizePolicy
from qtpy.QtCore import QElapsedTimer
from qtpy.QtCore import Signal, QParallelAnimationGroup, QPropertyAnimation, QEasingCurve, QPoint, QTimer, Qt, QVariantAnimation
from qtpy.QtWidgets import QStackedWidget, QWidget, QGraphicsOpacityEffect, QScrollArea, QApplication


# 动画堆叠窗口
class AnimatedStackedWidget(QStackedWidget):
    # 方向枚举作为类属性
    class Direction:
        HORIZONTAL = "horizontal"
        VERTICAL = "vertical"

    class AnimationDirection:
        LEFT = "left"
        RIGHT = "right"
        UP = "up"
        DOWN = "down"

    # 信号定义
    animationStarted = Signal(int, int)  # current_index, target_index
    animationFinished = Signal(int, int)  # old_index, new_index

    def __init__(self, parent=None, animation_duration: int = 300,
                 slide_direction: str = None):
        """
        :param parent: 父控件
        :param animation_duration: 动画时长（毫秒），默认 300ms
        :param slide_direction: 滑动方向，可选 'horizontal' 或 'vertical'
        """
        super().__init__(parent)

        # ---------- 基本属性 ----------
        self.slide_direction = slide_direction or self.Direction.HORIZONTAL
        self.animation_duration = animation_duration
        self.current_animation: Optional[QParallelAnimationGroup] = None
        self.pending_index: Optional[int] = None
        self.fast_response_enabled: bool = True

        # ---------- 滚动区域状态 ----------
        self._saved_hscroll = 0
        self._saved_vscroll = 0
        self._orig_hpolicy = None
        self._orig_vpolicy = None

        # ---------- 透明度效果管理 ----------
        self._active_effects: dict = {}  # widget -> QGraphicsOpacityEffect

    # ----------------------------------------------------------------------
    # 公共 API
    # ----------------------------------------------------------------------
    def setAnimationDuration(self, ms: int):
        """运行时修改动画时长"""
        self.animation_duration = ms

    def enableFastResponse(self, enabled: bool = True):
        """开启/关闭快速响应模式"""
        self.fast_response_enabled = enabled

    def setSlideDirection(self, direction: str):
        """
        设置滑动方向
        :param direction: self.Direction.HORIZONTAL 或 self.Direction.VERTICAL
        """
        if direction in [self.Direction.HORIZONTAL, self.Direction.VERTICAL]:
            self.slide_direction = direction
        else:
            raise ValueError("direction must be 'horizontal' or 'vertical'")

    def getSlideDirection(self) -> str:
        """获取当前滑动方向"""
        return self.slide_direction

    def addPage(self, widget: QWidget, title: str = ""):
        """便捷方法：添加页面"""
        self.addWidget(widget)
        return self.count() - 1

    def getCurrentPageIndex(self) -> int:
        """获取当前页面索引"""
        return self.currentIndex()

    def getPageCount(self) -> int:
        """获取页面总数"""
        return self.count()

    # ----------------------------------------------------------------------
    # 重写 QStackedWidget 的切换入口
    # ----------------------------------------------------------------------
    def setCurrentIndex(self, index: int):
        """
        重写父类方法，使所有切换都走动画路径。
        若当前已有动画且开启快速响应，则重置动画并直接切换。
        """
        if index == self.currentIndex():
            return

        # 快速响应：已有动画时直接重置
        if self.fast_response_enabled and self.current_animation is not None:
            self.current_animation.setCurrentTime(0)
            self.current_animation = None
            self._cleanup_effects()
            direction = self._calculate_direction(index)
            self._start_animation(index, direction)
            return

        # 正常情况：若已有动画则排队
        if self.current_animation is not None:
            if self.pending_index is None:
                self.pending_index = index
            return

        direction = self._calculate_direction(index)
        self._start_animation(index, direction)

    def setCurrentWidget(self, widget: QWidget):
        """通过widget设置当前页"""
        index = self.indexOf(widget)
        if index != -1:
            self.setCurrentIndex(index)

    # ----------------------------------------------------------------------
    # 动画实现
    # ----------------------------------------------------------------------
    def _calculate_direction(self, target_index: int) -> str:
        """计算滑动方向"""
        current_idx = self.currentIndex()

        if self.slide_direction == self.Direction.HORIZONTAL:
            return self.AnimationDirection.RIGHT if target_index > current_idx else self.AnimationDirection.LEFT
        else:  # VERTICAL
            return self.AnimationDirection.DOWN if target_index > current_idx else self.AnimationDirection.UP

    def _start_animation(self, target_index: int, slide_direction: str):
        """创建并启动页面切换动画"""
        if not (0 <= target_index < self.count()):
            # 越界直接切换
            super().setCurrentIndex(target_index)
            self._check_pending()
            return

        cur_widget = self.currentWidget()
        next_widget = self.widget(target_index)

        # 保存滚动区域状态（如果有的话）
        scroll_area = self._find_scroll_area()
        self._save_scroll_state(scroll_area)

        # 为动画准备环境
        self._prepare_environment(scroll_area, cur_widget, next_widget)

        # 根据方向初始化位置
        size = self.size()
        if self.slide_direction == self.Direction.HORIZONTAL:
            if slide_direction == self.AnimationDirection.RIGHT:
                next_widget.move(size.width(), 0)
            else:  # LEFT
                next_widget.move(-size.width(), 0)
        else:  # VERTICAL
            if slide_direction == self.AnimationDirection.DOWN:
                next_widget.move(0, size.height())
            else:  # UP
                next_widget.move(0, -size.height())

        # ---------- 透明度 ----------
        next_opacity = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(next_opacity)
        self._active_effects[next_widget] = next_opacity
        next_opacity.setOpacity(0.0)

        cur_opacity = QGraphicsOpacityEffect(cur_widget)
        cur_widget.setGraphicsEffect(cur_opacity)
        self._active_effects[cur_widget] = cur_opacity
        cur_opacity.setOpacity(1.0)

        # ---------- 位置动画 ----------
        pos_anim_next = QPropertyAnimation(next_widget, b"pos")
        pos_anim_next.setDuration(self.animation_duration)
        pos_anim_next.setEasingCurve(QEasingCurve.Type.OutCubic)

        pos_anim_cur = QPropertyAnimation(cur_widget, b"pos")
        pos_anim_cur.setDuration(self.animation_duration)
        pos_anim_cur.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 设置起始和结束位置
        start_pos_next, end_pos_next = self._get_position_values(
            next_widget, slide_direction, "next")
        start_pos_cur, end_pos_cur = self._get_position_values(
            cur_widget, slide_direction, "current")

        pos_anim_next.setStartValue(start_pos_next)
        pos_anim_next.setEndValue(end_pos_next)
        pos_anim_cur.setStartValue(start_pos_cur)
        pos_anim_cur.setEndValue(end_pos_cur)

        # ---------- 透明度动画 ----------
        fade_out = QPropertyAnimation(cur_opacity, b"opacity")
        fade_out.setDuration(self.animation_duration)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        fade_in = QPropertyAnimation(next_opacity, b"opacity")
        fade_in.setDuration(self.animation_duration)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)

        # ---------- 合并 ----------
        group = QParallelAnimationGroup()
        group.addAnimation(pos_anim_next)
        group.addAnimation(pos_anim_cur)
        group.addAnimation(fade_in)
        group.addAnimation(fade_out)

        # 发射开始信号
        self.animationStarted.emit(self.currentIndex(), target_index)

        # 动画结束回调
        def on_finished():
            self._animation_finished(target_index, cur_widget, next_widget, scroll_area)

        group.finished.connect(on_finished)
        self.current_animation = group
        group.start()

    def _get_position_values(self, widget: QWidget, slide_direction: str, role: str):
        """根据方向和角色获取位置值"""
        size = self.size()
        pos = widget.pos()

        if self.slide_direction == self.Direction.HORIZONTAL:
            if role == "next":
                if slide_direction == self.AnimationDirection.RIGHT:
                    return QPoint(size.width(), 0), QPoint(0, 0)
                else:  # LEFT
                    return QPoint(-size.width(), 0), QPoint(0, 0)
            else:  # current
                if slide_direction == self.AnimationDirection.RIGHT:
                    return QPoint(0, 0), QPoint(-size.width(), 0)
                else:  # LEFT
                    return QPoint(0, 0), QPoint(size.width(), 0)
        else:  # VERTICAL
            if role == "next":
                if slide_direction == self.AnimationDirection.DOWN:
                    return QPoint(0, size.height()), QPoint(0, 0)
                else:  # UP
                    return QPoint(0, -size.height()), QPoint(0, 0)
            else:  # current
                if slide_direction == self.AnimationDirection.DOWN:
                    return QPoint(0, 0), QPoint(0, -size.height())
                else:  # UP
                    return QPoint(0, 0), QPoint(0, size.height())

    # ----------------------------------------------------------------------
    # 动画结束后的清理工作
    # ----------------------------------------------------------------------
    def _animation_finished(self, target_index, old_widget, new_widget, scroll_area):
        # 清理透明度效果
        for w in (old_widget, new_widget):
            if w in self._active_effects:
                w.setGraphicsEffect(None)
                del self._active_effects[w]

        # 恢复位置
        old_widget.move(0, 0)
        new_widget.move(0, 0)

        # 正式切换索引
        super().setCurrentIndex(target_index)

        # 恢复滚动区域状态
        if scroll_area:
            scroll_area.setHorizontalScrollBarPolicy(self._orig_hpolicy)
            scroll_area.setVerticalScrollBarPolicy(self._orig_vpolicy)
            scroll_area.horizontalScrollBar().setValue(self._saved_hscroll)
            scroll_area.verticalScrollBar().setValue(self._saved_vscroll)
            # 解除尺寸限制
            scroll_area.setMinimumSize(0, 0)
            scroll_area.setMaximumSize(16777215, 16777215)
            self._update_scroll_area(scroll_area)

        # 发射完成信号
        self.animationFinished.emit(old_widget, new_widget)

        # 重置动画对象并检查是否有排队的切换请求
        self.current_animation = None
        self._check_pending()

    # ----------------------------------------------------------------------
    # 排队请求检查
    # ----------------------------------------------------------------------
    def _check_pending(self):
        if self.pending_index is not None:
            idx = self.pending_index
            self.pending_index = None
            self._start_animation(idx, self._calculate_direction(idx))

    # ----------------------------------------------------------------------
    # 辅助工具
    # ----------------------------------------------------------------------
    def _find_scroll_area(self):
        """向上遍历父控件，寻找最近的 QScrollArea（如果有）"""
        p = self.parent()
        while p:
            if isinstance(p, QScrollArea):
                return p
            p = p.parent()
        return None

    def _save_scroll_state(self, scroll_area):
        if scroll_area:
            self._saved_hscroll = scroll_area.horizontalScrollBar().value()
            self._saved_vscroll = scroll_area.verticalScrollBar().value()
            self._orig_hpolicy = scroll_area.horizontalScrollBarPolicy()
            self._orig_vpolicy = scroll_area.verticalScrollBarPolicy()

    def _prepare_environment(self, scroll_area, cur_widget, next_widget):
        """确保动画期间布局不受干扰"""
        # 统一尺寸
        next_widget.setFixedSize(cur_widget.size())
        next_widget.show()
        next_widget.raise_()

        if scroll_area:
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll_area.setFixedSize(scroll_area.size())
            self._update_scroll_area(scroll_area)

    def _update_scroll_area(self, scroll_area):
        """强制刷新滚动区域的布局与几何信息"""
        if not scroll_area:
            return
        scroll_area.viewport().update()
        scroll_area.updateGeometry()
        scroll_area.adjustSize()
        content = scroll_area.widget()
        if content:
            content.updateGeometry()
            content.adjustSize()
            layout = content.layout()
            if layout:
                layout.update()

    def _cleanup_effects(self):
        """在快速响应时清除残留的透明度效果"""
        for w, eff in list(self._active_effects.items()):
            if w.graphicsEffect() == eff:
                w.setGraphicsEffect(None)
        self._active_effects.clear()

    # ----------------------------------------------------------------------
    # 重写尺寸变化处理
    # ----------------------------------------------------------------------
    def resizeEvent(self, event):
        """窗口大小改变时重新调整子控件大小"""
        super().resizeEvent(event)
        # 如果当前有动画，可能需要更新动画参数
        if self.current_animation and self.count() > 0:
            current_widget = self.currentWidget()
            if current_widget:
                for child in self.children():
                    if isinstance(child, QPropertyAnimation):
                        # 这里可以添加动态调整逻辑
                        pass

    # ----------------------------------------------------------------------
    # 便捷工厂方法
    # ----------------------------------------------------------------------
    @classmethod
    def createHorizontal(cls, parent=None, duration=300):
        """创建水平滑动的实例"""
        return cls(parent, duration, cls.Direction.HORIZONTAL)

    @classmethod
    def createVertical(cls, parent=None, duration=300):
        """创建垂直滑动的实例"""
        return cls(parent, duration, cls.Direction.VERTICAL)

# 动画简单堆叠窗口
class SimpleAnimatedStackedWidget(QStackedWidget):
    animationStarted = Signal(int, int)
    animationFinished = Signal(int, int)

    class Direction:
        HORIZONTAL = "horizontal"
        VERTICAL = "vertical"

    def __init__(self, parent=None, animation_duration: int = 300, direction: str = Direction.HORIZONTAL):
        super().__init__(parent)
        self.direction = direction
        self.duration = animation_duration
        self.current_animation = None
        self.pending_index = None
        self.effects = {}
        self._initialized = False
        self._pending_operations = []
        self._layout_validated = False  # 新增：布局验证标志

    def showEvent(self, event):
        """确保控件完全初始化后再允许动画"""
        super().showEvent(event)
        # 延迟初始化，确保所有子控件布局完成
        QTimer.singleShot(50, self._on_initialized)

    def _on_initialized(self):
        """初始化完成后的回调"""
        self._initialized = True
        self._layout_validated = True
        self._validate_all_layouts()
        # 处理待执行的操作
        self._process_pending_operations()

    def _validate_all_layouts(self):
        """验证并激活所有子控件的布局"""
        for i in range(self.count()):
            widget = self.widget(i)
            if widget:
                # 强制更新几何信息
                widget.updateGeometry()
                # 激活布局
                if widget.layout():
                    widget.layout().activate()
                # 强制重绘
                widget.repaint()

        # 处理父级布局
        self.updateGeometry()
        if self.layout():
            self.layout().activate()

        # 强制自身重绘
        self.repaint()

    def resizeEvent(self, event):
        """窗口大小改变时确保控件正确布局"""
        super().resizeEvent(event)
        # 标记布局需要重新验证
        self._layout_validated = False
        # 延迟重新验证布局
        QTimer.singleShot(10, self._delayed_layout_validation)

    def _delayed_layout_validation(self):
        """延迟的布局验证"""
        if not self._layout_validated and self._initialized:
            self._validate_all_layouts()
            self._layout_validated = True

    def setCurrentIndex(self, index: int, animated: bool = True):
        """设置当前页面索引"""
        if index == self.currentIndex():
            return

        operation = ('set_index', index, animated)
        if not self._can_execute_operation():
            self._pending_operations.append(operation)
            return

        if not animated:
            self._direct_set_current_index(index)
            return

        # 处理动画冲突
        if self.current_animation:
            if self.pending_index is None:
                self.pending_index = index
            return

        self._start_animation(index)

    def setCurrentWidget(self, widget: QWidget, animated: bool = True):
        """通过widget设置当前页"""
        self.setCurrentIndex(self.indexOf(widget), animated)

    def setCurrentIndexNoAnimation(self, index: int):
        """无动画设置当前页面"""
        self.setCurrentIndex(index, animated=False)

    def setCurrentWidgetNoAnimation(self, widget: QWidget):
        """无动画设置当前widget - 这是您需要的方法"""
        self.setCurrentIndexNoAnimation(self.indexOf(widget))

    def _can_execute_operation(self):
        """检查是否可以执行操作"""
        # 确保控件已初始化且有子控件
        if not self._initialized or self.count() == 0:
            return False

        # 确保布局已验证
        if not self._layout_validated:
            return False

        # 确保当前控件有效且可见
        current_widget = self.currentWidget()
        if not current_widget or not current_widget.isVisible():
            return False

        # 确保尺寸有效
        size = self.size()
        if size.width() <= 0 or size.height() <= 0:
            return False

        return True

    def _process_pending_operations(self):
        """处理待执行的操作"""
        if not self._pending_operations:
            return

        # 复制列表避免在迭代时修改
        operations = self._pending_operations.copy()
        self._pending_operations.clear()

        for operation in operations:
            op_type, *args = operation
            if op_type == 'set_index':
                index, animated = args
                # 延迟执行，确保布局完成
                QTimer.singleShot(10, lambda idx=index, anim=animated:
                self._execute_set_index(idx, anim))

    def _execute_set_index(self, index: int, animated: bool):
        """实际执行设置索引的操作"""
        if not self._can_execute_operation():
            # 如果还不能执行，重新加入队列
            self._pending_operations.append(('set_index', index, animated))
            return

        if not animated:
            self._direct_set_current_index(index)
        else:
            self._start_animation(index)

    def _ensure_widget_ready(self, widget: QWidget):
        """确保控件准备好进行动画 - 增强版本"""
        if not widget:
            return False

        # 确保控件可见
        widget.setVisible(True)

        # 如果布局未验证，先验证布局
        if not self._layout_validated:
            self._validate_all_layouts()
            self._layout_validated = True

        # 强制更新几何信息和布局
        widget.updateGeometry()
        if widget.layout():
            widget.layout().activate()

        # 确保控件有正确的尺寸（基于当前堆叠窗口的实际尺寸）
        stack_size = self.size()
        if widget.size() != stack_size:
            widget.resize(stack_size)

        # 强制重绘
        widget.repaint()

        # 短暂延迟确保渲染完成
        QApplication.processEvents()

        return True

    def _direct_set_current_index(self, index: int):
        """直接设置当前索引，无动画"""
        if not (0 <= index < self.count()):
            return

        self._cleanup()

        # 确保新控件准备好
        new_widget = self.widget(index)
        if new_widget and self._ensure_widget_ready(new_widget):
            super().setCurrentIndex(index)
            new_widget.move(0, 0)
            new_widget.setGraphicsEffect(None)
        else:
            # 如果控件未准备好，使用默认方法
            super().setCurrentIndex(index)

    def _start_animation(self, target_index: int):
        """开始动画 - 修复尺寸获取时机"""
        if not (0 <= target_index < self.count()):
            self._direct_set_current_index(target_index)
            self._check_pending()
            return

        # 在执行动画前再次验证布局
        if not self._layout_validated:
            self._validate_all_layouts()
            self._layout_validated = True

        old_widget = self.currentWidget()
        new_widget = self.widget(target_index)

        # 确保控件准备好
        if not self._ensure_widget_ready(old_widget) or not self._ensure_widget_ready(new_widget):
            # 如果控件仍未准备好，延迟重试
            QTimer.singleShot(20, lambda: self._start_animation(target_index))
            return

        # 获取准确的尺寸（在布局验证后）
        size = self.size()

        # 准备控件层级
        old_widget.show()
        new_widget.show()
        new_widget.raise_()

        # 计算动画方向
        current_idx = self.currentIndex()
        if self.direction == self.Direction.HORIZONTAL:
            if target_index > current_idx:
                new_start = QPoint(size.width(), 0)
                new_end = QPoint(0, 0)
                old_end = QPoint(-size.width(), 0)
            else:
                new_start = QPoint(-size.width(), 0)
                new_end = QPoint(0, 0)
                old_end = QPoint(size.width(), 0)
        else:
            if target_index > current_idx:
                new_start = QPoint(0, size.height())
                new_end = QPoint(0, 0)
                old_end = QPoint(0, -size.height())
            else:
                new_start = QPoint(0, -size.height())
                new_end = QPoint(0, 0)
                old_end = QPoint(0, size.height())

        # 设置初始位置
        try:
            new_widget.move(new_start)
            old_widget.move(0, 0)
        except:
            self._direct_set_current_index(target_index)
            return

        # 设置透明度效果
        self._setup_opacity_effects(old_widget, new_widget)

        # 创建动画组
        self.current_animation = QParallelAnimationGroup()

        # 新页面位置动画
        new_pos_anim = QPropertyAnimation(new_widget, b"pos")
        new_pos_anim.setDuration(self.duration)
        new_pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        new_pos_anim.setStartValue(new_start)
        new_pos_anim.setEndValue(new_end)

        # 旧页面位置动画
        old_pos_anim = QPropertyAnimation(old_widget, b"pos")
        old_pos_anim.setDuration(self.duration)
        old_pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        old_pos_anim.setStartValue(QPoint(0, 0))
        old_pos_anim.setEndValue(old_end)

        # 透明度动画
        new_opacity_anim = QPropertyAnimation(self.effects[new_widget], b"opacity")
        new_opacity_anim.setDuration(self.duration)
        new_opacity_anim.setStartValue(0.0)
        new_opacity_anim.setEndValue(1.0)

        old_opacity_anim = QPropertyAnimation(self.effects[old_widget], b"opacity")
        old_opacity_anim.setDuration(self.duration)
        old_opacity_anim.setStartValue(1.0)
        old_opacity_anim.setEndValue(0.0)

        # 添加到动画组
        self.current_animation.addAnimation(new_pos_anim)
        self.current_animation.addAnimation(old_pos_anim)
        self.current_animation.addAnimation(new_opacity_anim)
        self.current_animation.addAnimation(old_opacity_anim)

        # 连接信号
        self.animationStarted.emit(current_idx, target_index)
        self.current_animation.finished.connect(lambda: self._animation_finished(target_index))
        self.current_animation.start()

    def _setup_opacity_effects(self, old_widget, new_widget):
        """设置透明度效果"""
        self._cleanup_effects()

        try:
            new_effect = QGraphicsOpacityEffect(new_widget)
            new_effect.setOpacity(0.0)
            new_widget.setGraphicsEffect(new_effect)
            self.effects[new_widget] = new_effect

            old_effect = QGraphicsOpacityEffect(old_widget)
            old_effect.setOpacity(1.0)
            old_widget.setGraphicsEffect(old_effect)
            self.effects[old_widget] = old_effect
        except:
            # 如果设置效果失败，继续无透明度动画
            pass

    def _animation_finished(self, target_index):
        """动画完成处理"""
        try:
            old_widget = self.currentWidget()
            self._cleanup()
            super().setCurrentIndex(target_index)
            self.animationFinished.emit(old_widget, self.widget(target_index))
            self._check_pending()
        except:
            # 如果动画完成处理失败，确保直接切换
            self._direct_set_current_index(target_index)

    def _cleanup(self):
        """清理动画资源"""
        try:
            if self.current_animation:
                self.current_animation.stop()
                self.current_animation = None
            self._cleanup_effects()
        except:
            pass

    def _cleanup_effects(self):
        """清理透明度效果"""
        try:
            for widget, effect in self.effects.items():
                try:
                    if widget and widget.graphicsEffect() == effect:
                        widget.setGraphicsEffect(None)
                except:
                    continue
            self.effects.clear()
        except:
            pass

    def _check_pending(self):
        """检查待处理的页面切换"""
        if self.pending_index is not None:
            idx = self.pending_index
            self.pending_index = None
            # 延迟执行，确保状态稳定
            QTimer.singleShot(10, lambda: self.setCurrentIndex(idx))

    # 便捷方法
    def setAnimationDuration(self, duration: int):
        self.duration = duration

    def setSlideDirection(self, direction: str):
        if direction in [self.Direction.HORIZONTAL, self.Direction.VERTICAL]:
            self.direction = direction

    @classmethod
    def horizontal(cls, parent=None, duration=300):
        return cls(parent, duration, cls.Direction.HORIZONTAL)

    @classmethod
    def vertical(cls, parent=None, duration=300):
        return cls(parent, duration, cls.Direction.VERTICAL)

    def force_refresh(self):
        """强制刷新控件状态"""
        self._initialized = False
        self._layout_validated = False
        QTimer.singleShot(100, self._force_refresh_delayed)

    def _force_refresh_delayed(self):
        """延迟刷新"""
        self._initialized = True
        self._layout_validated = True
        self._process_pending_operations()
        # 强制更新所有子控件
        for i in range(self.count()):
            widget = self.widget(i)
            if widget:
                widget.updateGeometry()
                widget.update()

# 上下弹出堆叠部件
class PopUpAniUpDownStackedWidget(QStackedWidget):
    """Win11 Settings 风格 · 上下滑入滑出（双页同显）"""

    aniFinished = Signal()
    aniStart = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isAnimationEnabled = True

        self._timer = QTimer(self)
        self._timer.setInterval(8)
        self._timer.timeout.connect(self._on_frame)

        self._animating = False
        self._duration = 420
        self._elapsed = 0

        self._curWidget = None
        self._nextWidget = None
        self._curStart = QPoint()
        self._curEnd = QPoint()
        self._nextStart = QPoint()
        self._nextEnd = QPoint()
        self._lastCurEnd = QPoint()

    # ------------------------------------------------------------------
    def setAnimationEnabled(self, enabled: bool):
        self.isAnimationEnabled = enabled

    def setDefaultDuration(self, ms: int):
        self._duration = ms

    # ------------------------------------------------------------------
    def setCurrentIndex(self, index: int, duration: int = None,
                        easingCurve=None, direction: str = 'auto',
                        parallel: bool = True):

        if index < 0 or index >= self.count() or index == self.currentIndex():
            return
        if not self.isAnimationEnabled:
            return super().setCurrentIndex(index)

        duration = duration or self._duration
        curIdx = self.currentIndex()

        if direction == 'auto':
            direction = 'down' if index > curIdx else 'up'

        h = self.height()
        margins = self.contentsMargins()
        origin = QPoint(margins.left(), margins.top())

        self._curWidget = self.widget(curIdx)
        self._nextWidget = self.widget(index)

        if direction == 'up':
            self._curStart = origin
            self._curEnd = QPoint(origin.x(), origin.y() - h)
            self._nextStart = QPoint(origin.x(), origin.y() + h)
            self._nextEnd = origin
        else:
            self._curStart = origin
            self._curEnd = QPoint(origin.x(), origin.y() + h)
            self._nextStart = QPoint(origin.x(), origin.y() - h)
            self._nextEnd = origin

        self._lastCurEnd = self._curEnd

        self._nextWidget.move(self._nextStart)
        self._nextWidget.show()
        self._nextWidget.raise_()
        self._curWidget.show()
        self._curWidget.lower()

        super().setCurrentIndex(index)

        self._elapsed = 0
        self._animating = True
        self._timer.start()
        self.aniStart.emit()

    def setCurrentWidget(self, widget: QWidget, **kwargs):
        idx = self.indexOf(widget)
        if idx != -1:
            self.setCurrentIndex(idx, **kwargs)

    @staticmethod
    def _win11_ease_func(progress: float) -> float:
        p1x, p1y = 0.2, 0.0
        p2x, p2y = 0.0, 1.0
        cx = 3.0 * p1x
        bx = 3.0 * (p2x - p1x) - cx
        ax = 1.0 - cx - bx
        cy = 3.0 * p1y
        by = 3.0 * (p2y - p1y) - cy
        ay = 1.0 - cy - by
        t = progress
        for _ in range(8):
            v = ((ax * t + bx) * t + cx) * t - progress
            d = (3.0 * ax * t + 2.0 * bx) * t + cx
            if abs(d) < 1e-6:
                break
            t -= v / d
        t = max(0.0, min(1.0, t))
        return ((ay * t + by) * t + cy) * t

    # ------------------------------------------------------------------
    def _on_frame(self):
        if not self._animating:
            self._timer.stop()
            return

        self._elapsed += self._timer.interval()
        raw = min(1.0, self._elapsed / self._duration)
        eased = self._win11_ease_func(raw)

        if self._curWidget:
            cy = int(self._curStart.y() + (self._curEnd.y() - self._curStart.y()) * eased)
            self._curWidget.move(self._curStart.x(), cy)

        if self._nextWidget:
            ny = int(self._nextStart.y() + (self._nextEnd.y() - self._nextStart.y()) * eased)
            self._nextWidget.move(self._nextStart.x(), ny)

        if raw >= 1.0:
            self._animating = False
            self._timer.stop()

            margins = self.contentsMargins()
            if self._nextWidget:
                self._nextWidget.move(margins.left(), margins.top())
                self._nextWidget.raise_()

            if self._curWidget:
                self._curWidget.move(self._lastCurEnd)
                self._curWidget.hide()

            self.aniFinished.emit()

    # ------------------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._animating:
            margins = self.contentsMargins()
            w = self.currentWidget()
            if w:
                w.move(margins.left(), margins.top())

# 左右弹出堆叠部件
class PopUpAniLeftRightStackedWidget(QStackedWidget):
    """左右滑入滑出（双页同显）"""

    aniFinished = Signal()
    aniStart = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isAnimationEnabled = True

        self._timer = QTimer(self)
        self._timer.setInterval(8)
        self._timer.timeout.connect(self._on_frame)

        self._animating = False
        self._duration = 420
        self._elapsed = 0

        self._curWidget = None
        self._nextWidget = None
        self._curStart = QPoint()
        self._curEnd = QPoint()
        self._nextStart = QPoint()
        self._nextEnd = QPoint()
        self._lastCurEnd = QPoint()

    # ------------------------------------------------------------------
    def setAnimationEnabled(self, enabled: bool):
        self.isAnimationEnabled = enabled

    def setDefaultDuration(self, ms: int):
        self._duration = ms

    # ------------------------------------------------------------------
    def setCurrentIndex(self, index: int, duration: int = None,
                        direction: str = 'auto'):
        """
        direction: 'auto' | 'left' | 'right'
            - 'left'  : 当前页向左滑出，新页从右侧滑入
            - 'right' : 当前页向右滑出，新页从左侧滑入
            - 'auto'  : index > curIdx → left, 否则 right
        """
        if index < 0 or index >= self.count() or index == self.currentIndex():
            return
        if not self.isAnimationEnabled:
            return super().setCurrentIndex(index)

        duration = duration or self._duration
        curIdx = self.currentIndex()

        if direction == 'auto':
            direction = 'left' if index > curIdx else 'right'

        w = self.width()
        margins = self.contentsMargins()
        origin = QPoint(margins.left(), margins.top())

        self._curWidget = self.widget(curIdx)
        self._nextWidget = self.widget(index)

        if direction == 'left':
            # 当前页向左滑出，新页从右侧滑入
            self._curStart = origin
            self._curEnd = QPoint(origin.x() - w, origin.y())
            self._nextStart = QPoint(origin.x() + w, origin.y())
            self._nextEnd = origin
        else:
            # 当前页向右滑出，新页从左侧滑入
            self._curStart = origin
            self._curEnd = QPoint(origin.x() + w, origin.y())
            self._nextStart = QPoint(origin.x() - w, origin.y())
            self._nextEnd = origin

        self._lastCurEnd = self._curEnd

        self._nextWidget.move(self._nextStart)
        self._nextWidget.show()
        self._nextWidget.raise_()
        self._curWidget.show()
        self._curWidget.lower()

        super().setCurrentIndex(index)

        self._elapsed = 0
        self._animating = True
        self._timer.start()
        self.aniStart.emit()

    def setCurrentWidget(self, widget: QWidget, **kwargs):
        idx = self.indexOf(widget)
        if idx != -1:
            self.setCurrentIndex(idx, **kwargs)

    # ------------------------------------------------------------------
    @staticmethod
    def _win11_ease_func(progress: float) -> float:
        """Win11 风格缓动曲线 (0.2, 0.0, 0.0, 1.0)"""
        p1x, p1y = 0.2, 0.0
        p2x, p2y = 0.0, 1.0
        cx = 3.0 * p1x
        bx = 3.0 * (p2x - p1x) - cx
        ax = 1.0 - cx - bx
        cy = 3.0 * p1y
        by = 3.0 * (p2y - p1y) - cy
        ay = 1.0 - cy - by
        t = progress
        for _ in range(8):
            v = ((ax * t + bx) * t + cx) * t - progress
            d = (3.0 * ax * t + 2.0 * bx) * t + cx
            if abs(d) < 1e-6:
                break
            t -= v / d
        t = max(0.0, min(1.0, t))
        return ((ay * t + by) * t + cy) * t

    # ------------------------------------------------------------------
    def _on_frame(self):
        if not self._animating:
            self._timer.stop()
            return

        self._elapsed += self._timer.interval()
        raw = min(1.0, self._elapsed / self._duration)
        eased = self._win11_ease_func(raw)

        if self._curWidget:
            cx = int(self._curStart.x() + (self._curEnd.x() - self._curStart.x()) * eased)
            self._curWidget.move(cx, self._curStart.y())

        if self._nextWidget:
            nx = int(self._nextStart.x() + (self._nextEnd.x() - self._nextStart.x()) * eased)
            self._nextWidget.move(nx, self._nextStart.y())

        if raw >= 1.0:
            self._animating = False
            self._timer.stop()

            margins = self.contentsMargins()
            if self._nextWidget:
                self._nextWidget.move(margins.left(), margins.top())
                self._nextWidget.raise_()

            if self._curWidget:
                self._curWidget.move(self._lastCurEnd)
                self._curWidget.hide()

            self.aniFinished.emit()

    # ------------------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._animating:
            margins = self.contentsMargins()
            w = self.currentWidget()
            if w:
                w.move(margins.left(), margins.top())

# 上下冻结翻页堆叠部件
class PageFreezeUpDownStackedWidget(QWidget):
    aniFinished = Signal()
    aniStart = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._duration = 420
        self._animating = False

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self._duration)
        self._anim.setEasingCurve(QEasingCurve.Linear)   # 缓动自己在 _ease 里做
        self._anim.valueChanged.connect(self._on_value)
        self._anim.finished.connect(self._on_finished)

        self._pages = []
        self._currentIndex = -1
        self._cur = self._nxt = None
        self._targetIndex = -1
        self._cy0 = self._cy1 = self._ny0 = self._ny1 = 0

        self._dead = set()      # 已销毁页面的 id()
        self._hooks = {}        # id(w) -> destroyed 槽

        # 布局冻结恢复用
        self._saved_size_policy = None
        self._saved_min_size = None
        self._saved_max_size = None

    # ================= 布局冻结（防崩溃核心） =================
    def _freeze_layout(self):
        """动画开始前：冻结布局，防止布局系统插手"""
        self._saved_size_policy = self.sizePolicy()
        self._saved_min_size = self.minimumSize()
        self._saved_max_size = self.maximumSize()

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumSize(self.size())
        self.setMaximumSize(self.size())

        # 禁用父布局，防止父布局在动画期间刷新
        p = self.parentWidget()
        if p and p.layout():
            p.layout().setEnabled(False)

    def _unfreeze_layout(self):
        """动画结束后：恢复布局控制，并强制刷新一次"""
        p = self.parentWidget()

        #  先恢复父布局启用状态
        if p and p.layout():
            p.layout().setEnabled(True)

        # 恢复自身布局属性
        if self._saved_size_policy is not None:
            self.setSizePolicy(self._saved_size_policy)
        if self._saved_min_size is not None:
            self.setMinimumSize(self._saved_min_size)
        if self._saved_max_size is not None:
            self.setMaximumSize(self._saved_max_size)

        # 通知布局系统：几何已变
        self.updateGeometry()

        # 强制父布局立即重算（关键）
        if p and p.layout():
            p.layout().update()

    # ================= 通用存活判断 =================
    def _alive(self, w) -> bool:
        if w is None:
            return False
        if id(w) in self._dead:
            return False
        try:
            w.isVisible()
        except (RuntimeError, TypeError):
            self._dead.add(id(w))
            return False
        return True

    # ---------------- 生命周期看守 ----------------
    def _watch(self, w):
        if w is None or not self._alive(w):
            return
        key = id(w)
        if key in self._hooks:
            return
        hook = partial(self._on_page_destroyed, w)
        try:
            w.destroyed.connect(hook)
        except (RuntimeError, TypeError):
            return
        self._hooks[key] = hook

    def _unwatch(self, w):
        if w is None:
            return
        key = id(w)
        hook = self._hooks.pop(key, None)
        if hook is not None and self._alive(w):
            try:
                w.destroyed.disconnect(hook)
            except (RuntimeError, TypeError):
                pass
        self._dead.discard(key)
        self._hooks.pop(key, None)

    def _on_page_destroyed(self, w, _obj=None):
        key = id(w)
        self._dead.add(key)
        self._hooks.pop(key, None)
        try:
            if w in self._pages:
                self._pages.remove(w)
        except ValueError:
            pass
        if self._animating and (w is self._cur or w is self._nxt):
            self._abort()

    # ================= Public API =================
    def duration(self):
        return self._duration

    def setDuration(self, ms: int):
        self._duration = int(ms)
        self._anim.setDuration(self._duration)

    def addWidget(self, w: QWidget):
        if not self._alive(w):
            return
        try:
            w.setParent(self)
            w.setGeometry(0, 0, self.width(), self.height())
            w.hide()
        except RuntimeError:
            return
        self._pages.append(w)
        self._watch(w)
        if self._currentIndex == -1:
            self._currentIndex = 0
            try:
                w.setGeometry(0, 0, self.width(), self.height())
                w.show()
            except RuntimeError:
                pass

    def removeWidget(self, w: QWidget):
        if self._animating and (w is self._cur or w is self._nxt):
            self._settle(emit=False)
        if w not in self._pages:
            return
        idx = self._pages.index(w)
        self._pages.remove(w)
        self._unwatch(w)
        try:
            w.setParent(None)
            w.hide()
        except RuntimeError:
            pass
        if idx < self._currentIndex:
            self._currentIndex -= 1
        self._currentIndex = max(-1, min(self._currentIndex, len(self._pages) - 1))
        if self._cur is w:
            self._cur = None
        if self._nxt is w:
            self._nxt = None

    def count(self):
        return len(self._pages)

    def currentIndex(self): return self._currentIndex

    def currentWidget(self):
        if 0 <= self._currentIndex < len(self._pages):
            return self._pages[self._currentIndex]
        return None

    def setCurrentWidget(self, widget: QWidget):
        try:
            self.setCurrentIndex(self._pages.index(widget))
        except ValueError:
            return

    def setCurrentIndex(self, index, direction="auto"):
        if index < 0 or index >= len(self._pages):
            return
        if self._animating and index == self._targetIndex:
            return
        if self._animating:
            self._settle(emit=True)
        if index == self._currentIndex:
            return

        cur = self.currentWidget()
        nxt = self._pages[index]
        if not self._alive(cur) or not self._alive(nxt):
            return

        h, w = self.height(), self.width()
        if direction == "auto":
            direction = "down" if index > self._currentIndex else "up"

        if direction == "up":
            self._cy0, self._cy1 = 0, h
            self._ny0, self._ny1 = -h, 0
        else:
            self._cy0, self._cy1 = 0, -h
            self._ny0, self._ny1 = h, 0

        try:
            nxt.setParent(self)
            nxt.setGeometry(0, self._ny0, w, h)
            nxt.show()
            nxt.raise_()
            cur.setGeometry(0, 0, w, h)
            cur.show()
        except RuntimeError:
            return

        self._cur, self._nxt = cur, nxt
        self._targetIndex = index
        self._watch(cur)
        self._watch(nxt)

        # 动画开始前冻结布局
        self._animating = True
        self._freeze_layout()
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        self.aniStart.emit()

    def stopAnimation(self):
        if self._animating:
            self._settle(emit=False)

    # ================= Animation =================
    def _place(self, w, y, ww, hh) -> bool:
        if not self._alive(w):
            return False
        try:
            w.setGeometry(0, y, ww, hh)
            return True
        except RuntimeError:
            return False

    def _on_value(self, t):
        if not self._animating:
            return
        try:
            e = self._ease(float(t))
            h, w = self.height(), self.width()
            cy = int(self._cy0 + (self._cy1 - self._cy0) * e)
            ny = int(self._ny0 + (self._ny1 - self._ny0) * e)
            if not (self._place(self._cur, cy, w, h) and
                    self._place(self._nxt, ny, w, h)):
                self._abort()
        except RuntimeError:
            self._abort()

    def _on_finished(self):
        if self._animating:
            self._settle(emit=True)

    def _abort(self):
        self._animating = False
        try:
            self._anim.stop()
        except RuntimeError:
            pass
        self._cur = self._nxt = None
        self._targetIndex = -1

    def _settle(self, emit=True):
        if not self._animating:
            return
        self._animating = False
        self._anim.stop()

        # 动画结束后恢复布局
        self._unfreeze_layout()

        cur, nxt, target = self._cur, self._nxt, self._targetIndex
        h, w = self.height(), self.width()

        if self._alive(nxt):
            try:
                nxt.setGeometry(0, 0, w, h)
                nxt.show()
                nxt.raise_()
            except RuntimeError:
                pass
            self._currentIndex = target
        if self._alive(cur) and cur is not nxt:
            try:
                cur.hide()
            except RuntimeError:
                pass

        self._unwatch(cur)
        self._unwatch(nxt)
        self._cur = self._nxt = None
        self._targetIndex = -1
        if emit:
            self.aniFinished.emit()

    def _ease(self, t: float) -> float:
        p1x, p1y = 0.2, 0.0
        p2x, p2y = 0.0, 1.0
        cx = 3 * p1x
        bx = 3 * (p2x - p1x) - cx
        ax = 1 - cx - bx
        cy = 3 * p1y
        by = 3 * (p2y - p1y) - cy
        ay = 1 - cy - by
        x = t
        for _ in range(8):
            v = ((ax * x + bx) * x + cx) * x - t
            d = (3 * ax * x + 2 * bx) * x + cx
            if abs(d) < 1e-6:
                break
            x -= v / d
        x = max(0.0, min(1.0, x))
        return ((ay * x + by) * x + cy) * x

    # ================= Events =================
    def hideEvent(self, e):
        super().hideEvent(e)
        if self._animating:
            self._settle(emit=True)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        w, h = self.width(), self.height()

        if self._animating:
            # ✅ 动画期间只改尺寸，不改坐标
            for pg in (self._cur, self._nxt):
                if self._alive(pg):
                    try:
                        pg.resize(w, h)
                    except RuntimeError:
                        pass
        elif self._alive(self.currentWidget()):
            self.currentWidget().setGeometry(0, 0, w, h)

# 上下翻页堆叠部件
class PageUpDownStackedWidget(QWidget):
    aniFinished = Signal()
    aniStart = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._duration = 420
        self._animating = False

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self._duration)
        self._anim.setEasingCurve(QEasingCurve.Linear)   # 缓动自己在 _ease 里做
        self._anim.valueChanged.connect(self._on_value)
        self._anim.finished.connect(self._on_finished)

        self._pages = []
        self._currentIndex = -1
        self._cur = self._nxt = None
        self._targetIndex = -1
        self._cy0 = self._cy1 = self._ny0 = self._ny1 = 0

        self._dead = set()      # 已销毁页面的 id()
        self._hooks = {}        # id(w) -> destroyed 槽

    # ================= 通用存活判断（零绑定判断） =================
    def _alive(self, w) -> bool:
        """跨 PyQt5/6、PySide2/6 主机制是 destroyed 信号（见 _watch） 这里只是同步兜底"""
        if w is None:
            return False
        if id(w) in self._dead:
            return False
        try:
            w.isVisible()            # 只读、无副作用，但必然访问 C++ 对象
        except (RuntimeError, TypeError):
            self._dead.add(id(w))    # 缓存结论，后续不再重复探测
            return False
        return True

    # ---------------- 生命周期看守 ----------------
    def _watch(self, w):
        """页面被销毁的瞬间立刻收到通知，比下一帧探测更早"""
        if w is None or not self._alive(w):
            return
        key = id(w)
        if key in self._hooks:
            return
        hook = partial(self._on_page_destroyed, w)
        try:
            w.destroyed.connect(hook)     # _obj 参数由 _on_page_destroyed 兜底
        except (RuntimeError, TypeError):
            return
        self._hooks[key] = hook

    def _unwatch(self, w):
        if w is None:
            return
        key = id(w)
        hook = self._hooks.pop(key, None)
        if hook is not None and self._alive(w):
            try:
                w.destroyed.disconnect(hook)
            except (RuntimeError, TypeError):
                pass
        self._dead.discard(key)
        self._hooks.pop(key, None)

    def _on_page_destroyed(self, w, _obj=None):
        """注意：_obj 可能已是失效包装，绝不能访问；只用 Python 侧的 w 引用"""
        key = id(w)
        self._dead.add(key)
        self._hooks.pop(key, None)
        try:
            if w in self._pages:          # QObject 无 __eq__，走 identity，不碰 C++
                self._pages.remove(w)
        except ValueError:
            pass
        if self._animating and (w is self._cur or w is self._nxt):
            self._abort()                 # 只清状态，不碰任何 widget

    # ================= Public API =================
    def duration(self):
        return self._duration

    def setDuration(self, ms: int):
        self._duration = int(ms)
        self._anim.setDuration(self._duration)

    def addWidget(self, w: QWidget):
        if not self._alive(w):
            return
        try:
            w.setParent(self)
            w.setGeometry(0, 0, self.width(), self.height())
            w.hide()
        except RuntimeError:
            return
        self._pages.append(w)
        self._watch(w)
        if self._currentIndex == -1:
            self._currentIndex = 0
            try:
                w.setGeometry(0, 0, self.width(), self.height())
                w.show()
            except RuntimeError:
                pass

    def removeWidget(self, w: QWidget):
        """移除前先落定动画，避免留下悬空引用"""
        if self._animating and (w is self._cur or w is self._nxt):
            self._settle(emit=False)
        if w not in self._pages:
            return
        idx = self._pages.index(w)
        self._pages.remove(w)
        self._unwatch(w)
        try:
            w.setParent(None)
            w.hide()
        except RuntimeError:
            pass
        if idx < self._currentIndex:
            self._currentIndex -= 1
        self._currentIndex = max(-1, min(self._currentIndex, len(self._pages) - 1))
        if self._cur is w:
            self._cur = None
        if self._nxt is w:
            self._nxt = None

    def count(self):        return len(self._pages)
    def currentIndex(self): return self._currentIndex

    def currentWidget(self):
        if 0 <= self._currentIndex < len(self._pages):
            return self._pages[self._currentIndex]
        return None

    def setCurrentWidget(self, widget: QWidget):
        try:
            self.setCurrentIndex(self._pages.index(widget))
        except ValueError:
            return

    def setCurrentIndex(self, index, direction="auto"):
        if index < 0 or index >= len(self._pages):
            return
        if self._animating and index == self._targetIndex:
            return
        if self._animating:
            self._settle(emit=True)
        if index == self._currentIndex:
            return

        cur = self.currentWidget()
        nxt = self._pages[index]
        if not self._alive(cur) or not self._alive(nxt):
            return

        h, w = self.height(), self.width()
        if direction == "auto":
            direction = "down" if index > self._currentIndex else "up"

        if direction == "up":
            self._cy0, self._cy1 = 0, h
            self._ny0, self._ny1 = -h, 0
        else:
            self._cy0, self._cy1 = 0, -h
            self._ny0, self._ny1 = h, 0

        try:
            nxt.setParent(self)
            nxt.setGeometry(0, self._ny0, w, h)
            nxt.show()
            nxt.raise_()
            cur.setGeometry(0, 0, w, h)
            cur.show()
        except RuntimeError:
            return

        self._cur, self._nxt = cur, nxt
        self._targetIndex = index
        self._watch(cur)
        self._watch(nxt)

        self._animating = True
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        self.aniStart.emit()

    def stopAnimation(self):
        """外部要在动画期间删页 / 切布局 / 关窗口时，先调它"""
        if self._animating:
            self._settle(emit=False)

    # ================= Animation =================
    def _place(self, w, y, ww, hh) -> bool:
        if not self._alive(w):
            return False
        try:
            w.setGeometry(0, y, ww, hh)
            return True
        except RuntimeError:
            return False

    def _on_value(self, t):
        if not self._animating:
            return
        try:
            e = self._ease(float(t))
            h, w = self.height(), self.width()
            cy = int(self._cy0 + (self._cy1 - self._cy0) * e)
            ny = int(self._ny0 + (self._ny1 - self._ny0) * e)
            if not (self._place(self._cur, cy, w, h) and
                    self._place(self._nxt, ny, w, h)):
                self._abort()
        except RuntimeError:
            self._abort()

    def _on_finished(self):
        if self._animating:
            self._settle(emit=True)

    def _abort(self):
        """页面已失效：只清状态，不碰 widget、不发信号"""
        self._animating = False
        try:
            self._anim.stop()
        except RuntimeError:
            pass
        self._cur = self._nxt = None
        self._targetIndex = -1

    def _settle(self, emit=True):
        """把动画落定到终态"""
        if not self._animating:
            return
        self._animating = False
        self._anim.stop()

        cur, nxt, target = self._cur, self._nxt, self._targetIndex
        h, w = self.height(), self.width()

        if self._alive(nxt):
            try:
                nxt.setGeometry(0, 0, w, h)
                nxt.show()          # 修复"动画期间被 hide → 结束变空白"
                nxt.raise_()
            except RuntimeError:
                pass
            self._currentIndex = target
        if self._alive(cur) and cur is not nxt:
            try:
                cur.hide()
            except RuntimeError:
                pass

        self._unwatch(cur)
        self._unwatch(nxt)
        self._cur = self._nxt = None
        self._targetIndex = -1
        if emit:
            self.aniFinished.emit()

    def _ease(self, t: float) -> float:
        p1x, p1y = 0.2, 0.0
        p2x, p2y = 0.0, 1.0
        cx = 3 * p1x
        bx = 3 * (p2x - p1x) - cx
        ax = 1 - cx - bx
        cy = 3 * p1y
        by = 3 * (p2y - p1y) - cy
        ay = 1 - cy - by
        x = t
        for _ in range(8):
            v = ((ax * x + bx) * x + cx) * x - t
            d = (3 * ax * x + 2 * bx) * x + cx
            if abs(d) < 1e-6:
                break
            x -= v / d
        x = max(0.0, min(1.0, x))
        return ((ay * x + by) * x + cy) * x

    # ================= Events =================
    def hideEvent(self, e):
        super().hideEvent(e)
        if self._animating:
            self._settle(emit=True)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        w, h = self.width(), self.height()
        if self._animating:
            for pg in (self._cur, self._nxt):
                if self._alive(pg):
                    try:
                        pg.setGeometry(pg.x(), pg.y(), w, h)
                    except RuntimeError:
                        pass
        elif self._alive(self.currentWidget()):
            self.currentWidget().setGeometry(0, 0, w, h)

# 左右翻页堆叠部件
class PageLeftRightStackedWidget(QWidget):
    """左右滑入滑出翻页部件（双页同显）"""

    aniFinished = Signal()
    aniStart = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._duration = 420
        self._animating = False

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self._duration)
        self._anim.setEasingCurve(QEasingCurve.Linear)   # 缓动自己在 _ease 里做
        self._anim.valueChanged.connect(self._on_value)
        self._anim.finished.connect(self._on_finished)

        self._pages = []
        self._currentIndex = -1
        self._cur = self._nxt = None
        self._targetIndex = -1
        self._cx0 = self._cx1 = 0
        self._nx0 = self._nx1 = 0

        self._dead = set()      # 已销毁页面的 id()
        self._hooks = {}        # id(w) -> destroyed 槽

    # ================= 通用存活判断（零绑定判断） =================
    def _alive(self, w) -> bool:
        """跨 PyQt5/6、PySide2/6 主机制是 destroyed 信号（见 _watch） 这里只是同步兜底"""
        if w is None:
            return False
        if id(w) in self._dead:
            return False
        try:
            w.isVisible()            # 只读、无副作用，但必然访问 C++ 对象
        except (RuntimeError, TypeError):
            self._dead.add(id(w))    # 缓存结论，后续不再重复探测
            return False
        return True

    # ---------------- 生命周期看守 ----------------
    def _watch(self, w):
        """页面被销毁的瞬间立刻收到通知，比下一帧探测更早"""
        if w is None or not self._alive(w):
            return
        key = id(w)
        if key in self._hooks:
            return
        hook = partial(self._on_page_destroyed, w)
        try:
            w.destroyed.connect(hook)
        except (RuntimeError, TypeError):
            return
        self._hooks[key] = hook

    def _unwatch(self, w):
        if w is None:
            return
        key = id(w)
        hook = self._hooks.pop(key, None)
        if hook is not None and self._alive(w):
            try:
                w.destroyed.disconnect(hook)
            except (RuntimeError, TypeError):
                pass
        self._dead.discard(key)
        self._hooks.pop(key, None)

    def _on_page_destroyed(self, w, _obj=None):
        """_obj 可能已是失效包装，绝不能访问；只用 Python 侧的 w 引用"""
        key = id(w)
        self._dead.add(key)
        self._hooks.pop(key, None)
        try:
            if w in self._pages:          # QObject 无 __eq__，走 identity，不碰 C++
                self._pages.remove(w)
        except ValueError:
            pass
        if self._animating and (w is self._cur or w is self._nxt):
            self._abort()                 # 只清状态，不碰任何 widget

    # ================= Public API =================
    def duration(self):
        return self._duration

    def setDuration(self, d):
        self._duration = int(d)
        self._anim.setDuration(self._duration)

    def addWidget(self, w: QWidget):
        if not self._alive(w):
            return
        try:
            w.setParent(self)
            w.setGeometry(0, 0, self.width(), self.height())   # 原代码只 move 不 resize
            w.hide()
        except RuntimeError:
            return
        self._pages.append(w)
        self._watch(w)
        if self._currentIndex == -1:
            self._currentIndex = 0
            try:
                w.setGeometry(0, 0, self.width(), self.height())
                w.show()
            except RuntimeError:
                pass

    def removeWidget(self, w: QWidget):
        """移除前先落定动画，避免留下悬空引用"""
        if self._animating and (w is self._cur or w is self._nxt):
            self._settle(emit=False)
        if w not in self._pages:
            return
        idx = self._pages.index(w)
        self._pages.remove(w)
        self._unwatch(w)
        try:
            w.setParent(None)
            w.hide()
        except RuntimeError:
            pass
        if idx < self._currentIndex:
            self._currentIndex -= 1
        self._currentIndex = max(-1, min(self._currentIndex, len(self._pages) - 1))
        if self._cur is w:
            self._cur = None
        if self._nxt is w:
            self._nxt = None

    def count(self):        return len(self._pages)
    def currentIndex(self): return self._currentIndex

    def currentWidget(self):
        if 0 <= self._currentIndex < len(self._pages):
            return self._pages[self._currentIndex]
        return None

    def setCurrentWidget(self, widget: QWidget):
        try:
            self.setCurrentIndex(self._pages.index(widget))
        except ValueError:
            return

    def setCurrentIndex(self, index, direction="auto"):
        if index < 0 or index >= len(self._pages):
            return
        if self._animating and index == self._targetIndex:
            return
        if self._animating:
            self._settle(emit=True)
        if index == self._currentIndex:
            return

        cur = self.currentWidget()
        nxt = self._pages[index]
        if not self._alive(cur) or not self._alive(nxt):
            return

        w, h = self.width(), self.height()
        if direction == "auto":
            direction = "left" if index > self._currentIndex else "right"

        if direction == "left":
            # 当前页向左滑出，新页从右侧滑入
            self._cx0, self._cx1 = 0, -w
            self._nx0, self._nx1 = w, 0
        else:
            # 当前页向右滑出，新页从左侧滑入
            self._cx0, self._cx1 = 0, w
            self._nx0, self._nx1 = -w, 0

        try:
            nxt.setParent(self)
            nxt.setGeometry(self._nx0, 0, w, h)
            nxt.show()
            nxt.raise_()
            cur.setGeometry(0, 0, w, h)
            cur.show()
        except RuntimeError:
            return

        self._cur, self._nxt = cur, nxt
        self._targetIndex = index
        self._watch(cur)
        self._watch(nxt)

        self._animating = True
        self._anim.stop()
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        self.aniStart.emit()

    def stopAnimation(self):
        """外部要在动画期间删页 / 切布局 / 关窗口时，先调它"""
        if self._animating:
            self._settle(emit=False)

    # ================= Animation =================
    def _place(self, w, x, ww, hh) -> bool:
        if not self._alive(w):
            return False
        try:
            w.setGeometry(x, 0, ww, hh)
            return True
        except RuntimeError:
            return False

    def _on_value(self, t):
        if not self._animating:
            return
        try:
            e = self._ease(float(t))
            w, h = self.width(), self.height()
            cx = int(self._cx0 + (self._cx1 - self._cx0) * e)
            nx = int(self._nx0 + (self._nx1 - self._nx0) * e)
            if not (self._place(self._cur, cx, w, h) and
                    self._place(self._nxt, nx, w, h)):
                self._abort()
        except RuntimeError:
            self._abort()

    def _on_finished(self):
        if self._animating:
            self._settle(emit=True)

    def _abort(self):
        """页面已失效：只清状态，不碰 widget、不发信号"""
        self._animating = False
        try:
            self._anim.stop()
        except RuntimeError:
            pass
        self._cur = self._nxt = None
        self._targetIndex = -1

    def _settle(self, emit=True):
        """把动画落定到终态"""
        if not self._animating:
            return
        self._animating = False
        self._anim.stop()

        cur, nxt, target = self._cur, self._nxt, self._targetIndex
        w, h = self.width(), self.height()

        if self._alive(nxt):
            try:
                nxt.setGeometry(0, 0, w, h)
                nxt.show()          # 修复"动画期间被 hide → 结束变空白"
                nxt.raise_()
            except RuntimeError:
                pass
            self._currentIndex = target
        if self._alive(cur) and cur is not nxt:
            try:
                cur.hide()
            except RuntimeError:
                pass

        self._unwatch(cur)
        self._unwatch(nxt)
        self._cur = self._nxt = None
        self._targetIndex = -1
        if emit:
            self.aniFinished.emit()

    @staticmethod
    def _ease(t: float) -> float:
        """Win11-ish cubic bezier feel"""
        p1x, p1y = 0.2, 0.0
        p2x, p2y = 0.0, 1.0

        cx = 3 * p1x
        bx = 3 * (p2x - p1x) - cx
        ax = 1 - cx - bx

        cy = 3 * p1y
        by = 3 * (p2y - p1y) - cy
        ay = 1 - cy - by

        x = t
        for _ in range(8):
            v = ((ax * x + bx) * x + cx) * x - t
            d = (3 * ax * x + 2 * bx) * x + cx
            if abs(d) < 1e-6:
                break
            x -= v / d

        x = max(0.0, min(1.0, x))
        return ((ay * x + by) * x + cy) * x

    # ================= Events =================
    def hideEvent(self, e):
        super().hideEvent(e)
        if self._animating:
            self._settle(emit=True)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        w, h = self.width(), self.height()
        if self._animating:
            for pg in (self._cur, self._nxt):
                if self._alive(pg):
                    try:
                        pg.setGeometry(pg.x(), 0, w, h)
                    except RuntimeError:
                        pass
        elif self._alive(self.currentWidget()):
            self.currentWidget().setGeometry(0, 0, w, h)

# 上下单页堆叠部件
class SinglePageUpDownStackedWidget(QStackedWidget):
    """
    Win11 Settings 风格 · 上下滑入（单页动画，无双页同显）
    """

    aniFinished = Signal()
    aniStart = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.isAnimationEnabled = True
        self._duration = 360

        self._timer = QTimer(self)
        self._timer.setInterval(8)
        self._timer.timeout.connect(self._on_frame)

        self._animating = False
        self._elapsed = 0

        self._targetIndex = -1
        self._animWidget = None
        self._startPos = QPoint()
        self._endPos = QPoint()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def setAnimationEnabled(self, enabled: bool):
        self.isAnimationEnabled = enabled

    def setDefaultDuration(self, ms: int):
        self._duration = ms

    def setCurrentIndex(self, index: int, direction="auto"):
        if index < 0 or index >= self.count():
            return
        if index == self.currentIndex():
            return
        if not self.isAnimationEnabled:
            return super().setCurrentIndex(index)

        curIdx = self.currentIndex()

        if direction == "auto":
            direction = "down" if index > curIdx else "up"

        self._targetIndex = index
        widget = self.widget(index)

        h = self.height()
        margins = self.contentsMargins()
        origin = QPoint(margins.left(), margins.top())

        if direction == "up":
            self._startPos = QPoint(origin.x(), origin.y() + h)
        else:
            self._startPos = QPoint(origin.x(), origin.y() - h)

        self._endPos = origin

        # ✅ 关键：不立即 setCurrentIndex
        widget.setGeometry(self._startPos.x(), self._startPos.y(),
                           self.width(), h)
        widget.show()
        widget.raise_()

        self._animWidget = widget
        self._elapsed = 0
        self._animating = True
        self._timer.start()

        self.aniStart.emit()

    def setCurrentWidget(self, widget: QWidget):
        idx = self.indexOf(widget)
        if idx != -1:
            self.setCurrentIndex(idx)

    # ------------------------------------------------------------------
    # Easing
    # ------------------------------------------------------------------
    @staticmethod
    def _win11_ease(progress: float) -> float:
        p1x, p1y = 0.2, 0.0
        p2x, p2y = 0.0, 1.0

        cx = 3 * p1x
        bx = 3 * (p2x - p1x) - cx
        ax = 1 - cx - bx

        cy = 3 * p1y
        by = 3 * (p2y - p1y) - cy
        ay = 1 - cy - by

        t = progress
        for _ in range(8):
            v = ((ax * t + bx) * t + cx) * t - progress
            d = (3 * ax * t + 2 * bx) * t + cx
            if abs(d) < 1e-6:
                break
            t -= v / d

        t = max(0.0, min(1.0, t))
        return ((ay * t + by) * t + cy) * t

    # ------------------------------------------------------------------
    # Frame
    # ------------------------------------------------------------------
    def _on_frame(self):
        if not self._animating:
            self._timer.stop()
            return

        self._elapsed += self._timer.interval()
        t = min(1.0, self._elapsed / self._duration)
        e = self._win11_ease(t)

        if self._animWidget:
            y = int(self._startPos.y() +
                    (self._endPos.y() - self._startPos.y()) * e)
            self._animWidget.move(self._startPos.x(), y)

        if t >= 1.0:
            self._animating = False
            self._timer.stop()

            # ✅ 动画结束才真正切换
            super().setCurrentIndex(self._targetIndex)

            margins = self.contentsMargins()
            w = self.currentWidget()
            if w:
                w.move(margins.left(), margins.top())

            self.aniFinished.emit()

    # ------------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._animating:
            margins = self.contentsMargins()
            w = self.currentWidget()
            if w:
                w.move(margins.left(), margins.top())

# 左右单页堆叠部件
class SinglePageLeftRightStackedWidget(QStackedWidget):
    """
    Win11 Settings 风格 · 左右滑入（单页动画，无双页同显）
    """

    aniFinished = Signal()
    aniStart = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.isAnimationEnabled = True
        self._duration = 360

        self._timer = QTimer(self)
        self._timer.setInterval(8)
        self._timer.timeout.connect(self._on_frame)

        self._animating = False
        self._elapsed = 0

        self._targetIndex = -1
        self._animWidget = None
        self._startPos = QPoint()
        self._endPos = QPoint()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def setAnimationEnabled(self, enabled: bool):
        self.isAnimationEnabled = enabled

    def setDefaultDuration(self, ms: int):
        self._duration = ms

    def setCurrentIndex(self, index: int, direction="auto"):
        if index < 0 or index >= self.count():
            return
        if index == self.currentIndex():
            return
        if not self.isAnimationEnabled:
            return super().setCurrentIndex(index)

        curIdx = self.currentIndex()

        if direction == "auto":
            direction = "left" if index > curIdx else "right"

        self._targetIndex = index
        widget = self.widget(index)

        w = self.width()
        margins = self.contentsMargins()
        origin = QPoint(margins.left(), margins.top())

        if direction == "left":
            # 新页从右侧滑入
            self._startPos = QPoint(origin.x() + w, origin.y())
        else:
            # 新页从左侧滑入
            self._startPos = QPoint(origin.x() - w, origin.y())

        self._endPos = origin

        # ✅ 关键：不立即 setCurrentIndex
        widget.setGeometry(self._startPos.x(), self._startPos.y(),
                           self.width(), self.height())
        widget.show()
        widget.raise_()

        self._animWidget = widget
        self._elapsed = 0
        self._animating = True
        self._timer.start()

        self.aniStart.emit()

    def setCurrentWidget(self, widget: QWidget):
        idx = self.indexOf(widget)
        if idx != -1:
            self.setCurrentIndex(idx)

    # ------------------------------------------------------------------
    # Easing
    # ------------------------------------------------------------------
    @staticmethod
    def _win11_ease(progress: float) -> float:
        p1x, p1y = 0.2, 0.0
        p2x, p2y = 0.0, 1.0

        cx = 3 * p1x
        bx = 3 * (p2x - p1x) - cx
        ax = 1 - cx - bx

        cy = 3 * p1y
        by = 3 * (p2y - p1y) - cy
        ay = 1 - cy - by

        t = progress
        for _ in range(8):
            v = ((ax * t + bx) * t + cx) * t - progress
            d = (3 * ax * t + 2 * bx) * t + cx
            if abs(d) < 1e-6:
                break
            t -= v / d

        t = max(0.0, min(1.0, t))
        return ((ay * t + by) * t + cy) * t

    # ------------------------------------------------------------------
    # Frame
    # ------------------------------------------------------------------
    def _on_frame(self):
        if not self._animating:
            self._timer.stop()
            return

        self._elapsed += self._timer.interval()
        t = min(1.0, self._elapsed / self._duration)
        e = self._win11_ease(t)

        if self._animWidget:
            x = int(self._startPos.x() +
                    (self._endPos.x() - self._startPos.x()) * e)
            self._animWidget.move(x, self._startPos.y())

        if t >= 1.0:
            self._animating = False
            self._timer.stop()

            # ✅ 动画结束才真正切换
            super().setCurrentIndex(self._targetIndex)

            margins = self.contentsMargins()
            w = self.currentWidget()
            if w:
                w.move(margins.left(), margins.top())

            self.aniFinished.emit()

    # ------------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self._animating:
            margins = self.contentsMargins()
            w = self.currentWidget()
            if w:
                w.move(margins.left(), margins.top())