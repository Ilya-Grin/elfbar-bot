from pymongo import MongoClient


class Database:
    def __init__(self, client):
        # CONNECT TO DB
        self.client = MongoClient(client)
        self.dbname = self.client['accountant']
        self.collection = self.dbname['users']

    def admins_get(self):
        # GET ALL ADMINS
        return self.collection.find_one({'_id': 'admins'})['admins']

    def user_get(self, user_id):
        # GET USER FROM DB
        return self.collection.find_one({'_id': user_id})

    def card_edit(self, user_id, card):
        # EDIT USER CARD
        self.collection.update_one({'_id': user_id}, {'$set': {'card': card}})

    def user_add(self, message):
        # USER ADD TO DB
        self.collection.insert_one(
            {'_id': message.from_user.id, 'name': message.from_user.first_name, 'card': []})
        print(f'New user registered ID: {message.from_user.id}')

    def bars_get(self):
        return self.collection.find_one({'_id': 'bars'})

    def bars_set(self, bars):
        self.collection.update_one({'_id': 'bars'}, {'$set': {'name': bars}})
