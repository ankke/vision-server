import logging
from datetime import datetime
from time import sleep

from flask import Response
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


def pano_handler(id, tag, sub_stream):
    cam = active_cameras.get(str(id) + sub_stream)

    stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)

    if cam is not None:
        filename = tag + "_pano_" + str(datetime.now()).replace(" ", "-")

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
        i = 1

        for p in photos:
            cv2.imwrite("./photos/%s.png" % str(i), p)
            i += 1

        status, pano = stitcher.stitch(photos)

        if status != cv2.Stitcher_OK:
            print("Can't stitch images, error code = %d" % status)
        else:
            cv2.imwrite("./photos/%s.png" % str(filename), pano)
            print("Stitching completed successfully")
    else:
        print("First play a camera to make a photo")
    return Response()


def gen(cam):
    while True:
        frame = cam.get_frame_bytes()
        if frame is not None:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
