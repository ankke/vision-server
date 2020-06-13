import simplejson

from flask import Flask
import cv2
from database import query_db, close_db
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/cameras')
def get_cameras():
    result = simplejson.dumps(query_db('select * from camera_camera'))
    close_db()
    return result


@socketio.on('connected')
def play():
    print("cinne")
    emit('my response', {'data': 'Connected'})
    # print('connected')
    # video = cv2.VideoCapture("rtsp://admin:AGHspace@192.168.0.54/cam/realmonitor?channel=1&subtype=0")
    # _, frame = video.read()
    # while video.isOpened():
    #     emit('frame', frame)


if __name__ == '__main__':
    # from gevent import pywsgi
    # from geventwebsocket.handler import WebSocketHandler
    #
    # server = pywsgi.WSGIServer(('', 8000), app, handler_class=WebSocketHandler)
    # print("Server listening on: http://localhost:" + str(8000))
    # server.serve_forever()
    socketio.run(app,debug=True)