import os


def get_appdata_roaming_path(filename,app_name="STD Studio"):
    """
    获取 Windows AppData/Roaming 下的完整文件路径
    :param filename: 短文件名或相对子路径
    :param app_name: 应用名称
    :return: 完整的绝对路径字符串 若获取失败则返回空字符串
    """
    # 获取 Windows APPDATA 环境变量 (指向 Roaming)
    appdata = os.getenv('APPDATA')

    if not appdata:
        print("错误：无法获取 Windows APPDATA 环境变量")
        return ""

    full_path = os.path.join(appdata, app_name, filename)

    return full_path

def get_appdata_local_path(filename,app_name="STD Studio"):
    """
    获取 Windows AppData/Local 下的完整文件路径
    :param filename: 短文件名或相对子路径
    :param app_name: 应用名称
    :return: 完整的绝对路径字符串 若获取失败则返回空字符串
    """
    appdata = os.getenv('LOCALAPPDATA')

    if not appdata:
        print("错误：无法获取 Windows LOCALAPPDATA 环境变量")
        return ""

    full_path = os.path.join(appdata, app_name, filename)

    return full_path