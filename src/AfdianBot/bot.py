import threading
from .exceptions import AfdianResponeException, AfdianGetMsgFailed
from inspect import getfullargspec
from .utils import login,logout
from .utils import get_api_token
from .utils import types
from .utils import bot_vars
from .utils import ctx
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
        self.__session = requests.session()
        self.use_multithreading = False
        self.local_latest_msg_id = None
        self.running = False
        self.pass_args = False
        console = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
        console.setFormatter(formatter)
        logger.addHandler(console)

    def _login(self):
        """
        机器人内部登录函数
        """
        logger.info("获取auth_token")
        logger.debug(f"登录爱发电，账号：{self.__account[:4] + '****'}")
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

    def register(self, name):
        """
        注册一个指令
        """
        def reg(func):
            self.add_cmd(name, func)
            return func
        return reg

    def add_cmd(self, cmd, func):
        """
        以函数的形式添加一个指令
        """
        self.__mapping[cmd] = func

    def at(self, *action):
        """
        设置函数在指定动作发生时执行,注意，当动作为sponsorship时，func的参数为SponsorMsg类型
        而在其他情况下，均不会传参
        :param action: startup/shutdown/sponsorship/unknown_cmd
        """
        def wrapper(func):
            self.func_at(func, *action)
        return wrapper

    def func_at(self, func, *action):
        """
        同at装饰器的介绍，通过函数的形式添加一个动作
        :param action: startup/shutdown/sponsorship/unknown_cmd
        :param func:
        """
        for i in action:
            self.__actions_mapping_funcs[i].add(func)

    def _handle_sponsorship_msg(self, msg_data):
        """
        处理赞助消息
        """
        msg = types.SponsorMsg(msg_data)
        logger.info(f"收到赞助消息,金额：{msg.amount} 用户id:{msg.sender_id}")
        for f in self.__actions_mapping_funcs['sponsorship']:
            try:
                f(msg)
            except:
                logger.error(f"在sponsorship动作出错:\n{traceback.format_exc()}")

    def _handle_text_msg(self, msg, cmd) -> bool:
        """
        处理文本消息
        """
        match = re.match(cmd, msg.content)
        if not match:
            return False
        try:
            args = match.groups()
            with ctx.MessageContext(msg=msg, args=args):
                if self.pass_args:
                    self.__mapping[cmd](msg, args)
                else:
                    self.__mapping[cmd]()
        except:
            logger.error(f"在{cmd}命令出错:\n{traceback.format_exc()}")
        return True

    def _reply(self, dialog: dict):
        """
        处理消息，执行函数
        """
        user_id = dialog.get("user")['user_id']
        msg_res = self.__session.get(
            f"https://afdian.com/api/message/messages?user_id={user_id}&type=new&message_id={self.local_latest_msg_id}"
        )
        msg_data = msg_res.json()
        if msg_data.get("ec") != 200:
            raise AfdianGetMsgFailed(msg_data.get("ec"), msg_data.get("em"))
        for msg_data in msg_data['data']['list']:
            msg = types.Msg(msg_data)
            if msg.sender_type == "send":
                continue
            if msg.msg_type == 2:
                self._handle_sponsorship_msg(msg_data)
                continue
            if msg.msg_type not in [1, 7]:
                logger.warning(
                    f"获取到未知的消息类型{msg.msg_type}! 当前处理msg_id:{msg.msg_id} 时间戳:{msg.send_time}"
                )
                continue
            msg = types.TextMsg(msg_data)
            logger.debug(f"收到消息：{msg.content} 用户id:{msg_data['message'].get('sender')}")
            for cmd in self.__mapping.keys():
                if self._handle_text_msg(msg, cmd):
                    break
            else:
                for cmd in self.__actions_mapping_funcs['unknown_cmd']:
                    cmd(msg)

    def _all_reply(self, dialogs:list):
        """
        回复所有消息
        :return:
        """
        if self.use_multithreading:
            # 创建线程列表
            threads = [threading.Thread(target=self._reply, args=(dialog,)) for dialog in dialogs]
            # 启动所有线程
            for thread in threads:
                thread.start()
        else:
            # 单线程处理所有对话
            for dialog in dialogs:
                self._reply(dialog)

    def send_msg(self, msg,user_id:str):
        """
        发送消息,只支持文本消息
        :param msg: 消息内容
        :param user_id: 用户id,默认使用处理对应消息的user_id
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

    def run(self, no_log=False, wait=10, debug=False, threaded=False, pass_args=False):
        """
        运行机器人,默认使用单线程模式,可选择多线程模式
        :param no_log: 是否不输出日志
        :param wait: 拉取消息列表的间隔时间
        :param debug: 是否开启debug模式(将输出debug日志到控制台)
        :param threaded: 是否使用多线程模式
        """
        # 根据条件选择日志级别
        level = (
            logging.WARNING if no_log
            else logging.DEBUG if debug
            else logging.INFO
        )
        if not pass_args:
            logger.warning(
            f"在v1.0.4后将使用上下文的方式而非传参方式来传递msg和命令参数,你可将参数pass_args改为True更为传参方式(详见文档)"
        )
            logger.warning("本警告将在若干版本后移除，你可调用本库config.disable_warning禁用警告")
        logger.setLevel(level)
        logger.info(f"当前模式：{'多线程' if threaded else '单线程'}")
        logger.info("开始启动机器人")
        self.use_multithreading = threaded
        self.pass_args = pass_args
        logger.info("登录爱发电")
        self._login()
        cookies = {
            "auth_token": self.auth_token
        }
        headers = {
            "User-Agent": FakeUserAgent().random
        }
        self.__session = requests.session()
        self.__session.cookies.update(cookies)
        self.__session.headers.update(headers)
        self.running = True
        logger.info("拉取latest_msg_id")
        latest_msg_list = self.__session.get("https://afdian.com/api/message/dialogs?page=1&unread=0").json().get("data").get("list")
        if len(latest_msg_list) > 0:
            self.local_latest_msg_id = latest_msg_list[0].get("latest_msg_id")
            logger.debug(f"latest_msg_id：{self.local_latest_msg_id}")
        for i in self.__actions_mapping_funcs['startup']:
            i()
        logger.info("机器人已准备就绪，开始工作!")
        while self.running:
            try:
                check_new_msg_req = self.__session.get(f"https://afdian.com/api/my/check?local_new_msg_id={self.local_latest_msg_id}")
                check_new_msg_data = check_new_msg_req.json()
                if check_new_msg_data.get("ec") == 200:
                    unread_msg_num = check_new_msg_data.get("data")['unread_message_num']
                    if unread_msg_num > 0:
                        dialogs = self.__session.get("https://afdian.com/api/message/dialogs?page=1&unread=1").json().get("data").get("list")
                        self._all_reply(dialogs)
                        self.local_latest_msg_id = dialogs[0].get("latest_msg_id")
                else:
                    raise AfdianGetMsgFailed(check_new_msg_data.get("ec"), check_new_msg_data.get("em"))
                time.sleep(wait)
            except AfdianResponeException:
                logger.error(f"爱发电接口返回错误：{traceback.format_exc()}")
                logger.info("重新登录中...")
                logout(self.auth_token)
                self._login()
            except requests.exceptions.JSONDecodeError: # 爱发电api返回抽风bug处理
                logger.debug("爱发电api返回错误的json数据，忽略")
            except KeyboardInterrupt:
                self.stop()
            except:
                logger.error(traceback.format_exc())

    def stop(self):
        """
        停止机器人
        :return:
        """
        logger.info("销毁auth_token中")
        logout(self.auth_token)
        logger.info("正在停止机器人...")
        self.running = False
        for i in self.__actions_mapping_funcs['shutdown']:
            i()