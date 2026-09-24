
import requests
from MetaverseSDK.MetaverseAPI import Key

ip = "linyi"
key = Key.APIKey.QWeather_api_key
host = Key.APIKey.QWeather_api_host


resp = requests.get(f"https://{host}//geo/v2/city/lookup?key={key}&location=兰山区&adm=临沂市")
a = resp.json()
print(a)

print("未来3天")
num = 3
resp = requests.get(f"https://{host}/v7/weather/30d?key={key}&location=101120911")
a = resp.json()["daily"]
print(a)
# for i in range(num):
#     print("白天天气现象",b["text_day"])