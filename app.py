import json
import logging
from urllib.parse import unquote

import simplejson
from flask import Flask, request, Response
from flask_cors import CORS

from database.connection import db_session
from database.dao import (
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
    get_settings,
    update_settings,
)
from database.encoder import AlchemyEncoder
from video.helpers import (
    photo_handler,
    pano_handler,
    stop_live_feed,
    start_recording_handler,
    stop_recording_handler,
    stream,
)
from video.video_camera import VideoCamera, active_cameras

app = Flask(__name__)
CORS(app)

logger = logging.getLogger("root")


@app.route("/health_check")
def health_check():
    return "Healthy"


@app.route("/camera/<id_>", methods=["GET"])
def get_camera(id_):
    camera = get_camera_by_id(id_)
    return simplejson.dumps(camera, cls=AlchemyEncoder)


@app.route("/camera", methods=["POST"])
def add_camera_():
    logger.error(request.json)
    new_camera = add_camera(request.json)
    return simplejson.dumps(new_camera, cls=AlchemyEncoder)


@app.route("/camera/<id_>", methods=["DELETE"])
def delete_camera_(id_):
    delete_camera(id_)
    return Response()


@app.route("/camera", methods=["PUT"])
def edit_camera_():
    edit_camera(request.json)
    return Response()


@app.route("/cameras")
def get_cameras():
    return json.dumps(get_all_cameras())


@app.route("/configuration", methods=["POST"])
def configuration_post():
    add_configuration(request.json)
    return Response()


@app.route("/configuration/<id_>", methods=["GET"])
def get_configuration(id_):
    camera = get_configuration_by_id(id_)
    return simplejson.dumps(camera, cls=AlchemyEncoder)


@app.route("/configuration/<id_>", methods=["DELETE"])
def configuration_delete(id_):
    delete_configuration(id_)
    return Response()


@app.route("/configuration", methods=["PUT"])
def configuration_put():
    edit_configuration(request.json)
    return Response()


@app.route("/configurations", methods=["GET"])
def configurations_get():
    return json.dumps(get_all_configurations())


@app.route("/configuration/<id_>/cameras", methods=["GET"])
def cameras_for_configuration_get(id_):
    return json.dumps(get_cameras_for_configuration(id_))


@app.route("/camera/stream", methods=["GET"])
def camera_stream():
    camera_id = request.args.get("id")
    sub_stream = unquote(request.args.get("sub_stream"))
    camera = get_camera_by_id(camera_id)
    video_camera = VideoCamera(camera, sub_stream)
    video_camera.activate()
    return Response(
        stream(video_camera), content_type="multipart/x-mixed-replace;boundary=frame"
    )


@app.route("/camera/photo")
def photo():
    return photo_handler(
        int(request.args.get("id")),
        request.args.get("tag"),
        unquote(request.args.get("sub_stream")),
    )


@app.route("/camera/start")
def start_recording():
    return start_recording_handler(
        int(request.args.get("id")),
        request.args.get("tag"),
        unquote(request.args.get("sub_stream")),
    )


@app.route("/camera/stop")
def stop_recording():
    return stop_recording_handler(
        int(request.args.get("id")),
        unquote(request.args.get("sub_stream")),
    )


@app.route("/ptz/pano")
def pano():
    return pano_handler(
        int(request.args.get("id")),
        request.args.get("tag"),
        request.args.get("sub_stream"),
        int(request.args.get("rot_value")),
    )


@app.route("/camera/kill")
def kill():
    return stop_live_feed(
        int(request.args.get("id")), unquote(request.args.get("sub_stream"))
    )


@app.route("/settings", methods=["GET"])
def settings_get():
    settings = get_settings()
    return simplejson.dumps(settings, cls=AlchemyEncoder)


@app.route("/settings", methods=["PUT"])
def settings_put():
    settings = update_settings(request.json)
    return simplejson.dumps(settings, cls=AlchemyEncoder)


@app.route("/ptz/up", methods=["GET"])
def move_up():
    key = request.args.get("id") + unquote(request.args.get("sub_stream"))
    camera = active_cameras[key]
    camera.ptz_cam.move_up()
    return Response()


@app.route("/ptz/down", methods=["GET"])
def move_down():
    key = request.args.get("id") + unquote(request.args.get("sub_stream"))
    camera = active_cameras[key]
    camera.ptz_cam.move_down()
    return Response()


@app.route("/ptz/left", methods=["GET"])
def move_left():
    key = request.args.get("id") + unquote(request.args.get("sub_stream"))
    camera = active_cameras[key]
    camera.ptz_cam.move_left()
    return Response()


@app.route("/ptz/right", methods=["GET"])
def move_right():
    key = request.args.get("id") + unquote(request.args.get("sub_stream"))
    camera = active_cameras[key]
    camera.ptz_cam.move_right()
    return Response()


@app.teardown_request
def teardown_db(_exception):
    db_session.remove()


if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    logger = logging.getLogger("root")
    logger.handlers = gunicorn_logger.handlers
    logger.setLevel(gunicorn_logger.level)
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == "__main__":
    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)
    app.run(
        host="0.0.0.0",
        port=5000,
    )
