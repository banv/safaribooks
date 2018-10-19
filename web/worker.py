from time import sleep
from datetime import datetime
from tendo import singleton
from app import app
from book import Book
from bookdb import BookDB
class Worker:
    def __init__(self):
        self.bookdb = BookDB()
        self.book = Book()
    def run(self):
        print("Start worker at: {}".format(datetime.now()))
        list_queued =  self.bookdb.listQueued()
        list_retry = self.bookdb.listRetry()
        print("Queued book : " + str(list_queued.count()))
        print("Retry book : " + str(list_retry.count()))

        for book in list_queued:
            bookid = book['identifier']
            print("Start to download " + bookid)
            self.bookdb.flagDownloading(bookid)
            try:
                path = self.book.download(bookid)
                self.bookdb.flagSuccess(bookid, path)
            except Exception as err:
                print("Error download book " + bookid, err)
                self.bookdb.flagFailed(bookid, str(err))

        for book in list_retry:
            bookid = book['identifier']
            print("Start to retry " + bookid)
            self.bookdb.flagRetrying(bookid)
            try:
                path = self.book.download(bookid)
                self.bookdb.flagSuccess(bookid, path)
            except Exception as err:
                print("Error download book " + bookid, err)
                self.bookdb.flagFailed(bookid, str(err))

        print("Worker done at: {}".format(datetime.now()))

if __name__== "__main__":
    me = singleton.SingleInstance()
    worker = Worker()
    while True:
        worker.run()
        # download finished, wait 5 seconds for next download
        sleep(5)









