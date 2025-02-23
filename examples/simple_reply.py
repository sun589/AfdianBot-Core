import src.AfdianBot as AfdianBot

bot = AfdianBot.Bot(account="xxxxx", password="xxxx") # 填写账号密码

@bot.register("hello") # 注册一个指令
def hello(msg:AfdianBot.types.TextMsg):
    sender_name = AfdianBot.api.get_user_info(msg.sender_id)['name']
    bot.send_msg(f"hello {sender_name}!", msg.sender_id) # 回复消息至对方

# 在一般情况下，程序默认使用单线程模式，即一个一个处理回复
# 但在一些需要并发需求(即同时处理多个消息)情况时，你可以加上threded参数启用多线程模式
# bot.run(threded=True)
bot.run()