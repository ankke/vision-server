import logging
from datetime import datetime

from flask import Response

from video.video import active_cameras

logger = logging.getLogger("root")


def stop_live_feed(id_, sub_stream):
    key = str(id_) + sub_stream
    cam = active_cameras.get(key)
    if cam is not None:
        cam.kill()
        active_cameras.pop(key)
    return Response()


# def refresh_handler():
#     for cam in get_all_cameras():
#         cam.enabled = True
#         try:
#             print(" ".join(["ping", "-c", "1", cam.ip_address.strip()]))
#             subprocess.check_output(["ping", "-c", "1", cam.ip_address.strip()])
#         except subprocess.SubprocessError:
#             print("cam " + cam.name + " didn't respond to ping")
#             cam.enabled = True
#     return Response()


def film_handler(id, sub_stream):
    cam = active_cameras.get(str(id) + sub_stream)
    if cam is not None:
        cam.save_frame(str(datetime.now()).replace(" ", "-"))
    else:
        Response("first play a camera to make a photo")
    return Response()


def photo_handler(id, tag, sub_stream):
    cam = active_cameras.get(str(id) + sub_stream)
    if cam is not None:
        cam.save_frame(tag + "_" + str(datetime.now()).replace(" ", "-"))
    else:
        print("first play a camera to make a photo")
    return Response()


def pano_handler(id, sub_stream):
    cam = active_cameras.get(str(id) + sub_stream)
    if cam is not None:
        cam.save_frame()
    return Response()


def gen(cam):
    while True:
        frame = cam.get_frame_bytes()
        if frame is not None:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
