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

    def __init__(self,url,parent=None):
        super().__init__(parent)

        self.url = url

    def run(self):
        try:
            self.finished.emit(self.get_python_all_versions())
        except Exception as e:
            self.error.emit(f"获取版本超时")
            print(e)

    def get_python_all_versions(self):
        try:
            resp = requests.get(self.url, timeout=10)
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

    def __init__(self,url,parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            self.finished.emit(self.get_python_versions_all_file())
        except Exception as e:
            self.error.emit(f"获取文件超时")
            print(e)

    def get_python_versions_all_file(self):
        try:
            resp = requests.get(self.url, timeout=10)
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

# 获取Github发布
class GetGitHubReleaseThread(QThread):
    """请求一次 GitHub Release"""

    release_fetched = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self,url,parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            data = self.get_latest_release()
            if data is None:
                self.error_occurred.emit("未找到 Release")
            else:
                parsed = self.parse_github_release(data)
                self.release_fetched.emit(parsed)

        except requests.exceptions.HTTPError as e:
            resp = e.response
            if resp is not None and resp.status_code == 403:
                self.error_occurred.emit("GitHub API 速率限制已超出")
            else:
                self.error_occurred.emit(str(e))

        except Exception as e:
            self.error_occurred.emit(str(e))

    # ---------- GitHub 请求逻辑 ----------
    def get_latest_release(self):
        headers = {"Accept": "application/vnd.github+json"}
        r = requests.get(self.url, headers=headers, timeout=10,verify=False)

        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    @staticmethod
    def parse_github_release(raw_json):
        return {
            "version": raw_json["tag_name"],
            "release_note": raw_json["body"],
            "publish_time": raw_json["published_at"],
            "is_prerelease": raw_json["prerelease"],
            "detail_page_url": raw_json["html_url"],
            "download_assets": [
                {
                    "filename": asset["name"],
                    "download_url": asset["browser_download_url"],
                    "size": asset["size"],
                    "sha256": (
                        asset["digest"].split(":")[-1]
                        if asset.get("digest") and ":" in asset["digest"]
                        else None
                    ),
                }
                for asset in raw_json["assets"]
            ],
        }