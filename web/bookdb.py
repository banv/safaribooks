from datetime import datetime

from constants import Status
from constants import MAX_RETRY

class BookDB:
    def __init__(self):
        from app import mongo
        self.mongo = mongo

    def list(self):
        return self.mongo.db.safaribooks.find({})

    def checkExist(self, bookid):
        abook = self.mongo.db.safaribooks.find_one({'identifier':bookid})
        print('query book from db ' + bookid + " result : " + str(abook != None))
        # pprint(abook)
        return abook

    def insert(self, book_info):
        self.mongo.db.safaribooks.insert(book_info)

    def listQueued(self):
        return self.mongo.db.safaribooks.find({'downloadStatus':Status.QUEUED.value})

    def listRetry(self):
        return self.mongo.db.safaribooks.find({"$and":[{'downloadStatus':Status.FAILED.value}, {'downloadCount': {"$lt":MAX_RETRY}}]})

    def flagDownloading(self, bookid):
        self.mongo.db.safaribooks.update_one({'identifier':bookid}, {"$set": {'downloadStatus': Status.DOWNLOADING.value, 'downloadStart': datetime.now()},
                                                                "$inc": {'downloadCount' : 1}})
    def flagRetrying(self, bookid):
        self.mongo.db.safaribooks.update_one({'identifier':bookid}, {"$set": {'downloadStatus': Status.RETRYING.value, 'downloadStart': datetime.now()},
                                                                "$inc": {'downloadCount' : 1}})
    def flagSuccess(self, bookid, path):
        self.mongo.db.safaribooks.update_one({'identifier':bookid}, {"$set": {'downloadStatus': Status.SUCCESS.value,
                                                                         'downloadEnd': datetime.now(),
                                                                         'downloadPath': path}})

    def flagFailed(self, bookid, log):
        self.mongo.db.safaribooks.update_one({'identifier':bookid}, {"$set": {'downloadStatus': Status.FAILED.value,
                                                                         'downloadEnd': datetime.now(),
                                                                         'downloadLog':log}})
    def flagQueued(self, bookid):
        self.mongo.db.safaribooks.update_one({'identifier':bookid}, {"$set": {'downloadStatus': Status.QUEUED.value}})


    def delete(self, bookid):
        self.mongo.db.safaribooks.delete_one({'identifier':bookid})