import logging

from tinydb import TinyDB, Query
from tinydb_serialization import SerializationMiddleware

from serilazers import DateTimeSerializer

logger = logging.getLogger(__name__)

serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), 'TinyDate')

db = TinyDB('db.json', storage=serialization)


class Paste(object):
    def __init__(self):
        self.date = None
        self.title = ''
        self.content = ''
        self.author = ''
        self.link = ''

    def save(self):
        db.insert(self.__dict__)
        logger.info('Saved new paste: %s' % self.link)

    def exist_post(self):
        PasteQuery = Query()

        results = db.search(PasteQuery.link == self.link)

        return len(results) > 0
