import logging
from datetime import datetime
from time import sleep

from flask import Response, jsonify
import cv2

from video.video_camera import active_cameras

logger = logging.getLogger("root")


def stop_live_feed(id_, sub_stream):
    key = str(id_) + sub_stream
    cam = active_cameras.get(key)
    if cam is not None:
        cam.deactivate()
        active_cameras.pop(key)
    return Response()


# not used
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


def start_recording_handler(id_, tag, sub_stream):
    cam = active_cameras.get(str(id_) + sub_stream)
    if cam is not None:
        filename = tag + "_video_" + str(datetime.now()).replace(" ", "-")
        cam.start_recording("./photos/%s" % str(filename))
    else:
        Response("first play a camera to record a video")
    return Response()


def stop_recording_handler(id_, sub_stream):
    logger.debug("stop recording")
    cam = active_cameras.get(str(id_) + sub_stream)
    if cam is not None:
        cam.stop_recording()
    return Response()


def photo_handler(id_, tag, sub_stream):
    cam = active_cameras.get(str(id_) + sub_stream)
    logger.debug(f"taking photo for {cam}")
    if cam is not None:
        cam.save_frame(tag + "_" + str(datetime.now()).replace(" ", "-"))
    else:
        logger.debug("first play a camera to take a photo")
    return Response()


def pano_handler(id_, tag, sub_stream, rot_value):
    cam = active_cameras.get(str(id_) + sub_stream)

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
        logger.debug("Stitching completed successfully")
    return Response()


def pano_horizontal(cam):
    photos = []
    cam.ptz_cam.move_left(0.5)
    sleep(4)
    photos.append(cam.frame)
    sleep(2)
    cam.ptz_cam.move_right(0.5)
    sleep(4)
    photos.append(cam.frame)
    sleep(2)
    cam.ptz_cam.move_right(0.5)
    sleep(4)
    photos.append(cam.frame)
    sleep(2)
    cam.ptz_cam.move_left(0.5)
    i = 0
    for p in photos:
        cv2.imwrite("./photos/%s.png" % str(i), p)
        i += 1
    return photos


def pano_vertical(cam):
    photos = []
    cam.ptz_cam.move_up(0.5)
    sleep(2)
    photos.append(cv2.rotate(cam.frame, cv2.ROTATE_90_CLOCKWISE))
    sleep(2)
    cam.ptz_cam.move_down(0.5)
    sleep(2)
    photos.append(cv2.rotate(cam.frame, cv2.ROTATE_90_CLOCKWISE))
    sleep(2)
    cam.ptz_cam.move_down(0.5)
    sleep(2)
    photos.append(cv2.rotate(cam.frame, cv2.ROTATE_90_CLOCKWISE))
    sleep(2)
    cam.ptz_cam.move_up(0.5)
    return photos


def stream(camera):
    while True:
        frame = camera.get_frame_bytes()
        if frame is not None:
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
