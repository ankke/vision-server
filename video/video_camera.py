import logging
import os
from threading import Thread, RLock, Condition
from time import sleep

import cv2

from database.dao import get_settings
from video.ptz import PTZ

environ_lock = RLock()
active_cameras = {}
logger = logging.getLogger("root")


class VideoCamera(object):
    def __init__(self, camera, sub_stream):
        self.camera = camera
        self.sub_stream = sub_stream
        self.condition = Condition()
        self.final_url = self.camera.url + sub_stream + self.camera.suffix
        self.active = False
        self.video = None
        self.new_frame_available = False
        self.frame = None
        self.live = False
        self.thread = Thread(target=self.update)
        self.file_writer = None
        self.saving = False
        self.thread_write = Thread(target=self.save_video)
        if camera.ptz:
            try:
                self.ptz_cam = PTZ(
                    self.camera.ip_address,
                    login=self.camera.login,
                    password=self.camera.password,
                    port=self.camera.port,
                )
            except:
                pass
        else:
            self.ptz_cam = None

    def activate(self):
        logger.debug("activate")
        self.set_capture_options()
        thread = Thread(target=self.connect())
        thread.start()
        thread.join(timeout=30)
        self.live = True
        active_cameras[str(self.camera.id) + self.sub_stream] = self
        logger.debug("starting thread for %s %s" % (self.camera.name, self.final_url))
        self.thread.start()

    def set_capture_options(self):
        settings = get_settings()
        with environ_lock:
            if self.camera.udp_supported and settings.udp_preferred:
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
                logger.debug(
                    "establishing udp connection for %s %s"
                    % (self.camera.name, self.final_url)
                )
            else:
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
                logger.debug(
                    "establishing tcp connection for %s %s"
                    % (self.camera.name, self.final_url)
                )

    def connect(self):
        self.video = cv2.VideoCapture(self.final_url)
        logger.debug("connected %s %s" % (self.camera.name, self.final_url))
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 6)
        if self.video is not None:
            self.active = True
            logger.debug("SUCCESS %s %s" % (self.camera.name, self.final_url))
        else:
            logger.debug("FAILURE %s %s" % (self.camera.name, self.final_url))
            raise ConnectionError

    def update(self):
        while self.live:
            # synchronised version does not work with UDP
            # with self.condition:
            #     if self.new_frame_available:
            #         self.condition.wait()
            sleep(0)
            _, self.frame = self.video.read()
            self.new_frame_available = True
            # self.condition.notifyAll()

    def deactivate(self):
        self.live = False
        self.thread.join()
        logger.debug(
            "closing connection with %s %s" % (self.camera.name, self.final_url)
        )
        if self.video is not None:
            self.video.release()

    def save_frame(self, timestamp):
        logger.debug("saving photo_%s" % str(timestamp))
        frame = self.frame
        cv2.imwrite("./photos/%s.png" % str(timestamp), frame)

    def get_frame_bytes(self):
        # synchronised version does not work with UDP
        # with self.condition:
        #     if not self.new_frame_available:
        #         self.condition.wait()
        if self.frame is not None:
            sleep(0)
            _, jpeg = cv2.imencode(".jpg", self.frame)
            self.new_frame_available = False
            return jpeg.tobytes()
        return None

    def is_live(self):
        return self.active

    def save_video(self):
        while self.saving:
            self.file_writer.write(self.frame)

    def start_recording(self, filename):
        self.saving = True
        frame_width = int(self.video.get(3))
        frame_height = int(self.video.get(4))

        size = (frame_width, frame_height)

        self.file_writer = cv2.VideoWriter(
            "{}.avi".format(filename), cv2.VideoWriter_fourcc(*"MJPG"), 30.0, size
        )
        self.thread_write.start()

    def stop_recording(self):
        self.saving = False
        self.thread_write.join()
        if self.file_writer is not None:
            self.file_writer.release()
