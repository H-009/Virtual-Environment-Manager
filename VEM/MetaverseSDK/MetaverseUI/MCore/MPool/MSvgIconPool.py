from qtpy.QtCore import QByteArray, QSize, Qt
from qtpy.QtGui import QPixmap, QIcon, QPainter
from qtpy.QtSvg import QSvgRenderer


# 矢量图标池
class SvgIconPool:
    def __init__(self, w=128, h=128):
        self.pool = {}
        self.default_render_size = QSize(w, h)

    def load(self, name: str, raw_svg_str: str):
        """加载Svg到池中 load(ico, svg)"""
        if not name or not raw_svg_str.strip():
            return

        if not raw_svg_str.strip().startswith("<svg"):
            return

        svg_byte = QByteArray(raw_svg_str.encode("utf-8"))
        renderer = QSvgRenderer(svg_byte)

        if not renderer.isValid():
            print(f"[SVG] 解析失败: {name}")
            return

        # 如果 SVG 自带 viewBox，优先使用
        view_box = renderer.viewBox()
        if view_box.isValid():
            size = view_box.size()
        else:
            size = self.default_render_size

        pix = QPixmap(size)
        pix.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pix)
        renderer.render(painter)
        painter.end()

        self.pool[name] = pix

    def get(self, name: str) -> QIcon:
        """获取 QIcon 对象"""
        pix = self.pool.get(name)
        if pix and not pix.isNull():
            return QIcon(pix)
        return QIcon()

    def older(self):
        """获取原始池 older()"""
        return self.pool

# 单例初始化
SIP = SvgIconPool()

