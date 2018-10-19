from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask_pymongo import PyMongo
from pprint import pprint
from mongoflask import MongoJSONEncoder, ObjectIdConverter

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/safaribook"
app.json_encoder = MongoJSONEncoder
app.url_map.converters['objectid'] = ObjectIdConverter

mongo = PyMongo(app)

#book using mongo, so call book after init mongo
from book import Book


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/book')
def book():
    # book = Book("9780471798545")
    # pprint(book.validate())
    simple_list_book = Book().list()
    pprint(simple_list_book.count())
    # for book in listbook:
    #     pprint(book)

    return render_template('book.html', listbook=simple_list_book, total=simple_list_book.count())

@app.route('/validate', methods=['POST'])
def validate():

    bookid = request.form['bookid']
    print("request book id: " + bookid)
    book = Book()
    result = book.validate(bookid)
    print("verify result")
    pprint(result)
    if (result['code'] != 0):
        print("validate failed")
    else :
        print("validate ok")
        # add to list


    return jsonify(result)

@app.route('/redownload', methods=['POST'])
def redownload():
    bookids = request.form.getlist('bookids[]')
    print("request redownload book ids:")
    print(bookids)
    redownload_bookids = Book().redownload(bookids)
    return jsonify(redownload_bookids)


@app.route('/delete', methods=['POST'])
def delete():
    bookids = request.form.getlist('bookids[]')
    print("request delete book ids:")
    print(bookids)
    deleted_bookids = Book().delete(bookids)
    return jsonify(deleted_bookids)

@app.route('/log', methods=['GET'])
def log():
    bookid = request.args.get('bookid')
    return Book().log(bookid)

