import logging
from datetime import datetime
from time import sleep

from flask import Response, jsonify
import cv2

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
    print(cam)
    if cam is not None:
        cam.save_frame(tag + "_" + str(datetime.now()).replace(" ", "-"))
    else:
        print("first play a camera to make a photo")
    return Response()


def pano_handler(id, tag, sub_stream, rot_value):
    cam = active_cameras.get(str(id) + sub_stream)
    if cam is None:
        return 404

    if rot_value % 2 == 1:
        photos = pano_vertical(cam)
    else:
        photos = pano_horizontal(cam)

    stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)

    filename = tag + "_pano_" + str(datetime.now()).replace(" ", "-")

    status, pano = stitcher.stitch(photos)

    if status != cv2.Stitcher_OK:
        return jsonify("Can't stitch images, error code = %d" % status), 537
    else:
        cv2.imwrite("./photos/%s.png" % str(filename), pano)
        print("Stitching completed successfully")
    return Response()


def pano_horizontal(cam):
    photos = []
    cam.ptzcam.move_left(0.5)
    sleep(2)
    photos.append(cam.frame)
    sleep(2)
    cam.ptzcam.move_right(0.5)
    sleep(2)
    photos.append(cam.frame)
    sleep(2)
    cam.ptzcam.move_right(0.5)
    sleep(2)
    photos.append(cam.frame)
    sleep(2)
    cam.ptzcam.move_left(0.5)
    return photos


def pano_vertical(cam):
    photos = []
    cam.ptzcam.move_up(0.5)
    sleep(2)
    photos.append(cv2.rotate(cam.frame, cv2.ROTATE_90_CLOCKWISE))
    sleep(2)
    cam.ptzcam.move_down(0.5)
    sleep(2)
    photos.append(cv2.rotate(cam.frame, cv2.ROTATE_90_CLOCKWISE))
    sleep(2)
    cam.ptzcam.move_down(0.5)
    sleep(2)
    photos.append(cv2.rotate(cam.frame, cv2.ROTATE_90_CLOCKWISE))
    sleep(2)
    cam.ptzcam.move_up(0.5)
    return photos


def gen(cam):
    while True:
        frame = cam.get_frame_bytes()
        if frame is not None:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
