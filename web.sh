cd web
source venv/bin/activate
export FLASK_ENV=development
export FLASK_APP=app.py
flask run &
python worker.py &
open /Applications/Google\ Chrome.app/ http://localhost:5000/book

