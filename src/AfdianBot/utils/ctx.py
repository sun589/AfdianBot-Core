from threading import local
from .types import TextMsg, SponsorMsg
from typing import Union

__all__ = ['get_current_args','get_current_msg']

_local_ctx = local()

def get_current_args() -> tuple:
    return getattr(_local_ctx, 'args', ())

def get_current_msg() -> Union[TextMsg,SponsorMsg]:
    return getattr(_local_ctx, 'msg', None)

class MessageContext:

    def __init__(self, msg:Union[TextMsg,SponsorMsg], args:tuple=()):
        self.msg:Union[TextMsg,SponsorMsg] = msg
        self.args:tuple = args

    def __enter__(self):
        _local_ctx.msg = self.msg
        _local_ctx.args = self.args
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del _local_ctx.msg
        del _local_ctx.args