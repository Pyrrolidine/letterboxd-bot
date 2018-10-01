class LbxdErrors(Exception):
    pass


class LbxdNotFound(LbxdErrors):
    pass


class LbxdServerError(LbxdErrors):
    pass
