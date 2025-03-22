import logging

__all__ = ['disable_warnings']

logger = logging.getLogger("AfdianBot")

class Filter(logging.Filter):
    def filter(self, record):
        return record.levelno != logging.WARNING

def disable_warnings(status=True):
    if status:
        logger.addFilter(Filter())
    else:
        logger.removeFilter(Filter())