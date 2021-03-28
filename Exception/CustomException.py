class ServiceError(Exception):
    pass


class RequestError(Exception):
    pass


class APIError(Exception):
    pass


class NetworkError(Exception):
    pass


class IndexError(Exception):
    pass


class OutOfSearch(Exception):
    pass


class TooQuick(Exception):
    pass

class NotSame(Exception):
    pass