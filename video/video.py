import logging
import os
from threading import Thread, RLock, Condition

import cv2

environ_lock = RLock()
active_cameras = {}
logger = logging.getLogger("root")


class VideoCamera(object):
    def __init__(self, camera, sub_stream):
        self.camera = camera
        self.sub_stream = sub_stream
        self.condition = Condition()
        self.final_url = self.camera.url + sub_stream + self.camera.suffix
        # self.url = (
        #     "rtsp://admin:AGHspace@192.168.0.54/cam/realmonitor?channel=1&subtype=0"
        # )
        self.active = False
        self.video = None
        self.new_frame_available = False
        self.frame = None
        self.live = False
        self.thread = Thread(target=self.update, args=())


    def activate(self):
        self.set_capture_options()
        thread = Thread(target=self.connect(), args=())
        thread.start()
        thread.join(timeout=30)
        self.live = True
        active_cameras[str(self.camera.id) + self.sub_stream] = self
        logger.debug("starting thread for %s %s" % (self.camera.name, self.final_url))
        self.thread.start()

    def set_capture_options(self):
        with environ_lock:
            if self.camera.udp_supported:
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
            # with self.condition:
            #     if self.new_frame_available:
            #         self.condition.wait()
            _, self.frame = self.video.read()
            self.new_frame_available = True
                # self.condition.notifyAll()

    def kill(self):
        self.live = False
        self.thread.join()
        print(
            "closing connection with %s %s" % (self.camera.name, self.final_url)
        )
        if self.video is not None:
            self.video.release()

    def save_frame(self, timestamp):
        logger.debug("saving photo_%s" % str(timestamp))
        frame = self.frame
        cv2.imwrite("./photos/%s.png" % str(timestamp), frame)

    def get_frame_bytes(self):
        # with self.condition:
        #     if not self.new_frame_available:
        #         self.condition.wait()
        if self.frame is not None:
            _, jpeg = cv2.imencode(".jpg", self.frame)
            self.new_frame_available = False
            return jpeg.tobytes()
        return None

    def is_live(self):
        return self.active
