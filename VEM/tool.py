import ast
import inspect
import os
import subprocess
from types import MethodType
from typing import Optional, Union, List

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QTreeWidgetItem
from bs4 import BeautifulSoup
from qfluentwidgets import Theme
import re
import urllib.request
from urllib.parse import urlparse
from pathlib import Path
import shlex

def str_to_bool(str_bool):
    if str_bool == "True" or str_bool == "true":
        return True
    if str_bool == "False" or str_bool == "false":
        return False

def str_to_theme(mode_str: str, default: Theme = Theme.AUTO) -> Theme:
    """
    将字符串安全地转换为 qfluentwidgets 的 Theme 枚举。
    如果字符串不匹配，自动返回你指定的默认值（默认是 Theme.AUTO）。
    """
    # 核心逻辑：遍历 Theme 的所有成员，比对名字，找到了就返回对应的枚举
    return next((m for m in Theme if m.name == mode_str.upper()), default)

def replace_placeholders_regex(text, placeholder_values):
    """
    使用正则表达式一次性替换所有占位符
    """
    if not placeholder_values:
        return text

    # 构建正则模式：匹配 % 后跟一个或多个字母、数字或下划线
    # r'%([A-Za-z0-9_]+)' 是你提取时用的，这里替换时也要用类似的
    # 为了确保精确匹配，我们可以直接遍历字典构建一个大的正则，或者使用回调

    def replacement_callback(match):
        full_match = match.group(0)  # 例如 '%10'
        # 在字典中查找对应的值
        return placeholder_values.get(full_match, full_match)  # 如果没找到，保留原样

    # 使用 re.sub 全局替换
    # 模式解释: %(?=[A-Za-z0-9_]) 确保后面有合法字符，然后匹配整个占位符
    # 更简单的写法是直接匹配你定义的格式
    pattern = r'%[A-Za-z0-9_]+'

    return re.sub(pattern, replacement_callback, text)

def is_drive_root_fast(path: str) -> bool:
    """
    字符串盘符判断
    """
    if not path:
        return False

    p = Path(path).resolve(strict=False)

    # 必须是绝对路径
    if not p.is_absolute():
        return False

    # 必须是盘符根目录
    return p.parent == p and p.drive

def is_valid_get_pip_source(text: str) -> bool:
    """
    get-pip url判断是否合法
    """

    def extract_url_from_command(text: str) -> Optional[str]:
        """
        从 curl / wget / 纯 URL 中提取 URL
        """
        text = text.strip()

        # 1️⃣ 纯 URL 直接返回
        if text.startswith(("http://", "https://")):
            return text

        # 2️⃣ curl / wget 命令解析
        try:
            parts = shlex.split(text)
        except Exception:
            return None

        if not parts:
            return None

        cmd = parts[0]

        if cmd in ("curl", "wget"):
            # 找第一个 http(s) URL
            for p in parts:
                if p.startswith(("http://", "https://")):
                    return p

        return None

    if not text:
        return False

    # ✅ 先截断命令，只保留 URL
    url = extract_url_from_command(text)
    if not url:
        return False

    url = url.strip()

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.netloc:
        return False

    pattern = re.compile(
        r'^https?://bootstrap\.pypa\.io'
        r'(/pip/\d+(\.\d+){1,2})?/get-pip\.py$',
        re.IGNORECASE
    )
    if not pattern.match(url):
        return False

    try:
        req = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False

def is_valid_get_pip_source_re(text: str) -> bool:
    """
    判断是否为合法的 get-pip 来源 完全正则表达式匹配
    支持：
      - https://bootstrap.pypa.io/get-pip.py
      - https://bootstrap.pypa.io/pip/x.y.z/get-pip.py
      - curl / wget 命令形式
    """
    _GET_PIP_RE = re.compile(
        r'''
        ^(?:
            (?P<cmd>curl|wget)\s+
            (?P<flags>-\w+\s+)*
        )?
        https?://bootstrap\.pypa\.io
        (?:/pip/\d+(?:\.\d+){1,2})?
        /get-pip\.py
        (?:\s+-o\s+\S+)?
        $
        ''',
        re.IGNORECASE | re.VERBOSE
    )

    if not text:
        return False

    text = text.strip()

    # ✅ 纯 URL 或 curl/wget 命令
    return bool(_GET_PIP_RE.match(text))

def extract_curl_path(curl_command):
    """
    从 curl 命令中提取目标路径，支持引号和空格处理

    参数:
        curl_command: 完整的 curl 命令字符串

    返回:
        提取出的目标路径字符串
    """
    # 移除命令开头的 curl（如果存在）
    command = curl_command.strip()
    if command.startswith('curl '):
        command = command[5:].strip()

    # 使用 shlex 分割命令参数，正确处理引号
    try:
        args = shlex.split(command)
    except ValueError:
        # 如果 shlex 解析失败，使用简单空格分割
        args = command.split()

    # 查找 -o 或 --output 参数
    output_path = None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ['-o', '--output'] and i + 1 < len(args):
            output_path = args[i + 1]
            break
        i += 1

    # 如果没有找到 -o 参数，尝试从 URL 推断文件名
    if not output_path:
        for arg in args:
            if arg.startswith('http://') or arg.startswith('https://'):
                parsed_url = urlparse(arg)
                filename = os.path.basename(parsed_url.path)
                if filename:
                    output_path = filename
                break

    return output_path

def run_command(command, visible=False,mode="/c"):
    """
    执行命令
    :param command: 命令字符串
    :param visible: True=弹出新的cmd窗口并阻塞等待关闭, False=后台静默
    :param mode: 模式
    """

    if visible:
        try:
            # 用 ^" 转义内部引号，避免 cmd 解析混乱
            escaped = command.replace('"', '^"')
            subprocess.run(
                f'cmd {mode} "{escaped}"',
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            return 1
        except subprocess.TimeoutExpired:
            return "错误: 超时"
        except Exception as e:
            return f"异常: {str(e)}"
    else:
        # 后台静默执行：直接运行命令，不使用 cmd /k，因为不需要交互
        # 对于后台模式，直接传 command 列表或字符串即可，subprocess 会等待进程结束
        try:
            # 建议将 command 拆分为列表以提高安全性，或者保持 shell=True
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stderr and "error" in result.stderr.lower():
                return f"潜在错误: {result.stderr}"
            return result.stdout if result.returncode == 0 else f"错误: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "错误: 命令执行超时"
        except Exception as e:
            return f"异常: {str(e)}"

# 表格添加行 1列
def table_add_row_1(table,c1):
    row = table.rowCount()
    table.insertRow(row)
    table.setItem(row, 0,QTableWidgetItem(c1))

# 表格添加行 2列
def table_add_row_2(table,c1, c2,v1):
    row = table.rowCount()
    table.insertRow(row)
    item1 = QTableWidgetItem(c1)
    item1.setData(Qt.UserRole, v1)

    table.setItem(row, 0,item1)
    table.setItem(row, 1,QTableWidgetItem(c2))

# 表格添加行 4列
def table_add_row_4(table,c1, c2, c3, c4,v1):
    row = table.rowCount()
    table.insertRow(row)
    item1 = QTableWidgetItem(c1)
    item1.setData(Qt.UserRole, v1)

    table.setItem(row, 0,item1)
    table.setItem(row, 1,QTableWidgetItem(c2))
    table.setItem(row, 2,QTableWidgetItem(c3))
    table.setItem(row, 3,QTableWidgetItem(c4))

# 表格添加行 5列
def table_add_row_5(table,c1, c2, c3, c4, c5,v1):
    row = table.rowCount()
    table.insertRow(row)
    item1 = QTableWidgetItem(c1)
    item1.setData(Qt.UserRole, v1)
    table.setItem(row, 0, item1)
    table.setItem(row, 1, QTableWidgetItem(c2))
    table.setItem(row, 2, QTableWidgetItem(c3))
    table.setItem(row, 3, QTableWidgetItem(c4))
    table.setItem(row, 4, QTableWidgetItem(c5))

# 表格添加行 7列
def table_add_row_7(table,c1, c2, c3, c4, c5,c6,c7,v1):
    row = table.rowCount()
    table.insertRow(row)
    item1 = QTableWidgetItem(c1)
    item1.setData(Qt.UserRole, v1)
    table.setItem(row, 0, item1)
    table.setItem(row, 1, QTableWidgetItem(c2))
    table.setItem(row, 2, QTableWidgetItem(c3))
    table.setItem(row, 3, QTableWidgetItem(c4))
    table.setItem(row, 4, QTableWidgetItem(c5))
    table.setItem(row, 5, QTableWidgetItem(c6))
    table.setItem(row, 6, QTableWidgetItem(c7))

# 表格添加行 带图标
def table_add_row_ico(table, c1, c2, c3, icon=None):
    """
    icon: QIcon 对象，传 None 就不设行头图标
    """
    row = table.rowCount()
    table.insertRow(row)

    table.setItem(row, 0, QTableWidgetItem(c1))
    table.setItem(row, 1, QTableWidgetItem(c2))
    table.setItem(row, 2, QTableWidgetItem(c3))

    # 给新行的行头设 SVG 图标
    if icon is not None:
        item = QTableWidgetItem()
        item.setIcon(icon)
        item.setText(f" {row + 1}")   # 行号
        table.setVerticalHeaderItem(row, item)

def get_unique_name(path, name, is_file=True):
    """
    在指定路径下获取唯一的文件或文件夹名称

    :param path: str, 目标目录路径
    :param name: str, 基础名称（不含路径）
    :param is_file: bool, True为文件模式(保留扩展名), False为文件夹模式
    :return: str, 唯一的完整绝对路径
    """
    # 构建初始完整路径
    full_path = os.path.join(path, name)

    # 如果不存在，直接返回
    if not os.path.exists(full_path):
        return full_path

    # 如果存在，根据模式生成唯一名称
    base, ext = os.path.splitext(name)
    counter = 1
    max_retries = 100  # 设置上限 1000

    while counter <= max_retries:
        if is_file:
            # 文件模式: name(1).txt (序号插在名与扩展名之间)
            new_name = f"{base} ({counter}){ext}"
        else:
            # 文件夹模式: name(1) (序号直接追加)
            new_name = f"{name} ({counter})"

        new_full_path = os.path.join(path, new_name)

        if not os.path.exists(new_full_path):
            return new_full_path

        counter += 1

def is_valid_venv_create_command(command: str):
    """
    校验命令是否是创建 venv 虚拟环境的标准形式：
        <python_interpreter> -m venv <target_path>

    要求：
    - 必须以 Python 解释器路径开头
    - 必须包含 '-m venv'
    - '-m venv' 后面必须有目标路径

    Returns:
        (is_valid, message)
    """
    command = command.strip()
    if not command:
        return False

    # ── 1. 尝试用 shlex 拆分（正确处理引号）──
    try:
        parts = shlex.split(command)
    except ValueError:
        return False

    if len(parts) < 3:
        return False

    # ── 2. 验证第一个 token 是 Python 解释器 ──
    interpreter = parts[0]
    interp_name = Path(interpreter).name.lower()

    # 匹配 python.exe / python3.exe / python3.8.exe 等
    if not re.match(r'^python(\d+\.\d+)?\.exe$', interp_name):
        return False

    # ── 3. 找到 '-m venv' 的位置 ──
    try:
        m_idx = parts.index('-m')
    except ValueError:
        return False

    if m_idx + 1 >= len(parts) or parts[m_idx + 1] != 'venv':
        return False

    # ── 4. '-m venv' 后面必须有目标路径 ──
    venv_target_idx = m_idx + 2
    if venv_target_idx >= len(parts):
        return False

    target = parts[venv_target_idx]

    # 目标路径不能是另一个 flag（以 - 开头）
    if target.startswith('-'):
        return False

    # 基本路径合法性检查
    try:
        p = Path(target)
        if p.is_reserved():
            return False
    except Exception:
        return False

    return True

# 字符串列表转列表
def str_list_to_list(text):
    return ast.literal_eval(text)

# 字符串行转列表
def str_line_to_list(text):
    return text.splitlines()

def get_dict_from_textedits(textedit_l, textedit_r):
    """
    从两个 QTextEdit 中还原字典
    :param textedit_l: 左侧 QTextEdit (Keys)
    :param textedit_r: 右侧 QTextEdit (Values)
    :return: dict
    """
    # 1. 获取纯文本并按行分割
    # toPlainText() 返回所有文本，splitlines() 按行分割成列表
    keys = textedit_l.toPlainText().splitlines()
    values = textedit_r.toPlainText().splitlines()

    result_dict = {}

    # 2. 遍历并组合，处理行数不一致的情况
    # 使用 zip_longest 可以处理两边行数不一样的情况，这里简单用 min 长度
    min_len = min(len(keys), len(values))

    for i in range(min_len):
        key = keys[i].strip()
        value = values[i].strip()

        # 跳过空行或空键
        if not key:
            continue

        # 尝试将值转换为原始类型 (可选，如果原本存的是 int/bool)
        # 如果原本都是字符串，直接赋值即可
        result_dict[key] = value

    return result_dict

def run_command_temp_cmd(command: Union[str, List[str]],activate_path, visible=False, mode="/c"):
    """
    在单个 CMD 进程中串行执行所有命令（通过 stdin 发送，非 & 拼接）
    :param command: 单条命令字符串 / 多条命令组成的列表
    :param activate_path 激活参数
    :param visible: True=弹出新的cmd窗口, False=后台静默
    :param mode: cmd执行模式 (/c 执行后关闭, /k 执行后保持窗口打开)
    """
    # 1. 统一处理为列表
    if isinstance(command, str):
        command_list = [command]
    else:
        command_list = command

    if not command_list:
        return "无命令可执行"

    # 2. 构建要发送的命令字符串，每条命令后加换行符
    # 最后添加 'exit' 确保 CMD 进程在执行完所有命令后正常退出
    input_commands = "\n".join(command_list) + "\nexit\n"

    try:
        if visible:
            # 可视化模式：
            # 注意：subprocess 的 stdin 管道在可见窗口模式下较难直接交互
            # 如果必须可见且要在同一窗口，通常建议改用 /k 模式让用户看，
            # 或者使用 CreateProcess 等更底层的 API。
            # 这里为了简化，可见模式下仍建议使用 & 拼接或批处理文件。
            # 但如果坚持用 stdin 方式且可见，CMD 窗口会闪退或无法输入，体验较差。
            # 因此，可见模式下推荐回退到 & 拼接或生成临时 bat 文件。

            # 此处提供一个折中方案：生成临时 bat 文件并执行，这样既在一个进程里，又可见
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='gbk') as f:
                f.write("@echo off\n")
                f.write(f'call "{activate_path}"\n')
                for cmd in command_list:
                    f.write(f"{cmd}\n")
                # 如果是 /c 模式，执行完自动关闭；/k 则保留
                bat_path = f.name

            try:
                subprocess.run(
                    f'cmd {mode} "{bat_path}"',
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            finally:
                os.unlink(bat_path)  # 执行完后删除临时文件

        else:
            # 静默模式：通过 stdin 管道发送命令
            process = subprocess.Popen(
                ["cmd"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW  # 确保完全后台，不弹窗
            )
            # 发送命令并等待执行完毕
            process.communicate(input=input_commands.encode('gbk'))

        return 1

    except Exception as e:
        return f"执行异常: {str(e)}"

# 批量注册实例方法
def batch_registration_instance_method(mixin,self):
    for name, func in inspect.getmembers(mixin, inspect.isfunction):
        self.__dict__[name] = MethodType(func, self)

# 安全销毁树
def safe_delete_item_close(item: QTreeWidgetItem):
    """递归安全删除子节点"""
    for i in reversed(range(item.childCount())):
        child = item.takeChild(i)
        safe_delete_item_close(child)
    # 断开数据引用，帮助 GC
    item.setData(0, Qt.UserRole, None)
    del item

# 切换页面防抖
def switch_widget_debounce(stackedWidget,widget):
    if stackedWidget.currentWidget() is widget:
        return
    stackedWidget.setCurrentWidget(widget)