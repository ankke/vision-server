import base64
import os
from threading import Thread, RLock, Condition

import cv2

environ_lock = RLock()
active_cameras = {}


class VideoCamera(object):
    def __init__(self, camera):
        self.camera = camera
        self.condition = Condition()
        self.final_url = self.camera.url + self.camera.sub_stream + self.camera.suffix
        self.active = False
        self.video = None
        self.new_frame_available = False
        self.connect()
        _, self.frame = self.video.read()
        print("starting thread for %s %s" % (self.camera.name, self.final_url))
        self.live = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()

    def __del__(self):
        print("closing connection with %s %s" % (self.camera.name, self.final_url))
        if self.video is not None:
            self.video.release()

    def save_frame(self, timestamp):
        print("saving photo_%s" % str(timestamp))
        frame = self.frame
        cv2.imwrite("./photos/photo%s.png" % str(timestamp), frame)

    def get_frame(self):
        frame = self.frame
        if frame is not None:
            _, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        return None

    def update(self):
        while self.live:
            _, self.frame = self.video.read()

    def is_live(self):
        return self.active

    def kill(self):
        self.live = False
        self.thread.join()

    def connect(self):
        thread = Thread(target=self.set_udp, args=())
        thread.start()
        thread.join(timeout=60)
        if self.video is not None:
            self.active = True
            print("SUCCESS %s %s" % (self.camera.name, self.final_url))
        else:
            print("FAILURE %s %s" % (self.camera.name, self.final_url))
            raise ConnectionError

    def set_udp(self):
        with environ_lock:
            if self.camera.udp_supported:
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'
                print("establishing udp connection for %s %s" % (self.camera.name, self.final_url))
            else:
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
                print("establishing tcp connection for %s %s" % (self.camera.name, self.final_url))
            self.video = cv2.VideoCapture(self.final_url)
            print("connected %s %s" % (self.camera.name, self.final_url))
            self.video.set(cv2.CAP_PROP_BUFFERSIZE, 6)


class StreamArray(list):
    def __init__(self, cam):
        super().__init__()
        self.cam = cam

    def __iter__(self):
        return gen(self.cam)

    def __len__(self):
        return 1


def gen(cam):
    while True:
        frame = cam.get_frame()
        if frame is not None:
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n'


def encode_in_base64(frame):
    frame = base64.b64encode(frame).decode('utf-8')
    return "data:image/jpeg;base64,{}".format(frame)
