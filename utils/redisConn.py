import redis

class Redis:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.__conn = redis.Redis(connection_pool=redis.BlockingConnectionPool(
            max_connections=15, host=host, port=port, db=db, password=password),decode_responses=True)

    def __getattr__(self, command):
        def _(*args):
            return getattr(self.__conn, command)(*args)  # 重新组装方法调用
        return _
