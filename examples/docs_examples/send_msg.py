import AfdianBot

bot = AfdianBot.Bot(account="xxx",password="xxxx") # 实例化一个bot

@bot.register("/test1")
def test1():
    bot.send_msg("Hello1!")

bot.run()