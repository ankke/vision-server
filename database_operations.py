from sqlalchemy.orm.exc import NoResultFound

from database import db_session
from models import Camera, Configuration, Camera_Configuration


def add_camera(json):
    new_camera = Camera(**json)
    db_session.add(new_camera)
    db_session.commit()


def edit_camera(json):
    db_session.query(Camera).filter_by(id=json["id"]).update(json)
    db_session.commit()


def delete_camera(id):
    try:
        cam = db_session.query(Camera).filter_by(id=id).one()
        db_session.delete(cam)
        db_session.commit()
    except NoResultFound:
        print("no camera with id: " + id)


def get_configuration(id):
    try:
        conf = db_session.query(Configuration).filter_by(id=id).one()
        return conf
    except NoResultFound:
        print("no configuration with id: " + id)


def get_cameras_for_configuration(conf_id):
    try:
        cameras_id = db_session.query(Camera_Configuration.camera_id).filter_by(configuration_id=int(conf_id)).all()
        cameras = []
        for cam_id in cameras_id:
            cam = db_session.query(Camera).filter_by(id=cam_id.camera_id).one()
            cameras.append(cam)
        return cameras
    except NoResultFound:
        print("no configuration with id: " + conf_id)
