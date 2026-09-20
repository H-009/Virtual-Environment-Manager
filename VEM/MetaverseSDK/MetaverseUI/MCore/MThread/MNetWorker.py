import requests
from qtpy.QtCore import QThread, Signal
from bs4 import BeautifulSoup


# 获取Python全部版本
class GetPythonVersions(QThread):
    """
    获取python版本
    """
    finished = Signal(list)
    error = Signal(str)

    def __init__(self,parent=None):
        super().__init__(parent)

    def run(self):
        try:
            self.finished.emit(self.get_python_all_versions())
        except Exception as e:
            self.error.emit(f"获取版本超时")
            print(e)

    @staticmethod
    def get_python_all_versions():
        try:
            url = "https://www.python.org/ftp/python/"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html.parser')
            versions = [
                a['href'].strip('/')
                for a in soup.find_all('a')
                if a.has_attr('href')
                   and a['href'][0].isdigit()
                   and a['href'].endswith('/')
            ]
            # 只保留合法 x.y.z 版本号
            versions = [v for v in versions if v.count('.') >= 1 and all(p.isdigit() for p in v.split('.'))]
            versions.sort(key=lambda x: list(map(int, x.split('.'))), reverse=True)
            return versions

        except Exception as e:
            print(e)
            return []

# 获取Python版本全部文件
class GetPythonFile(QThread):
    """
    获取python文件
    """
    finished = Signal(list)
    error = Signal(str)

    def __init__(self,v,parent=None):
        super().__init__(parent)
        self.v = v

    def run(self):
        try:
            self.finished.emit(self.get_python_versions_all_file(self.v))
        except Exception as e:
            self.error.emit(f"获取文件超时")
            print(e)

    @staticmethod
    def get_python_versions_all_file(v):
        try:
            # 传入具体的Python版本号，比如v="3.14.2"，拼接访问该版本的专属下载目录
            url = f"https://www.python.org/ftp/python/{v}/"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html.parser')
            # 提取所有符合要求的文件，仅排除文件夹
            file_list = [
                a['href']
                for a in soup.find_all('a')
                # 跳过无效的空href属性
                if a.has_attr('href')
                   # 排除所有以/结尾的子文件夹 其余都是文件
                   and not a['href'].endswith('/')
                   # 额外过滤掉页面导航用的上级目录链接"../"，避免无关条目混入
                   and a['href'] != '../'
            ]

            return file_list

        except Exception as e:
            print(e)
            return []