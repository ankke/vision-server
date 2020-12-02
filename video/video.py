import logging
import os
from threading import Thread, RLock, Condition

import cv2

environ_lock = RLock()
active_cameras = {}


class VideoCamera(object):
    def __init__(self, camera):
        self.camera = camera
        self.condition = Condition()
        # self.final_url = self.camera.url + self.camera.sub_stream + self.camera.suffix
        self.final_url = (
            "rtsp://admin:AGHspace@192.168.0.54/cam/realmonitor?channel=1&subtype=0"
        )
        # self.final_url = 0
        self.active = False
        self.video = None
        self.new_frame_available = False
        self.frame = None
        self.live = False
        self.thread = Thread(target=self.update, args=())

    def __del__(self):
        logging.error(
            "closing connection with %s %s" % (self.camera.name, self.final_url)
        )
        if self.video is not None:
            self.video.release()

    def activate(self):
        self.set_capture_options()
        thread = Thread(target=self.connect(), args=())
        logging.error("starting thread for %s %s" % (self.camera.name, self.final_url))
        thread.start()
        thread.join(timeout=30)
        self.live = True
        active_cameras[self.camera.id] = self.camera
        self.thread.start()

    def set_capture_options(self):
        with environ_lock:
            if self.camera.udp_supported:
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
                logging.error(
                    "establishing udp connection for %s %s"
                    % (self.camera.name, self.final_url)
                )
            else:
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
                logging.error(
                    "establishing tcp connection for %s %s"
                    % (self.camera.name, self.final_url)
                )

    def connect(self):
        self.video = cv2.VideoCapture(self.final_url)
        logging.error("connected %s %s" % (self.camera.name, self.final_url))
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 6)
        if self.video is not None:
            self.active = True
            logging.error("SUCCESS %s %s" % (self.camera.name, self.final_url))
        else:
            logging.error("FAILURE %s %s" % (self.camera.name, self.final_url))
            raise ConnectionError

    def update(self):
        while self.live:
            with self.condition:
                if self.new_frame_available:
                    self.condition.wait()
                _, self.frame = self.video.read()
                self.new_frame_available = True
                self.condition.notifyAll()

    def kill(self):
        self.live = False
        self.thread.join()

    def save_frame(self, timestamp):
        logging.error("saving photo_%s" % str(timestamp))
        frame = self.frame
        cv2.imwrite("~/Desktop/photo%s.png" % str(timestamp), frame)

    def get_frame_bytes(self):
        with self.condition:
            if not self.new_frame_available:
                self.condition.wait()
            if self.frame is not None:
                _, jpeg = cv2.imencode(".jpg", self.frame)
                self.new_frame_available = False
                self.condition.notifyAll()
                return jpeg.tobytes()
            return None

    def is_live(self):
        return self.active
