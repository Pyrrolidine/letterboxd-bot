""" Custom exception classes
    To catch whether no item was found or a request failed
"""

class LbxdErrors(Exception):
    pass


class LbxdNotFound(LbxdErrors):
    pass


class LbxdServerError(LbxdErrors):
    pass
