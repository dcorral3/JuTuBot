from pymongo import MongoClient
import dbconf


class DB:
    def __init__(self):
        self.db = MongoClient(
            host=dbconf.host,
            username=dbconf.username,
            password=dbconf.password,
            authSource=dbconf.authSource
        )[dbconf.authSource]

    def insert_user(self, user_id):
        return self.db.users.insert_one({
            '_id': user_id,
            'history': []
        })

    def get_user(self, user_id):
        return self.db.users.find_one({'_id': user_id})
