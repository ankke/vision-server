import simplejson
from flask import Flask, request, Response

from database import AlchemyEncoder
from database_operations import edit_camera, add_camera, delete_camera
from models import Camera
from request_handler import refresh_handler, photo_handler, pano_handler, stop_live_feed, live_feed

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello world"


@app.route('/cameras')
def get_cameras():
    return simplejson.dumps(Camera.query.all(), cls=AlchemyEncoder)


@app.route('/cameras/delete')
def delete():
    delete_camera(request.args.get('id'))
    return Response()


@app.route('/cameras/show')
def show():
    return live_feed(request.args.get('id'))


@app.route('/cameras/refresh')
def refresh():
    return refresh_handler()


@app.route('/cameras/photo')
def photo(request):
    return photo_handler(request.args.get('id'))


@app.route('/cameras/pano')
def pano(request):
    return pano_handler(request.args.get('id'))


@app.route('/cameras/kill')
def kill(request):
    return stop_live_feed(request.args.get('id'))


@app.route('/cameras/add', methods=['POST'])
def add():
    add_camera(request.json)
    return Response()


@app.route('/cameras/edit', methods=['PUT'])
def edit():
    edit_camera(request.json)
    return Response()


if __name__ == '__main__':
    app.run()
