"""
本文件用于共享变量
"""
def get(name):
    return vars[name]

def set(name,value):
    global vars
    vars[name] = value

vars = {
    "auth_token":None,
    "api_token":None,
    "user_id":None
}