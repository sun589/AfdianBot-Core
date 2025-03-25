# 这里拿base64做演示,实际场景中请更换加密算法,这里仅简单演示
import AfdianBot
import base64


def calc_code(code):
    return base64.b64encode(code.encode()).decode()


bot = AfdianBot.Bot(account="xxx", password="xxxx")  # 实例化一个bot


@bot.register("/calc (\S+)")
def test1(code):
    # 使用api.query_sponsor检查发送者是否到指定金额档位
    # 如果你想判断发送者是否赞助过某一个方案,可以在plans中检查
    """
    for i in AfdianBot.api.query_sponsor(msg.sender_id)['plans']:
        if i['plan_id'] == "xxx":
            bot.send_msg(f"你的激活码是:{calc_code(code)}",msg.sender_id)
            break
    else:
        bot.send_msg("你没有赞助xxx方案!",msg.sender_id)
    """
    msg = AfdianBot.ctx.get_current_msg()
    if AfdianBot.api.query_sponsor(msg.sender_id)['all_sum_amount'] >= 20:
        bot.send_msg(f"你的激活码是:{calc_code(code)}", msg.sender_id)
    else:
        bot.send_msg("你没有赞助够20元!", msg.sender_id)


bot.run()