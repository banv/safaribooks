import os
import sys
import json
from lxml import html, etree
from html import escape
from multiprocessing import Process, Queue, Value
from safaribooks import SafariBooks, WinQueue, Display
from safaribooks import PATH, COOKIES_FILE

class WebSafariBooks(SafariBooks):
    def __init__(self, args):
        self.args = args
        self.display = Display("log/info_%s.log" % escape(args.bookid))
        self.display.intro()

        self.cookies = {}

        if not args.cred:
            if not os.path.isfile(COOKIES_FILE):
                self.display.exit("Login: unable to find cookies file.\n"
                                  "    Please use the --cred option to perform the login.")

            self.cookies = json.load(open(COOKIES_FILE))

        else:
            self.display.info("Logging into Safari Books Online...", state=True)
            self.do_login(*args.cred)
            if not args.no_cookies:
                json.dump(self.cookies, open(COOKIES_FILE, "w"))

        self.book_id = args.bookid
        self.api_url = self.API_TEMPLATE.format(self.book_id)


    def web_get_book_info(self):
        response = self.requests_provider(self.api_url)
        if response == 0:
            return response

        response = response.json()
        if "last_chapter_read" in response:
            del response["last_chapter_read"]

        return response

    def init_download(self, book_info):
        self.book_info = book_info
        self.display.book_info(self.book_info)

        self.book_title = self.book_info["title"]
        self.base_url = self.book_info["web_url"]

        self.clean_book_title = "".join(self.escape_dirname(self.book_title).split(",")[:2]) \
                                + " ({0})".format(self.book_id)

        books_dir = os.path.join(PATH, "Books")
        if not os.path.isdir(books_dir):
            os.mkdir(books_dir)

        self.BOOK_PATH = os.path.join(books_dir, self.clean_book_title)

    def download(self, args):
        self.display.info("Retrieving book info...")
        self.book_info = self.get_book_info()
        self.display.book_info(self.book_info)

        self.display.info("Retrieving book chapters...")
        self.book_chapters = self.get_book_chapters()

        self.chapters_queue = self.book_chapters[:]

        if len(self.book_chapters) > sys.getrecursionlimit():
            sys.setrecursionlimit(len(self.book_chapters))

        self.book_title = self.book_info["title"]
        self.base_url = self.book_info["web_url"]

        self.clean_book_title = "".join(self.escape_dirname(self.book_title).split(",")[:2]) \
                                + " ({0})".format(self.book_id)

        books_dir = os.path.join(PATH, "Books")
        if not os.path.isdir(books_dir):
            os.mkdir(books_dir)

        self.BOOK_PATH = os.path.join(books_dir, self.clean_book_title)
        self.css_path = ""
        self.images_path = ""
        self.create_dirs()
        self.display.info("Output directory:\n    %s" % self.BOOK_PATH)

        self.chapter_title = ""
        self.filename = ""
        self.css = []
        self.images = []

        self.display.info("Downloading book contents... (%s chapters)" % len(self.book_chapters), state=True)
        self.BASE_HTML = self.BASE_01_HTML + (self.KINDLE_HTML if not args.no_kindle else "") + self.BASE_02_HTML

        self.cover = False
        self.get()
        if not self.cover:
            self.cover = self.get_default_cover()
            cover_html = self.parse_html(
                html.fromstring("<div id=\"sbo-rt-content\"><img src=\"Images/{0}\"></div>".format(self.cover)), True
            )

            self.book_chapters = [{
                "filename": "default_cover.xhtml",
                "title": "Cover"
            }] + self.book_chapters

            self.filename = self.book_chapters[0]["filename"]
            self.save_page_html(cover_html)

        self.css_done_queue = Queue(0) if "win" not in sys.platform else WinQueue()
        self.display.info("Downloading book CSSs... (%s files)" % len(self.css), state=True)
        self.collect_css()
        self.images_done_queue = Queue(0) if "win" not in sys.platform else WinQueue()
        self.display.info("Downloading book images... (%s files)" % len(self.images), state=True)
        self.collect_images()

        self.display.info("Creating EPUB file...", state=True)
        self.create_epub()

        if not args.no_cookies:
            json.dump(self.cookies, open(COOKIES_FILE, "w"))

        self.display.done(os.path.join(self.BOOK_PATH, self.book_id + ".epub"))
        self.display.unregister()

        if args.mobi:
            self.display.info("Creating MOBI file...", state=True)
            self.convert_mobi()


        if not self.display.in_error and not args.log:
            os.remove(self.display.log_file)

        return os.path.join(self.BOOK_PATH, self.book_id + ".epub")

    def convert_mobi(self):
        epub_file = os.path.join(self.BOOK_PATH, self.book_id + ".epub")
        mobi_file = os.path.join(self.BOOK_PATH, self.book_id + ".mobi")
        covert_opts = "--mobi-ignore-margin"
        convert_app = "/Applications/calibre.app/Contents/console.app/Contents/MacOS/ebook-convert"
        log_opts = "2>log/mobi_" + str(self.book_id) + ".log"
        command = convert_app + " \"" + epub_file + "\" \"" + mobi_file + "\" " + covert_opts + " "  + log_opts
        self.display.info("Command: %s" % command, state=True)
        os.system(command)