source venv/bin/activate
export FLASK_ENV=development
export FLASK_APP=app.py
python -m flask run &
python worker.py &

