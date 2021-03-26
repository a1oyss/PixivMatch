class Config(object):
    """
    配置对象,包括api_key,minsim,db_bitmask
    """
    def __init__(self, api_key, minsim, db_bitmask):
        self._db_bitmask = db_bitmask
        self._minsim = minsim
        self._api_key = api_key

    @property
    def api_key(self):
        return self._api_key

    @property
    def minsim(self):
        return self._minsim

    @property
    def db_bitmask(self):
        return self._db_bitmask

    @db_bitmask.setter
    def db_bitmask(self, value):
        self._db_bitmask = value

    @minsim.setter
    def minsim(self, value):
        self._minsim = value

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    def __str__(self):
        return "api_key:%s,minsim:%s,db_bitmask:%s" % (self._api_key, self._minsim, self._db_bitmask)
