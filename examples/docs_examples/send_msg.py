import AfdianBot

bot = AfdianBot.Bot(account="xxx",password="xxxx") # 实例化一个bot

@bot.register("/test1")
def test1(msg:AfdianBot.types.TextMsg):
    bot.send_msg("Hello1!",msg.sender_id)

bot.run()