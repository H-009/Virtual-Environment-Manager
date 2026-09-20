import random


# 变量类
class Variable:
    # 获取欢迎语
    @staticmethod
    def get_welcome(name, time):
        Welcome = [
            f"你好,{name}",
            f"欢迎,{name}",
            f"欢迎回来,{name}",
            "time_name",
            f"{name},你好",
            f"{name},欢迎",
            f"{name},欢迎回来",
            "name_time",
        ]
        text = Welcome[random.randint(0, len(Welcome) - 1)]
        if text == "time_name": # 正时间欢迎
            hour = int(time.split(':')[0])
            if 5 <= hour < 12:
                return f"早上好,{name}"
            elif 12 <= hour < 14:
                return f"中午好,{name}"
            elif 14 <= hour < 19:
                return f"下午好,{name}"
            else:  # 19-24 或 0-4
                return f"晚上好,{name}"
        if text == "name_time": # 反时间欢迎
            hour = int(time.split(':')[0])
            if 5 <= hour < 12:
                return f"{name},早上好"
            elif 12 <= hour < 14:
                return f"{name},中午好"
            elif 14 <= hour < 19:
                return f"{name},下午好"
            else:  # 19-24 或 0-4
                return f"{name},晚上好"
        else:  # 非时间欢迎
            return text

# 常量类
class Constant:
    a = 1
