import threading
from inspect import getfullargspec
from .exceptions import AfdianResponeException
from .utils import login,logout
from .utils import get_api_token
from .utils import types
from .utils import bot_vars
import logging
from fake_useragent import FakeUserAgent
import time
import requests
import re
import traceback

logger = logging.getLogger("AfdianBot")
__all__ = ["Bot"]

class Bot:

    def __init__(self, account, password):
        self.__account = account
        self.__password = password
        self.__mapping = {}
        self.__actions_mapping_funcs = {
            "startup": set(),
            "shutdown": set(),
            "sponsorship": set(),
            "unknown_cmd": set()
        }
        self.use_multithreading = False
        self.local_latest_msg_id = None
        self.running = False

    def _login(self):
        logger.info("获取auth_token")
        self.auth_token = login(self.__account, self.__password)
        logger.info(f"auth_token: {self.auth_token[:8] + '****'}")
        logger.debug("获取api_token")
        self.api_token = get_api_token(self.auth_token)
        if self.api_token:
            logger.debug(f"api_token: {self.api_token[:8] + '****'}")
        else:
            logger.debug("用户并未申请api_token!")
        logger.info("获取用户信息")
        profile_res = requests.get("https://afdian.com/api/my/profile", cookies={"auth_token": self.auth_token}, headers={"User-Agent": FakeUserAgent().random}).json()
        self.user_id = profile_res['data']['user'].get('user_id')
        username = profile_res['data']['user'].get('name')
        bot_vars.set("auth_token",self.auth_token)
        bot_vars.set("user_id",self.user_id)
        bot_vars.set("api_token",self.api_token)
        logger.info("user_id：" + self.user_id)
        logger.info(f"{username}登录成功!")

    def register(self, name, auto_truncate_fill=True):
        """
        注册一个指令
        """
        def wrapper(func):
            self.add_cmd(name, func, auto_truncate_fill)
            return func
        return wrapper

    def at(self, action):
        """
        设置函数在指定动作发生时执行,注意，当动作为sponsorship时，func的参数为SponsorMsg类型
        而在其他情况下，均不会传参
        :param action: startup/shutdown/sponsorship/unknown_cmd
        :return:
        """
        def wrapper(func):
            self.func_at(action, func)
        return wrapper

    def func_at(self, action, func):
        """
        同at装饰器的介绍，通过函数的形式添加一个动作
        :param action: startup/shutdown/sponsorship/unknown_cmd
        :param func:
        :return:
        """
        self.__actions_mapping_funcs[action].add(func)

    def add_cmd(self, cmd, func, auto_truncate_fill=True):
        """
        以函数的形式添加一个指令
        """
        self.__mapping[cmd] = (func,auto_truncate_fill)

    def _reply(self, session, dialog):
        """
        处理消息，执行函数
        :return:
        """
        user_id = dialog.get("user")['user_id']
        msg_res = session.get(f"https://afdian.com/api/message/messages?user_id={user_id}&type=new&message_id={self.local_latest_msg_id}")
        msg_list = msg_res.json().get("data")['list']
        msg_data = msg_res.json()
        if msg_data.get("ec") == 200:
            for i in msg_list:
                if i.get('type') == "send": # 禁止回复机器人自己的消息
                    continue
                logger.debug(f"收到消息：{i['message'].get('content')}")
                for j in self.__mapping.keys():
                    if i['message'].get('type') in [1,7]:
                        match = re.match(j,i['message'].get('content'))
                        if match:
                            args = match.groups()
                            needed_args = len(getfullargspec(self.__mapping[j][0]).args) - 1 # 减一留给msg
                            if self.__mapping[j][1]: # 判断是否需要处理多余/过少的参数
                                if len(args) < needed_args: # 对于参数不足的情况，填充None
                                    args = args + (None,) * (needed_args - len(args))
                                elif len(args) > needed_args:# 对于参数过多的情况，截断，避免参数过多的情况
                                    args = args[:needed_args]
                            msg = types.TextMsg(i)
                            if needed_args > 1: # 需要留一个给msg，因此不是大于零
                                self.__mapping[j][0](msg,*args)
                            else:
                                self.__mapping[j][0](msg)
                            break
                    elif i['message'].get('type') == 2:
                        msg = types.SponsorMsg(i)
                        for f in self.__actions_mapping_funcs['sponsorship']:
                            f(msg)
                        break
                else:
                    if i['message'].get('type') in [1,7]: # 仅文本消息才执行未知指令的函数，避免误判
                        for j in self.__actions_mapping_funcs['unknown_cmd']:
                            msg = types.TextMsg(i)
                            j(msg)

    def _all_reply(self, session:requests.session, dialogs:list):
        """
        回复所有消息
        :return:
        """
        tasks = []
        for dialog in dialogs:
            if self.use_multithreading:
                thread = threading.Thread(target=self._reply, args=(session, dialog))
                tasks.append(thread)
                thread.start()
            else:
                self._reply(session, dialog)
        if self.use_multithreading:
            for task in tasks:
                task.join()

    def send_msg(self, msg,user_id:str):
        """
        发送消息,只支持文本消息
        :param user_id: 用户id
        :param msg: 消息内容
        :return:
        """
        msg = str(msg)
        data = {
            "user_id":user_id,
            "type":"1",
            "content":msg
        }
        cookies = {"auth_token": self.auth_token}
        headers = {
            "User-Agent": FakeUserAgent().random
        }
        send_req = requests.post("https://afdian.com/api/message/send",headers=headers,data=data,cookies=cookies)
        send_res = send_req.json()
        if send_res.get("ec") != 200:
            raise AfdianResponeException(send_res.get("ec"), send_res.get("em"))

    def run(self, no_log=False, wait=10, debug=False, threaded=False):
        """
        运行机器人,默认使用单线程模式,可选择多线程模式
        :param no_log: 是否不输出日志
        :param wait: 拉取消息列表的间隔时间
        :param debug: 是否开启debug模式(将输出debug日志到控制台)
        :param threaded: 是否使用多线程模式
        :return:
        """
        if no_log:
            level = logging.WARNING
        elif debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        logger.info(f"当前模式：{'多线程' if threaded else '单线程'}")
        logger.info("开始启动机器人")
        self.use_multithreading = threaded
        logger.info("登录爱发电")
        self._login()
        cookies = {
            "auth_token": self.auth_token
        }
        headers = {
            "User-Agent": FakeUserAgent().random
        }
        session = requests.session()
        session.cookies.update(cookies)
        session.headers.update(headers)
        self.running = True
        logger.info("拉取latest_msg_id")
        latest_msg_list = session.get("https://afdian.com/api/message/dialogs?page=1&unread=0").json().get("data").get("list")
        if len(latest_msg_list) > 0:
            self.local_latest_msg_id = latest_msg_list[0].get("latest_msg_id")
            logger.debug(f"latest_msg_id：{self.local_latest_msg_id}")
        for i in self.__actions_mapping_funcs['startup']:
            i()
        logger.info("机器人已准备就绪，开始工作!")
        while self.running:
            try:
                check_new_msg_res = session.get(f"https://afdian.com/api/my/check?local_new_msg_id={self.local_latest_msg_id}")
                check_new_msg_data = check_new_msg_res.json()
                logger.debug(check_new_msg_data)
                if check_new_msg_data.get("ec") == 200:
                    unread_msg_num = check_new_msg_data.get("data")['unread_message_num']
                    if unread_msg_num > 0:
                        dialogs = session.get("https://afdian.com/api/message/dialogs?page=1&unread=1").json().get("data").get("list")
                        self._all_reply(session, dialogs)
                        self.local_latest_msg_id = dialogs[0].get("latest_msg_id")
                else:
                    logger.error("查看新消息失败!")
                time.sleep(wait)
            except AfdianResponeException as e:
                logger.error(f"爱发电接口返回错误：{e}")
                logger.info("重新登录中...")
                try:
                    logout(self.auth_token)
                    self._login()
                except:
                    logger.critical("ccccccc报错力(悲)")
                    logger.critical(traceback.format_exc())
                    logger.critical("紫砂中...")
                    exit(1)
            except KeyboardInterrupt:
                logger.info("正在停止机器人")
                self.stop()
            except:
                logger.error("ccc报错力:(")
                logger.error(traceback.format_exc())

    def stop(self):
        """
        停止机器人
        :return:
        """
        logger.info("销毁auth_token中")
        logout(self.auth_token)
        for i in self.__actions_mapping_funcs['shutdown']:
            i()
        logger.info("正在停止机器人")
        self.running = False