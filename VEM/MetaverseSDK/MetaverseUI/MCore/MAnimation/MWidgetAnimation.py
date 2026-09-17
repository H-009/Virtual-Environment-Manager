from qtpy.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
from qtpy.QtWidgets import QLabel, QGraphicsOpacityEffect
from qfluentwidgets import isDarkTheme


# 任务球动画
def MissionBallAnimation(main_window,src_btn,dst_btn,color_auto=False,size=15,on_finished_callback=None):
    """
    main_window       主窗口
    src_btn          起始按钮
    dst_btn          终点按钮
    color_auto       自动颜色 / 自定义颜色
    size             小球尺寸
    on_finished_callback: Callable[[], None] | None
                       动画结束后调用的外部函数
    """

    # ---------- 颜色 ----------
    if not color_auto:
        color = "#ff29f1ff" if isDarkTheme() else "#ff009faa"
    else:
        color = color_auto

    # ---------- 坐标 ----------
    src_global = src_btn.mapToGlobal(src_btn.rect().center())
    dst_global = dst_btn.mapToGlobal(dst_btn.rect().center())

    src_pos = main_window.mapFromGlobal(src_global)
    dst_pos = main_window.mapFromGlobal(dst_global)

    # ---------- 小球 ----------
    dot = QLabel(main_window)
    dot.setFixedSize(size, size)
    dot.setStyleSheet(f"""
        background:{color};
        border-radius:{size // 2}px;
    """)
    dot.setAttribute(Qt.WA_TransparentForMouseEvents)
    dot.move(src_pos - dot.rect().center())
    dot.show()

    # ---------- 贝塞尔控制点 ----------
    dx = dst_pos.x() - src_pos.x()
    dy = dst_pos.y() - src_pos.y()

    cp1 = QPoint(
        int(src_pos.x() + dx * 0.35),
        int(src_pos.y() - abs(dy) * 0.55)
    )
    cp2 = QPoint(
        int(src_pos.x() + dx * 0.65),
        int(dst_pos.y() - abs(dy) * 0.35)
    )

    # ---------- 动画 ----------
    anim = QPropertyAnimation(dot, b"pos")
    anim.setDuration(800)
    anim.setEasingCurve(QEasingCurve.OutCubic)

    steps = 24
    for i in range(1, steps):
        t = i / steps
        mt = 1 - t
        x = (
            mt**3 * src_pos.x() +
            3 * mt**2 * t * cp1.x() +
            3 * mt * t**2 * cp2.x() +
            t**3 * dst_pos.x()
        )
        y = (
            mt**3 * src_pos.y() +
            3 * mt**2 * t * cp1.y() +
            3 * mt * t**2 * cp2.y() +
            t**3 * dst_pos.y()
        )
        anim.setKeyValueAt(t, QPoint(int(x), int(y)))

    anim.setEndValue(dst_pos - dot.rect().center())

    dot._anim = anim
    if not hasattr(main_window, "_fly_dots"):
        main_window._fly_dots = []
    main_window._fly_dots.append(dot)

    # ===============================
    # 动画结束处理
    # ===============================
    def on_finished():
        # ---- 淡出 ----
        opacity = QGraphicsOpacityEffect(dot)
        dot.setGraphicsEffect(opacity)

        fade = QPropertyAnimation(opacity, b"opacity")
        fade.setDuration(200)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.setEasingCurve(QEasingCurve.InCubic)

        dot._fade = fade

        def on_fade_finished():
            dot.deleteLater()
            if dot in main_window._fly_dots:
                main_window._fly_dots.remove(dot)

            # 外部回调（核心）
            if callable(on_finished_callback):
                on_finished_callback()

        fade.finished.connect(on_fade_finished)
        fade.start()

    anim.finished.connect(on_finished)
    anim.start()