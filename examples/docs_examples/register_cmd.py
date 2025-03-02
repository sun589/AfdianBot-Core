import AfdianBot

bot = AfdianBot.Bot(account="xxx",password="xxxx") # 实例化一个bot

@bot.register("/test1") # 注册一个基础指令(支持正则表达式，见下面)
def test1(msg:AfdianBot.types.TextMsg): # 注意，本库在调用时会传入TextMsg类型的消息对象(一些情况除外)!
    bot.send_msg("Hello1!",msg.sender_id) # 发送消息

@bot.register("/test2 [a-zA-Z0-9] ") # 支持正则表达式,在本例子中即本函数只在后面一项为纯字母+数字时才执行
def test2(msg:AfdianBot.types.TextMsg):
    bot.send_msg("Hello2!",msg.sender_id)

bot.run()