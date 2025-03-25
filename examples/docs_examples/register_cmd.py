import AfdianBot

bot = AfdianBot.Bot(account="xxx",password="xxxx") # 实例化一个bot

@bot.register("/test1") # 注册一个基础指令(支持正则表达式，见下面)
def test1(): # 注意，本库在调用时会传入TextMsg类型的消息对象(一些情况除外)!
    bot.send_msg("Hello1!") # 发送消息

@bot.register("/test2 [a-zA-Z0-9]") # 支持正则表达式,在本例子中即本函数只在后面一项为纯字母+数字时才执行
def test2():
    bot.send_msg("Hello2!")

@bot.register("/test3 (\S+) (\S+)") # 通过括号让其作为参数传入函数，默认将自动对过多/过少参数处理(取舍/填充)
def test3(a, b):
    bot.send_msg(f"你输入了{a}和{b}参数")

@bot.register("/test4 (\S+)",tupled_args=True) # 加上tupled_args为True可以让参数作为元组传入
def test4(args):
    bot.send_msg(f"你输入了{'和'.join(args)}参数")

"""
# 当你将bot的pass_msg设置为True时，应留出参数接收msg
@bot.register("/test5")
def test5(msg):
    bot.send_msg(f"发送者:{msg.sender_id}")

bot.run()
"""
