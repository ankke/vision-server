import simplejson
from flask import Flask, request, Response
from flask_cors import CORS
from flask_socketio import SocketIO

from database import AlchemyEncoder
from database_operations import get_cameras_for_configuration, add_camera_to_database, edit_camera_in_database, \
    get_camera_from_database, add_configuration_to_database, get_configuration_from_database, \
    delete_camera_from_database, delete_configuration_from_database, edit_configuration_in_database
from models import Camera, Configuration
from request_handler import refresh_handler, photo_handler, pano_handler, stop_live_feed
from video import gen, VideoCamera, active_cameras

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


@app.route('/health_check')
def hello_world():
    return "Hello world"


@app.route('/camera', methods=['GET'])
def get_camera():
    camera = get_camera_from_database(request.args.get('id'))
    return simplejson.dumps(camera, cls=AlchemyEncoder)


@app.route('/camera', methods=['POST'])
def add_camera():
    new_camera = add_camera_to_database(request.json)
    return simplejson.dumps(new_camera, cls=AlchemyEncoder)


@app.route('/camera', methods=['DELETE'])
def delete_camera():
    delete_camera_from_database(request.args.get('id'))
    return Response()


@app.route('/camera', methods=['PUT'])
def edit_camera():
    edit_camera_in_database(request.json)
    return Response()


@app.route('/cameras')
def get_cameras():
    return simplejson.dumps(Camera.query.all(), cls=AlchemyEncoder)


@app.route('/configuration', methods=['GET'])
def get_configuration():
    id = request.args.get("id")
    configuration_str = simplejson.dumps(get_configuration_from_database(id), cls=AlchemyEncoder)
    cameras_str = simplejson.dumps(get_cameras_for_configuration(id), cls=AlchemyEncoder)
    configuration = simplejson.loads(configuration_str)
    cameras = simplejson.loads(cameras_str)
    return {"configuration": configuration, "cameras": cameras}  # TODO Find something better...


@app.route('/configuration', methods=['POST'])
def add_configuration():
    add_configuration_to_database(request.json)
    return Response()


@app.route('/configuration', methods=['DELETE'])
def delete_configuration():
    delete_configuration_from_database(request.args.get('id'))
    return Response()


@app.route('/configuration', methods=['PUT'])
def edit_configuration():
    edit_configuration_in_database(request.json)
    return Response()


@app.route('/configurations')
def get_configurations():
    return simplejson.dumps(Configuration.query.all(), cls=AlchemyEncoder)


@app.route('/cameras/show')
def show():
    id = request.args.get('id')
    camera = Camera.query.filter_by(id=id).first()
    try:
        camera = VideoCamera(camera)
        active_cameras[id] = camera
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


@app.route('/cameras/edit', methods=['PUT'])
def edit():
    edit_camera_in_database(request.json)
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
