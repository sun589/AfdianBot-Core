# 注意:本例子中未预留参数的动作均为不传参的动作
import AfdianBot

bot = AfdianBot.Bot(account="xxx",password="xxxx") # 实例化一个bot

@bot.at("startup") # 在开机完毕时执行
def startup_func():
    print("AfdianBot准备就绪!")

@bot.at("shutdown") # 关机时执行
def shutdown_func():
    print("Bye bye!")

@bot.at("sponsorship") # 被赞助时执行
def sponsorship_func():
    msg = AfdianBot.ctx.get_current_msg()
    bot.send_msg(f"你赞助了{msg.amount}元!")

@bot.at("unknown_cmd") # 当发现没有匹配的指令的时候执行
def unknown_cmd_func():
    bot.send_msg("我不明白你在说什么!")

bot.run()