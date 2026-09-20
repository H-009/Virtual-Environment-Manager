import ctypes
import winreg


# 窗口等比例大小
def window_size(screen_size,proportion_x,proportion_y):
    width = int(screen_size.width() // proportion_x)
    height = int(screen_size.height() // proportion_y)
    # 中心坐标
    x = (screen_size.width() - width) // 2
    y = (screen_size.height() - height) // 2
    print(f"W{width} H{height} X{x} Y{y}")
    return x,y,width,height

# 屏幕中心
def screen_center(screen_size,w,h):
    # 中心坐标
    x = (screen_size.width() - w) // 2
    y = (screen_size.height() - h) // 2
    print(f"X{x} Y{y}")
    return x,y

# 系统缩放
def system_scaling():
    # Windows API方法
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        scale = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        scaling = round(scale * 4) / 4  # 标准化为1.0/1.25等
        print("系统缩放",scaling)
        return scaling
    except Exception as a:
        print("缩放获取异常",a)
        return 0

