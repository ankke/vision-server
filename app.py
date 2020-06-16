import simplejson
from flask import Flask, request, Response
from flask_socketio import SocketIO

from database import AlchemyEncoder
from database_operations import edit_camera, add_camera, delete_camera
from models import Camera
from flask_cors import CORS
from request_handler import refresh_handler, photo_handler, pano_handler, stop_live_feed
from video import gen, VideoCamera, active_cameras

app = Flask(__name__)
CORS(app)


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


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
    camera = Camera.query.filter_by(id=request.args.get('id')).first()
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client_socket.connect(('localhost', 5000))

    try:
        camera = VideoCamera(camera)
        active_cameras[id] = camera
        # for video_frame in gen(camera):
        #     # client_socket.sendall(video_frame)
        #     socketio.emit('sendFrame', {'image': video_frame}, namespace='/web')
        # return Response()
        # socketio.emit(
        #     'sendFrame',
        #     {
        #         'image': live_feed(request.args.get('id'))
        #     }, namespace='/web')

        return Response(gen(camera), content_type="multipart/x-mixed-replace;boundary=frame")
    except ConnectionError:
        print("closing tab")
        camera.kill()
        del camera
        return Response()


@app.route('/cameras/refresh')
def refresh():
    return refresh_handler()


@app.route('/cameras/photo')
def photo():
    return photo_handler(request.args.get('id'))


@app.route('/cameras/pano')
def pano():
    return pano_handler(request.args.get('id'))


@app.route('/cameras/kill')
def kill():
    return stop_live_feed(request.args.get('id'))


@app.route('/cameras/add', methods=['POST'])
def add():
    add_camera(request.json)
    return Response()


@app.route('/cameras/edit', methods=['PUT'])
def edit():
    edit_camera(request.json)
    return Response()


@socketio.on('connect', namespace='/web')
def connect_web():
    print('[INFO] Web client connected: {}'.format(request.sid))


@socketio.on('disconnect', namespace='/web')
def disconnect_web():
    print('[INFO] Web client disconnected: {}'.format(request.sid))


if __name__ == '__main__':
    print("start")
    socketio.run(app=app, host='127.0.0.1', port=5000)
