"""
存放一些自定义的类型
"""

class Msg:
    """
    基础消息类型
    msg_type: 消息类型,只有send/receive
    msg_id: 消息id
    id: 消息id
    sender_id: 发送者id
    send_time: 发送时间
    """
    def __init__(self, data: dict):
        self.msg_type = data["message"].get("type")
        self.msg_id = data["message"].get("msg_id")
        self.id = data["message"].get("id")
        self.sender_id = data["message"].get("sender")
        self.send_time = data["message"].get("send_time")

class TextMsg(Msg):
    """
    文本消息,继承自Msg
    msg_type: 消息类型,只有send/receive
    msg_id: 消息id
    id: 消息id
    sender_id: 发送者id
    send_time: 发送时间
    content: 消息内容
    """
    def __init__(self, data: dict):
        super().__init__(data)
        self.content = data["message"].get("content")

    def __str__(self):
        return self.content

class SponsorMsg(Msg):
    """
    赞助消息
    msg_type: 消息类型,只有send/receive
    msg_id: 消息id
    id: 消息id
    sender_id: 发送者id
    send_time: 发送时间
    amount: 赞助金额
    remark: 备注
    plan_id: 计划id
    isredeem: 是否由兑换码/赠送领取
    """
    def __init__(self, data: dict):
        super().__init__(data)
        content = data["message"]['content']
        self.amount = content.get("total_amount")
        self.remark = content.get("remark")
        self.plan_id = content['plan'].get("plan_id")
        self.isredeem = bool(content['ext'].get("redeem"))