import AfdianBot

bot = AfdianBot.Bot(account="xxx",password="xxxx") # 实例化一个bot

@bot.register("/who_r_u")
def test1():
    bot_info = AfdianBot.api.get_user_info(bot.user_id)
    bot.send_msg(f"我的名字叫:{bot_info['name']}")
    bot.send_msg(f"我的user_id是:{bot.user_id}")
    bot.send_msg(f"我的头像url是:{bot_info['avatar']}")
    bot.send_msg(f"我的auth_token是:{bot.auth_token[:5]}****,我不会全部告诉你的!")
    bot.send_msg(f"我的api_token是:{bot.api_token[:5]}****,我不会全部告诉你的!")

bot.run()