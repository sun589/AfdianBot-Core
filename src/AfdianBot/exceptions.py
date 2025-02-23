class AfdianLoginFailed(Exception):
    """账号登录失败报错"""

    def __init__(self, ec, message):
        self.ec = ec
        self.message = message

    def __str__(self):
        return f'错误码：{self.ec}，错误信息：{self.message}'

class AfdianResponeException(Exception):
    """爱发电响应异常"""

    def __init__(self, ec, message):
        self.ec = ec
        self.message = message

    def __str__(self):
        return f'错误码：{self.ec}，错误信息：{self.message}'