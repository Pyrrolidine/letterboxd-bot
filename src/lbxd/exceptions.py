class LbxdErrors(Exception):
    pass


class LbxdNotFound(LbxdErrors):
    def __init__(self, message):
        self.message = message


class LbxdServerError(LbxdErrors):
    def __init__(self, message):
        self.message = message
