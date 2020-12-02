from datetime import datetime

from flask import Response

from database.dao import get_camera_by_id
from video.video import active_cameras, VideoCamera


def live_feed(id):
    camera = get_camera_by_id(id)

    try:
        camera = VideoCamera(camera)
        active_cameras[id] = camera
        return gen(camera)

        # return Response(gen(camera), content_type="multipart/x-mixed-replace;boundary=frame")
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

def film_handler(id):
    cam = active_cameras.get(id)
    if cam is not None:
        cam.save_frame(str(datetime.now()).replace(" ", "-"))
    else:
        Response("first play a camera to make a photo")
    return Response()

def photo_handler(id):
    cam = active_cameras.get(id)
    if cam is not None:
        cam.save_frame(str(datetime.now()).replace(" ", "-"))
    else:
        Response("first play a camera to make a photo")
    return Response()


def pano_handler(id):
    cam = active_cameras.get(id)
    if cam is not None:
        cam.save_frame()
    return Response()


def gen(cam):
    while True:
        frame = cam.get_frame_bytes()
        if frame is not None:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
