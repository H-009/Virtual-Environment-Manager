
# Url构建器
class UrlBuilder:
    # 获取Python全部版本
    @staticmethod
    def PythonAllVersions():
        return "https://www.python.org/ftp/python/"

    # 获取Python版本全部文件
    @staticmethod
    def PythonVersionsAllFile(v):
        return f"https://www.python.org/ftp/python/{v}/"

    # 获取Github仓库
    @staticmethod
    def GithubRepo(owner, repo):
        return f"https://github.com/{owner}/{repo}/"

    # 获取Github仓库最新版本
    @staticmethod
    def GithubRepoLatestRelease(owner, repo):
        return f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

    # 获取Github仓库问题
    @staticmethod
    def GithubRepoIssues(owner, repo):
        return f"https://github.com/{owner}/{repo}/issues"

    # 获取Github仓库发布
    @staticmethod
    def GithubRepoReleases(owner, repo):
        return f"https://github.com/{owner}/{repo}/releases/latest"