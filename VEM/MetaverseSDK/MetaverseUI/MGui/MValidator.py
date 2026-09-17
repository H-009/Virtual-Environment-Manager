import re
from qtpy.QtGui import QValidator
from qfluentwidgets import TeachingTip, InfoBarIcon, TeachingTipTailPosition

# 验证器


# 升格验证器
class PromotionValidator(QValidator):
    def __init__(self, widget,obj):
        super().__init__(widget)
        self.widget = widget
        self.obj = obj

    def validate(self,text, pos):
        # 禁止大写字母
        if re.search(r"[A-Z]", text):
            self._show_tip("不允许输入大写字母")
            return QValidator.State.Invalid, text, pos

        # 禁止中文
        if re.search(r"[\u4e00-\u9fff]", text):
            self._show_tip("不允许输入中文")
            return QValidator.State.Invalid, text, pos

        # 禁止全角字符
        if re.search(r"[\uff00-\uffef]", text):
            self._show_tip("不允许输入全角字符")
            return QValidator.State.Invalid, text, pos

        # 禁止特殊符号 ! @ # ￥ % 等
        if re.search(r"[!@#￥%^&*()+~`]", text):
            self._show_tip("不允许输入特殊符号")
            return QValidator.State.Invalid, text, pos

        # 最终白名单校验（兜底）
        if not re.fullmatch(r"[a-z0-9 _.\[\]=,;'/\\%-]*", text):
            self._show_tip("包含非法字符")
            return QValidator.State.Invalid, text, pos

        return QValidator.State.Acceptable, text, pos

    def _show_tip(self, message):
        TeachingTip.create(
            target=self.widget,
            icon=InfoBarIcon.INFORMATION,
            title='提示',
            content=message,
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self.obj
        )

# 升格占位符验证器
class PromotionPlaceholderValidator(QValidator):
    def __init__(self, widget,obj):
        super().__init__(widget)
        self.widget = widget
        self.obj = obj

    def validate(self, text, pos):
        # 禁止大写字母
        if re.search(r"[A-Z]", text):
            self._show_tip("不允许输入大写字母")
            return QValidator.State.Invalid, text, pos

        # 禁止中文
        if re.search(r"[\u4e00-\u9fff]", text):
            self._show_tip("不允许输入中文")
            return QValidator.State.Invalid, text, pos

        # 禁止全角字符
        if re.search(r"[\uff00-\uffef]", text):
            self._show_tip("不允许输入全角字符")
            return QValidator.State.Invalid, text, pos

        # 禁止特殊符号 ! @ # ￥ % 等
        if re.search(r"[!@#￥^&*()+~`]", text):
            self._show_tip("不允许输入特殊符号")
            return QValidator.State.Invalid, text, pos

        # 最终白名单校验（兜底）
        if not re.fullmatch(r"[a-z0-9 _.\[\]=,;'/\\%-]*", text):
            self._show_tip("包含非法字符")
            return QValidator.State.Invalid, text, pos

        return QValidator.State.Acceptable, text, pos

    def _show_tip(self, message):
        TeachingTip.create(
            target=self.widget,
            icon=InfoBarIcon.INFORMATION,
            title='提示',
            content=message,
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self.obj
        )

# 操作符验证器
class OperatorValidator(QValidator):
    def __init__(self, widget,obj):
        super().__init__(widget)
        self.widget = widget
        self.obj = obj

    def validate(self, text, pos):
        # 禁止点（最高优先级）
        if "." in text:
            self._show_tip("不允许输入点（.）")
            return QValidator.State.Invalid, text, pos

        return QValidator.State.Acceptable, text, pos

    def _show_tip(self, message):
        TeachingTip.create(
            target=self.widget,
            icon=InfoBarIcon.INFORMATION,
            title='提示',
            content=message,
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=2000,
            parent=self.obj
        )