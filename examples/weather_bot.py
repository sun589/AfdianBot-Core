import AfdianBot
import requests
bot = AfdianBot.Bot(account="xxxxx", password="xxxx") # 填写账号密码
@bot.register("/天气 (.*) (.*) (.*)")
def weather(province,city,county):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    r1 = requests.get(f"https://wis.qq.com/weather/common?source=pc&weather_type=observe&province={province}&city={city}&county={county}",headers=headers).json()['data']['observe']
    bot.send_msg(f"""查询地区：{province}{city}{county}
温度:{r1.get('degree')}
湿度:{r1.get('humidity')}
天气:{r1.get('weather')}
更新时间:{r1.get('update_time')}
风向:{r1.get('wind_direction_name')}
风级:{r1.get('wind_power')}""")
bot.run()