class Illust(object):
    """
    用于存储插图各种信息

    similarity:相似度
    illust_id:插图id
    illust_url:插图url
    illust_title:插图title
    member_id:作者id
    member_name:作者name
    """

    def __init__(self, similarity, illust_id, illust_url, illust_title, member_id, member_name):
        self._similarity = similarity
        self._illust_id = illust_id
        self._illust_url = illust_url
        self._illust_title = illust_title
        self._member_id = member_id
        self._member_name = member_name

    @property
    def similarity(self):
        return self._similarity

    @property
    def illust_id(self):
        return self._illust_id

    @property
    def illust_url(self):
        return self._illust_url

    @property
    def illust_title(self):
        return self._illust_title

    @property
    def member_id(self):
        return self._member_id

    @property
    def member_name(self):
        return self._member_name

    @similarity.setter
    def similarity(self, value):
        self._similarity = value

    @illust_id.setter
    def illust_id(self, value):
        self._illust_id = value

    @illust_url.setter
    def illust_url(self, value):
        self._illust_url = value

    @illust_title.setter
    def illust_title(self, value):
        self._illust_title = value

    @member_id.setter
    def member_id(self, value):
        self._member_id = value

    @member_name.setter
    def member_name(self, value):
        self._member_name = value
