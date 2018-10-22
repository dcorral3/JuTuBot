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

    def add_to_history(self, user_id, data):
        history_record = {'url': data['url'], 'timestamp': data['timestamp']}
        self.db.users.update_one({'_id': user_id},
                                 {'$addToSet': {'history': history_record}}, 
                                 upsert=True)

    def get_history(self, user_id):
        data = self.db.users.find({"_id": user_id}, {"_id": 0})
        data = data[0]["history"]
        return data
    
