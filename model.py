from pymongo import MongoClient
import dbconf
import datetime


class DB:
    def __init__(self):
        self.db = MongoClient(
            host=dbconf.host,
            username=dbconf.username,
            password=dbconf.password,
            authSource=dbconf.authSource
        )[dbconf.authSource]

    def insert_user(self, user_id, first_name):
        return self.db.users.insert_one({
            '_id': user_id,
            'first_name': first_name,
            'history': []
        })

    def get_user(self, user_id):
        return self.db.users.find_one({'_id': user_id})

    def add_to_history(self, user_id, data):
        tmp = data.copy()
        del tmp['download_count']
        del tmp['last_download']
        del tmp['t_audio']
        self.db.users.update_one({'_id': user_id},
                                 {'$addToSet': {'history': tmp}},
                                 upsert=True)

    def get_history(self, user_id):
        data = self.db.users.find({"_id": user_id}, {"_id": 0})
        return data[0]["history"]

    def insert_file_record(self, data):
        return self.db.files.insert_one(data)

    def get_file(self, url):
        return self.db.files.find_one({"_id": url})

    def update_record(self, url):
        dt = datetime.datetime.now().strftime("%s")
        self.db.files.update_one(
            {'_id': url},
            {'$inc': {'download_count': 1},
             '$set': {'last_download': dt}},
            upsert=True)
