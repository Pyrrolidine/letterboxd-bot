""" Custom exception classes
    To catch, from bot.py, whether no item was found or a request failed
"""

class LbxdErrors(Exception):
    pass


class LbxdNotFound(LbxdErrors):
    pass


class LbxdServerError(LbxdErrors):
    pass
