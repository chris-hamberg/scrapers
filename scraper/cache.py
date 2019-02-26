from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.binary import Binary
import pickle, zlib

class MongoCache:

    def __init__(self, client=None, expires=timedelta(days=30)):
        self.client = MongoClient('localhost', 27017) if client is None else client
        self.db = self.client.cache
        self.db.webpage.create_index('timestamp', expireAfterSeconds=expires.total_seconds())

    def __getitem__(self, url):
        '''Load value at this URL'''
        record = self.db.webpage.find_one({'_id': url})
        if record:
            return pickle.loads(zlib.decompress(record['result']))
        else:
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        '''Save value for this URL'''
        record = {
                'result': Binary(zlib.compress(pickle.dumps(result))), 
                'timestamp': datetime.utcnow()
                }
        self.db.webpage.update({'_id': url}, {'$set': record}, upsert=True)
