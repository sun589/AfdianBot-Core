class AfdianException(Exception):
    """AfdianBot基本异常类型"""
    def __init__(self, ec, message):
        self.ec = ec
        self.message = message

    def __str__(self):
        return f'错误码：{self.ec}，错误信息：{self.message}'

class AfdianLoginFailed(AfdianException):
    """账号登录失败报错"""
    pass

class AfdianResponeException(AfdianException):
    """爱发电响应异常"""
    pass

class AfdianGetMsgFailed(AfdianResponeException):
    """获取消息失败"""
    pass