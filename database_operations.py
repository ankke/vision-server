from sqlalchemy.orm.exc import NoResultFound

from database import db_session
from models import Camera, Configuration, Camera_Configuration


def add_camera_to_database(json):
    new_camera = Camera(**json)
    db_session.add(new_camera)
    db_session.commit()
    return new_camera


# raise exception when camera id does not exists
def get_camera_from_database(id):
    return db_session.query(Camera).filter_by(id=id).one()


def edit_camera_in_database(json):
    try:
        cam = db_session.query(Camera).filter_by(id=json["id"])
        cam.one()
        cam.update(json)
        db_session.commit()
    except NoResultFound:
        print("no camera with id: " + str(json["id"]))


def delete_camera_from_database(id):
    try:
        cam = get_camera_from_database(id)
        db_session.delete(cam)
        db_session.commit()
    except NoResultFound:
        print("no camera with id: " + id)


def get_configuration_from_database(id):
    try:
        return db_session.query(Configuration).filter_by(id=id).one()
    except NoResultFound:
        print("no configuration with id: " + id)


def get_cameras_for_configuration(conf_id):
    try:
        cameras_id = db_session.query(Camera_Configuration.camera_id).filter_by(configuration_id=int(conf_id)).all()
        cameras = []
        for cam_id in cameras_id:
            cam = get_camera_from_database(cam_id.camera_id)
            cameras.append(cam)
        return cameras
    except NoResultFound:
        print("no configuration with id: " + conf_id)


def add_cameras_to_configuration(configuration, cameras):
    for cam in cameras:
        cam = get_camera_from_database(cam)
        json = {"camera_id": cam.id, "configuration_id": configuration.id}
        cam_conf = Camera_Configuration(**json)
        db_session.add(cam_conf)


def add_configuration_to_database(json):
    configuration = Configuration(**json["configuration"])
    db_session.add(configuration)
    db_session.flush()

    try:
        add_cameras_to_configuration(configuration, json["cameras"])
        db_session.commit()
    except NoResultFound:
        print("At least one camera ID is incorrect")
        db_session.rollback()


def edit_configuration_in_database(json):
    configuration = json["configuration"]
    cameras = json["cameras"]

    try:
        configuration_to_update = db_session.query(Configuration).filter_by(id=configuration["id"])
        configuration_to_update.update(configuration)
        configuration_to_update = configuration_to_update.one()

        command = Camera_Configuration.__table__.delete().where(Camera_Configuration.configuration_id == configuration["id"])
        db_session.execute(command)

        add_cameras_to_configuration(configuration_to_update, cameras)
        db_session.commit()
    except NoResultFound:
        print("no configuration with id: " + str(configuration["id"]) + " or at least one camera ID is incorrect")
    pass


def delete_configuration_from_database(id):
    configuration = get_configuration_from_database(id)
    if configuration is not None:
        db_session.delete(configuration)
        db_session.commit()
