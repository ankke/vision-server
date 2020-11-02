import json
import logging

import simplejson
from flask import Flask, request, Response
from flask_cors import CORS
from flask_socketio import SocketIO

from database.connection import db_session
from database.encoder import AlchemyEncoder
from database.operations import (
    get_cameras_for_configuration,
    add_camera,
    edit_camera,
    get_camera_by_id,
    add_configuration,
    get_configuration_by_id,
    delete_camera,
    delete_configuration,
    edit_configuration,
    get_all_cameras,
    get_all_configurations,
)
from video.helpers import photo_handler, pano_handler, stop_live_feed
from video.video import VideoCamera, active_cameras, gen

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)


@app.route("/health_check")
def health_check():
    return "Healthy"


@app.route("/camera", methods=["GET"])
def get_camera():
    camera = get_camera_by_id(request.args.get("id"))
    return simplejson.dumps(camera, cls=AlchemyEncoder)


@app.route("/camera", methods=["POST"])
def add_camera_():
    new_camera = add_camera(request.json)
    return simplejson.dumps(new_camera, cls=AlchemyEncoder)


@app.route("/camera/<id>", methods=["DELETE"])
def delete_camera_(id):
    delete_camera(id)
    return Response()


@app.route("/camera", methods=["PUT"])
def edit_camera_():
    print(request.json)
    edit_camera(request.json)
    return Response()


@app.route("/cameras")
def get_cameras():
    return json.dumps(get_all_cameras())


@app.route("/configuration", methods=["GET"])
def get_configuration():
    id = request.args.get("id")
    configuration_str = simplejson.dumps(
        get_configuration_by_id(id), cls=AlchemyEncoder
    )
    cameras_str = simplejson.dumps(
        get_cameras_for_configuration(id), cls=AlchemyEncoder
    )
    configuration = simplejson.loads(configuration_str)
    cameras = simplejson.loads(cameras_str)
    return {
        "configuration": configuration,
        "cameras": cameras,
    }  # TODO Find something better...


@app.route("/configuration", methods=["POST"])
def add_configuration():
    add_configuration(request.json)
    return Response()


@app.route("/configuration", methods=["DELETE"])
def delete_configuration():
    delete_configuration(request.args.get("id"))
    return Response()


@app.route("/configuration", methods=["PUT"])
def edit_configuration():
    edit_configuration(request.json)
    return Response()


@app.route("/configurations")
def get_configurations():
    return simplejson.dumps(get_all_configurations(), cls=AlchemyEncoder)


@app.route("/camera/show")
def show():
    id = request.args.get("id")
    camera = get_camera_by_id(id)
    try:
        camera = VideoCamera(camera)
        active_cameras[id] = camera
        return Response(
            gen(camera), content_type="multipart/x-mixed-replace;boundary=frame"
        )
    except ConnectionError:
        print("closing tab")
        camera.kill()
        del camera
        return Response()


# @app.route("/cameras/refresh")
# def refresh():
#     return refresh_handler()


@app.route("/camera/photo")
def photo():
    return photo_handler(request.args.get("id"))


@app.route("/camera/pano")
def pano():
    return pano_handler(request.args.get("id"))


@app.route("/camera/kill")
def kill():
    return stop_live_feed(request.args.get("id"))


@socketio.on("connect", namespace="/web")
def connect_web():
    print("[INFO] Web client connected: {}".format(request.sid))


@socketio.on("disconnect", namespace="/web")
def disconnect_web():
    print("[INFO] Web client disconnected: {}".format(request.sid))


@app.teardown_request
def teardown_db(exception):
    db_session.remove()


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == "__main__":
    print("start")
    socketio.run(app=app, host="127.0.0.1", port=5000)
