import simplejson

from flask import Flask

from database import query_db, close_db

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello world"


@app.route('/cameras')
def get_cameras():
    result = simplejson.dumps(query_db('select * from camera_camera'))
    close_db()
    return result


if __name__ == '__main__':
    app.run()
