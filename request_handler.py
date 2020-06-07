import subprocess
from datetime import datetime

from flask import Response

from database import db_session
from models import Camera
from video import gen, active_cameras, VideoCamera


def live_feed(id):
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


def stop_live_feed(id):
    cam = active_cameras.get(id)
    if cam is not None:
        cam.kill()
    active_cameras.pop(id)
    del cam
    return Response()


def refresh_handler():
    for cam in Camera.query.all():
        cam.enabled = True
        try:
            print(" ".join(["ping", "-c", "1", cam.ip_address.strip()]))
            subprocess.check_output(["ping", "-c", "1", cam.ip_address.strip()])
        except subprocess.SubprocessError:
            print('cam ' + cam.name + ' didn\'t respond to ping')
            cam.enabled = True
        db_session.commit()
    return Response()


def photo_handler(id):
    cam = active_cameras.get(id)
    if cam is not None:
        cam.save_frame(str(datetime.now()).replace(' ', '-'))
    else:
        print('first play a camera to make a photo')
    return Response()


def pano_handler(id):
    cam = active_cameras.get(id)
    if cam is not None:
        cam.save_frame()
    return Response()

