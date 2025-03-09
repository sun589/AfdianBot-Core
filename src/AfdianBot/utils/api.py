"""
存放各种api
"""
import json
import requests
from ..exceptions import *
from fake_useragent import FakeUserAgent
import logging
from . import bot_vars
import time
from hashlib import md5

logger = logging.getLogger("AfdianBot")

__all__ = ["login","logout","get_user_info","get_sponsors","get_api_token","get_sign"]

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
    logger.debug(f"登录爱发电，账号：{account[4:]+'****'}")
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
    logout_req = requests.get("https://afdian.com/api/passport/logout", headers=headers, cookies=cookies)
    logout_res = logout_req.json()
    if logout_res.get("ec") != 200:
        raise AfdianResponeException(logout_res.get("ec"), logout_res.get("em"))

def get_api_token(auth_token:str) -> str:
    """
    获取api_token
    :param auth_token: auth_token
    :return: api_token
    """
    headers = {
        "User-Agent": FakeUserAgent().random
    }
    cookies = {
        "auth_token":auth_token
    }
    get_api_token_req = requests.get("https://afdian.com/api/creator/list-open-tokens",headers=headers,cookies=cookies)
    get_api_token_res = get_api_token_req.json()
    if get_api_token_res.get("ec") != 200:
        raise AfdianResponeException(get_api_token_res.get("ec"),get_api_token_res.get("em"))
    return get_api_token_res['data']['token']

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

def query_sponsor(user_id:str,auth_token:str=None) -> dict:
    """
    获取用户对机器人赞助的信息(如金额，方案等)
    :param user_id: 查询的user_id
    :param auth_token: auth_token,默认使用机器人的auth_token
    :return: 赞助信息(见使用文档)
    """
    if not auth_token:
        auth_token = bot_vars.get("auth_token")
    headers = {
        "User-Agent":FakeUserAgent().random
    }
    cookies = {
        "auth_token":auth_token
    }
    query_res = requests.get(f"https://afdian.com/api/user/sponsor-info?user_id={user_id}",headers=headers,cookies=cookies).json()
    if query_res.get("ec") != 200:
        raise AfdianResponeException(query_res.get("ec"),query_res.get("em"))
    sponsors_info = query_res['data']['sponsor_info']['in_detail']
    plans = [{"plan_id":i['plan_id'],"time":i['expire_time']} for i in sponsors_info['list']]
    return {
        "all_sum_amount": float(sponsors_info['all_sum_amount']),
        "current_amount": float(sponsors_info['current_amount']),
        "plans":plans
    }

def get_sponsors(num:int=20,page:int=1,target:str=None,user_id:str=None,api_token:str=None):
    """
    获取指定数量赞助者
    :param num: 数量
    :param page: 页数
    :param target: 查询目标的user_id,可选
    :param user_id: user_id,默认使用机器人的user_id
    :param api_token: api_token.默认使用机器人的api_token
    :return: 赞助者列表
    """
    if not user_id:
        user_id = bot_vars.get("user_id")
    api_token = api_token if api_token else bot_vars.get("api_token")
    if not api_token:
        return []
    ts = int(time.time())
    # 我就没见过如此离谱的api传参方式(我在这里卡了20多分钟)... (艹皿艹 )
    params = {
        "page": page,
        "per_page": num,
    }
    if target: params['user_id'] = target
    data = {
        "ts": ts,
        "user_id": user_id,
    }
    sign = get_sign(user_id, api_token, params, ts)
    data['sign'] = sign
    data['params'] = json.dumps(params).replace(" ","")
    get_sponsors_res = requests.post(f"https://afdian.com/api/open/query-sponsor{f'?user_id={target}' if target else ''}", json=data).json()
    if get_sponsors_res.get("ec") != 200:
        raise AfdianResponeException(get_sponsors_res.get("ec"),get_sponsors_res.get("em"))
    try:
        sponsors = get_sponsors_res['data']['list']
    except KeyError:
        return []
    sponsors_info = []
    for sponsor in sponsors:
        sponsors_info.append({
            "user":sponsor['user'],
            "all_sum_amount":float(sponsor["all_sum_amount"]),
            "avatar":float(sponsor['user'].get('avatar')),
            "name":sponsor['user'].get('name')
        })
    return sponsors_info

def get_sign(user_id:str, api_token:str, params:dict, ts) -> str:
    """
    获取sign(用于爱发电官方公开的api中)
    :param user_id: user_id
    :param api_token: api_token
    :param params: 请求api的参数(dict)
    :param ts: 时间戳
    :return: sign
    """
    params = json.dumps(params).replace(" ","")
    return md5(f"{api_token}params{params}ts{ts}user_id{user_id}".encode("utf-8")).hexdigest()