"""
用于共享变量
"""
def get(name):
    return _vars[name]

def set_var(name, value):
    global _vars
    _vars[name] = value

_vars = {
    "auth_token":None,
    "api_token":None,
    "user_id":None
}