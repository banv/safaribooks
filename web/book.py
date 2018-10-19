from datetime import datetime
import re
import os
import shutil
from html import escape
from pprint import pprint
from bookdb import BookDB
from constants import Status
from websafaribooks import WebSafariBooks

class Args:
    def __init__(self):
        self.cred = ''
        self.no_cookies = False
        self.no_kindle = False
        self.log = True
        self.mobi = False
        self.bookid = "9780471798545"


class Book:
    def __init__(self):
        self.bookdb = BookDB()
        self.safaribook = None


    def init_safari(self, bookid):
        self.args = Args()
        self.args.bookid = bookid
        print("login account: " + self.args.cred)
        print("book id :" + self.args.bookid)

        cred = WebSafariBooks.parse_cred(self.args.cred)
        if not cred:
            print("invalid credential: %s" % self.args.cred)

        self.args.cred = cred

        self.safaribook = WebSafariBooks(self.args)


    def download(self, bookid):
        book_path = ""
        # if (self.safaribook == None):
        self.init_safari(bookid)
        book_path = self.safaribook.download(self.args)

        return book_path

    def validate_id(self, bookid):
        match=re.search(r'^[\d]+$', bookid)
        return match


    def validate(self, bookid):
        if (bookid == None or not bookid.strip()):
            return {'code':3,'message':'Book ID is empty '}

        if self.validate_id(bookid) == None:
            return {'code':3,'message':'Invalid Book ID ' + bookid}

        # check book exist in db
        abook = self.bookdb.checkExist(bookid)
        if (abook != None):
            print("Book already inserted in DB")
            return {'code':2,'message':'Book already added'}
        else:
            print("start get book info from API: " + bookid)
            if (self.safaribook == None):
                self.init_safari(bookid)

            book_info = self.safaribook.web_get_book_info()
            pprint(book_info)

        if (book_info == 0):
            return {'code':1,'message':'API: unable to retrieve book info'}

        elif not isinstance(book_info, dict) or len(book_info.keys()) == 1:
            if "detail" in book_info:
                return {'code':1, 'message':book_info['detail']}
            else:
                return {'code':1, 'message':'Query book info failed'}
        else:
            print("query book info ok")
            self.safaribook.init_download(book_info)

            num_author = len(book_info['authors'])
            count = 0
            book_info['authorsName'] = ''
            for author in book_info['authors']:
                count += 1
                if (count < num_author):
                    book_info['authorsName'] += author['name'] + ", "
                else:
                    book_info['authorsName'] += author['name']


            book_info['downloadStatus'] = Status.QUEUED.value
            book_info['downloadCount'] = 0
            book_info['addedDate'] = datetime.now()
            book_info['downloadStart'] = ""
            book_info['downloadEnd'] = ""
            book_info['downloadLog'] = ""
            book_info['downloadPath'] = ""
            book_info['downloadTmpPath'] = os.path.join(self.safaribook.BOOK_PATH, "OEBPS")

            self.bookdb.insert(book_info)
            book_info['code'] = 0
            return book_info

    def list(self):
        simple_list_book = []
        listbook = self.bookdb.list()
        return listbook

    # Redownload multi books
    def redownload(self, bookids):
        redownload_bookids = {}
        for bookid in bookids:
            abook = self.bookdb.checkExist(bookid);
            if (abook):
                #book in DB
                # update db status
                print('Update book {} to queue'.format(bookid))
                self.bookdb.flagQueued(bookid)
                #delete local file
                print('Delete temp path {} for book {}'.format(abook['downloadTmpPath'], bookid))
                shutil.rmtree(abook['downloadTmpPath'], True);
                if os.path.exists(abook['downloadPath']):
                    print('Delete book path {} for book {}'.format(abook['downloadPath'], bookid))
                    os.remove(abook['downloadPath'])

                redownload_bookids[bookid] = Status.QUEUED.value
            else:
                print('book not exist : ' + bookid)
                redownload_bookids[bookid] = Status.NOTEXIST.value

        return redownload_bookids

    # Delete many books
    def delete(self, bookids):
        deleted_bookids = {}
        for bookid in bookids:
            abook = self.bookdb.checkExist(bookid);
            if (abook):
                # book in DB
                #delete local file
                shutil.rmtree(abook['downloadTmpPath'], True);
                if os.path.exists(abook['downloadPath']):
                    os.remove(abook['downloadPath'])
                # delete from db
                self.bookdb.delete(bookid)
                deleted_bookids[bookid] = Status.NOTEXIST.value
            else:
                print('book not exist : ' + bookid)
                deleted_bookids[bookid] = Status.NOTEXIST.value

        return deleted_bookids

    def log(self, bookid):
        PATH = os.path.dirname(os.path.realpath(__file__))
        log_file = "log/info_%s.log" % escape(bookid)
        log_full_path = os.path.join(PATH, log_file)
        print(log_full_path)
        if (os.path.exists(log_full_path)):
            with open(log_full_path, 'r') as f:
                return "<pre>" + f.read() + "</pre>"
        else:
            return "Download is not start for book: " + bookid