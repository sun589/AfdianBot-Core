# 获取api密钥(get_api_token)
## 使用实例
```python
import AfdianBot

bot = AfdianBot.Bot(account="xxx",password="xxxx") # 实例化一个bot

@bot.register("/test1")
def test1(msg:AfdianBot.types.TextMsg):
    print(AfdianBot.api.get_api_token()) # 运行机器人时可忽略auth_token,将自动填入bot的auth_token

print(AfdianBot.api.get_api_token(auth_token="xxxx")) # 单用时请传入auth_token
```

## api.get_api_token 函数解析

> [!attention]
> 如果返回结果为空，请检查机器人是否已申请api_token!  
> 如果没有api_token，请前往 https://afdian.com/dashboard/dev 申请!

> [!warning]
> 请不要将你的api_token泄露给他人，否则后果自行承担！

> 获取爱发电的api密钥

### 输入参数
| 字段名        | 类型     | 描述                               |
|------------|--------|----------------------------------|
| auth_token | string | 账号的auth_token,默认填入bot的auth_token |

### 返回数据
爱发电登录返回的auth_token