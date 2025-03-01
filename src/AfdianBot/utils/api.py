"""
存放各种api
"""
import requests
from ..exceptions import *
from fake_useragent import FakeUserAgent
import logging
logger = logging.getLogger("AfdianBot")

__all__ = ["login","logout","get_user_info"]

def login(account:str,password:str) -> str:
    """
    登录爱发电，获取auth_token
    :param account: 手机号/邮箱
    :param password: 密码
    :return: user_id,auth_token
    """
    headers = {
        "User-Agent": FakeUserAgent().random,
    }
    login_data = {
        "account":account,
        "password":password,
        "mp_token":-1
    }
    logger.debug(f"登录爱发电，账号：{account}，密码：{'****'+password[len(password)-3:len(password)]}")
    login_res = requests.post("https://afdian.com/api/passport/login", data=login_data, headers=headers) # 发送登录请求
    account_data = login_res.json()
    ec = account_data.get("ec")
    if ec != 200:
        raise AfdianLoginFailed(ec, account_data.get("em"))
    return account_data['data'].get("auth_token")

def logout(auth_token:str) -> None:
    """
    退出登录,销毁auth_token
    :param auth_token:
    :return:
    """
    headers = {
        "User-Agent": FakeUserAgent().random,
    }
    cookies = {
        "auth_token":auth_token
    }
    requests.get("https://afdian.com/api/passport/logout", headers=headers, cookies=cookies)

def get_user_info(user_id:str) -> dict:
    """
    获取用户信息
    :param user_id: user_id
    :return: 用户信息
    """
    headers = {
        "User-Agent": FakeUserAgent().random,
    }
    get_profile_res = requests.get(f"https://afdian.com/api/user/get-profile?user_id={user_id}",headers)
    if get_profile_res.json().get("ec") != 200:
        raise AfdianResponeException(get_profile_res.json().get("ec"), get_profile_res.json().get("em"))
    return {
        "name":get_profile_res.json().get("data").get("user").get("name"),
        "avatar":get_profile_res.json().get("data").get("user").get("avatar"),
    }