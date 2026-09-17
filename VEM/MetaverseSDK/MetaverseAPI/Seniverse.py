
import requests
from MetaverseSDK.MetaverseAPI import Key

ip = "linyi"
key = Key.APIKey.Seniverse_private

print("实况天气")
resp = requests.get(f"https://api.seniverse.com/v3/weather/now.json?key={key}&location={ip}&language=zh-Hans&unit=c")
a = resp.json()["results"][0]['now']
print(a)
print("天气现象",a["text"])
print("现象代码",a["code"])
print("温度",a["temperature"])

print("未来3天")
num = 3
resp = requests.get(f"https://api.seniverse.com/v3/weather/daily.json?key={key}&location={ip}&language=zh-Hans&unit=c&start=0&days={num}")
a = resp.json()["results"][0]['daily']
print(a)
for i in range(num):
    b = a[i]
    print()
    print("日期",b["date"])
    print("白天天气现象",b["text_day"])
    print("白天现象代码",b["code_day"])
    print("晚间天气现象",b["text_night"])
    print("晚间现象代码",b["code_night"])
    print("当天最高温度",b["high"])
    print("当天最低温度",b["low"])
    print("降水量",b["rainfall"],"mm")
    print("降水概率",b["precip"],"%")
    print("风向",b["wind_direction"])
    print("风向角度",b["wind_direction_degree"])
    print("风速",b["wind_speed"],"km/h")
    print("风力等级",b["wind_scale"])
    print("相对湿度",b["humidity"],"%")

print("生活指数")
resp = requests.get(f"https://api.seniverse.com/v3/life/suggestion.json?key={key}&location=shanghai&language=zh-Hans&days={num}")
a = resp.json()["results"][0]['suggestion']
print(a)
for i in range(num):
    b = a[i]
    print()
    print("日期",b["date"])
    print("空调开启",b["ac"]["brief"],b["ac"]["details"])
    print("空气污染扩散条件",b["air_pollution"]["brief"],b["air_pollution"]["details"])
    print("晾晒",b["airing"]["brief"],b["airing"]["details"])
    print("过敏",b["allergy"]["brief"],b["allergy"]["details"])
    print("啤酒",b["beer"]["brief"],b["beer"]["details"])
    print("划船",b["boating"]["brief"],b["boating"]["details"])
    print("洗车",b["car_washing"]["brief"],b["car_washing"]["details"])
    print("舒适度",b["comfort"]["brief"],b["comfort"]["details"])
    print("穿衣",b["dressing"]["brief"],b["dressing"]["details"])
    print("钓鱼",b["fishing"]["brief"],b["fishing"]["details"])
    print("感冒",b["flu"]["brief"],b["flu"]["details"])
    print("放风筝",b["kiteflying"]["brief"],b["kiteflying"]["details"])
    print("化妆",b["makeup"]["brief"],b["makeup"]["details"])
    print("心情",b["mood"]["brief"],b["mood"]["details"])
    print("晨练",b["morning_sport"]["brief"],b["morning_sport"]["details"])
    print("路况",b["road_condition"]["brief"],b["road_condition"]["details"])
    print("购物",b["shopping"]["brief"],b["shopping"]["details"])
    print("运动",b["sport"]["brief"],b["sport"]["details"])
    print("防晒",b["sunscreen"]["brief"],b["sunscreen"]["details"])
    print("交通",b["traffic"]["brief"],b["traffic"]["details"])
    print("雨伞",b["umbrella"]["brief"],b["umbrella"]["details"])
    print("紫外线",b["uv"]["brief"],b["uv"]["details"])
