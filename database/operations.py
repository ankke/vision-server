from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from database.connection import db_session
from database.models import *


def add_camera(json):
    sub_streams = json["sub_streams"]
    json.pop("sub_streams")
    camera = Camera(**json)
    db_session.add(camera)
    db_session.flush()
    for sub_stream in sub_streams:
        db_session.add(CameraSubStream(camera=camera.id, sub_stream=sub_stream))
    db_session.commit()


# raise exception when camera id does not exists
def get_camera_by_id(id):
    return (
        db_session.query(Camera)
            .filter_by(id=id)
            .options(joinedload("sub_streams"))
            .one()
    )


def edit_camera(json):
    try:
        sub_streams = json["sub_streams"]
        json.pop("sub_streams")
        cam = db_session.query(Camera).filter(Camera.id == json["id"]).update(json)
        db_session.commit()
    except NoResultFound:
        print("no camera with id: " + str(json["id"]))


def delete_camera(id):
    try:
        cam = get_camera_by_id(id)
        db_session.delete(cam)
        db_session.commit()
    except NoResultFound:
        print("no camera with id: " + id)


def get_configuration_by_id(id):
    try:
        return db_session.query(Configuration).filter_by(id=id).one()
    except NoResultFound:
        print("no configuration with id: " + id)


def get_cameras_for_configuration(conf_id):
    try:
        cameras_id = (
            db_session.query(Camera_Configuration.camera_id)
                .filter_by(configuration_id=int(conf_id))
                .all()
        )
        cameras = []
        for cam_id in cameras_id:
            cam = get_camera_by_id(cam_id.camera_id)
            cameras.append(cam)
        return cameras
    except NoResultFound:
        print("no configuration with id: " + conf_id)


def add_cameras_to_configuration(configuration, cameras):
    for cam in cameras:
        cam = get_camera_by_id(cam)
        json = {"camera_id": cam.id, "configuration_id": configuration.id}
        cam_conf = Camera_Configuration(**json)
        db_session.add(cam_conf)


def add_configuration(json):
    configuration = Configuration(**json["configuration"])
    db_session.add(configuration)
    db_session.flush()

    try:
        add_cameras_to_configuration(configuration, json["cameras"])
        db_session.commit()
    except NoResultFound:
        print("At least one camera ID is incorrect")
        db_session.rollback()


def edit_configuration(json):
    configuration = json["configuration"]
    cameras = json["cameras"]

    try:
        configuration_to_update = db_session.query(Configuration).filter_by(
            id=configuration["id"]
        )
        configuration_to_update.update(configuration)
        configuration_to_update = configuration_to_update.one()

        command = (
            db_session.query(Camera_Configuration)
                .delete()
                .where(Camera_Configuration.configuration_id == configuration["id"])
        )
        db_session.execute(command)

        add_cameras_to_configuration(configuration_to_update, cameras)
        db_session.commit()
    except NoResultFound:
        print(
            "no configuration with id: "
            + str(configuration["id"])
            + " or at least one camera ID is incorrect"
        )
    pass


def delete_configuration(id):
    configuration = get_configuration_by_id(id)
    if configuration is not None:
        db_session.delete(configuration)
        db_session.commit()


def get_all_cameras():
    cameras = (
        db_session.query(Camera)
            .options(joinedload("sub_streams"))
            .group_by(Camera.id)
            .all()
    )
    result = []
    for camera in cameras:
        result.append(
            {
                "id": camera.id,
                "name": camera.name,
                "url": camera.url,
                "suffix": camera.suffix,
                "ip_address": camera.ip_address,
                "udp_supported": camera.udp_supported,
                "ptz_app": camera.ptz_app,
                "enabled": camera.enabled,
                "sub_streams": list(
                    map(lambda sub: sub.sub_stream, camera.sub_streams)
                ),
            }
        )
    return result


def get_all_configurations():
    return db_session.query(Configuration).all()
