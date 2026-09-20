
from enum import Enum

class APIKey(Enum):
    # 心知天气密钥对
    Seniverse_private = "SH1ORw8vdN4KiDYaa"  # 心知天气API私钥
    Seniverse_public = "PIHnLOiQS6exGIFdv" # 心知天气API公钥

    # 和风天气API凭据
    QWeather_api_key = "bcfb2aed7c2e473fa9b4be8b5821ec83" # 和风天气API Key
    QWeather_api_host = "jt3aaqa367.re.qweatherapi.com" # 和风天气API主机

    # 高德地图API Key
    AMap_key = "95661ed0ae3acb646242cb6d7f22ca92"

    # 直接获取枚举值
    def __str__(self):
        return self.value
