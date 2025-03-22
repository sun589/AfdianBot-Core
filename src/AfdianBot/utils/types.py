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
        self.sender_type: str = data.get("type")
        self.msg_type: str = data["message"].get("type")
        self.msg_id: int = data["message"].get("msg_id")
        self.id: int = data["message"].get("id")
        self.sender_id: str = data["message"].get("sender")
        self.send_time: int = data["message"].get("send_time")

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
        self.content: str = data["message"].get("content")

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
    real_amount: 实际金额(添加到账户的金额)
    remark: 备注
    plan_id: 计划id
    phone: 手机号
    address: 收货地址
    recipient: 收件人
    redeem_id: 兑换码id
    pay_type: 支付方式
    isredeem: 是否由兑换码/赠送领取
    isupgrade: 是否为升级套餐
    """
    def __init__(self, data: dict):
        super().__init__(data)
        content = data["message"]['content']
        self.amount: float = float(content.get("total_amount"))
        self.real_amount: float = float(content.get("show_amount"))
        self.remark: str = content.get("remark")
        self.plan_id: str = content['plan'].get("plan_id")
        self.phone: str = content['ext']['address'].get("phone")
        self.address: str = content['ext']['address'].get("address")
        self.recipient: str = content['ext']['address'].get("name")
        self.pay_type: int = content.get("pay_type")
        self.isupgrade: bool = bool(content.get("is_upgrade"))
        self.isredeem: bool = bool(content['ext'].get("redeem"))
        self.redeem_id: str = content['ext'].get("redeem")