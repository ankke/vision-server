import logging

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from database.connection import db_session
from database.models import *

logger = logging.getLogger("root")


def add_camera(json):
    sub_streams = json["sub_streams"]
    json.pop("sub_streams")
    auth_url = ''
    port = ''
    if json["login"] != '':
        auth_url = f'{json["login"]}:{json["password"]}@'
    else:
        json.pop("login")
    if json["port"] != '':
        port = f':{json["port"]}'
    else:
        json.pop("port")
    if json["ptz_port"] == '':
        json.pop("ptz_port")
    url = f'rtsp://{auth_url}{json["ip_address"]}{port}'
    camera = Camera(**json)

    camera.url = url
    db_session.add(camera)
    db_session.flush()
    for sub_stream in sub_streams:
        db_session.add(CameraSubStream(camera=camera.id, sub_stream=sub_stream))
    db_session.commit()


def get_camera_by_id(id):
    return (
        db_session.query(Camera)
        .filter_by(id=id)
        .options(joinedload("sub_streams"))
        .one()
    )


def edit_camera(json):
    camera = db_session.query(Camera).filter(Camera.id == json["id"]).one()
    sub_streams = json["sub_streams"]
    ss = (
        db_session.query(CameraSubStream)
        .filter(CameraSubStream.camera == camera.id)
        .all()
    )
    for s in ss:
        db_session.delete(s)
    for sub_stream in sub_streams:
        db_session.add(CameraSubStream(camera=camera.id, sub_stream=sub_stream))
    json.pop("sub_streams")
    db_session.query(Camera).filter(Camera.id == json["id"]).update(json)
    db_session.commit()


def delete_camera(id):
    try:
        camera = get_camera_by_id(id)
        db_session.delete(camera)
        db_session.commit()
    except NoResultFound:
        logger.info("no camera with id: " + id)


def get_configuration_by_id(id):
    return db_session.query(Configuration).filter_by(id=id).one()


def get_cameras_for_configuration(configuration_id):
    cameras = (
        db_session.query(Camera)
        .join(CameraConfiguration)
        .filter(CameraConfiguration.configuration_id == configuration_id)
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
                "ptz": camera.ptz,
                "enabled": camera.enabled,
                "sub_streams": list(
                    map(lambda sub: sub.sub_stream, camera.sub_streams)
                ),
            }
        )
    return result


def add_configuration(json):
    cameras = json["cameras"]
    json.pop("cameras")
    configuration = Configuration(**json)
    db_session.add(configuration)
    db_session.flush()
    for camera in cameras:
        db_session.add(
            CameraConfiguration(camera_id=camera, configuration_id=configuration.id)
        )
    db_session.commit()


def edit_configuration(json):
    cameras = json["cameras"]
    json.pop("cameras")
    configuration = (
        db_session.query(Configuration).filter(Configuration.id == json["id"]).one()
    )
    cc = (
        db_session.query(CameraConfiguration)
        .filter(CameraConfiguration.configuration_id == configuration.id)
        .all()
    )
    for c in cc:
        db_session.delete(c)
    for camera in cameras:
        db_session.add(
            CameraConfiguration(camera_id=camera, configuration_id=configuration.id)
        )
    db_session.query(Configuration).filter(Configuration.id == json["id"]).update(json)
    db_session.commit()


def delete_configuration(id):
    configuration = get_configuration_by_id(id)
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
                "ptz": camera.ptz,
                "enabled": camera.enabled,
                "sub_streams": list(
                    map(lambda sub: sub.sub_stream, camera.sub_streams)
                ),
            }
        )
    return result


def get_all_configurations():
    configurations = (
        db_session.query(Configuration)
        .options(joinedload("cameras"))
        .group_by(Configuration.id)
        .all()
    )
    result = []
    for configuration in configurations:
        result.append(
            {
                "id": configuration.id,
                "name": configuration.name,
                "subnet": configuration.subnet,
                "cameras": list(map(lambda cam: cam.camera_id, configuration.cameras)),
            }
        )
    return result


def get_settings():
    return db_session.query(Setting).one()


def update_settings(json):
    logger.debug(json)
    settings = db_session.query(Setting).first()
    settings.path = json["path"]
    settings.udp_preferred = json["udp_preferred"]
    db_session.commit()


def create_settings(json):
    settings = Setting(path=json["path"], udp_preferred=json["udp_preferred"])
    db_session.add(settings)
    db_session.commit()
