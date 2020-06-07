from sqlalchemy.orm.exc import NoResultFound

from database import db_session
from models import Camera


def add_camera(json):
    new_camera = Camera(**json)
    db_session.add(new_camera)
    db_session.commit()


def edit_camera(json):
    db_session.query(Camera).filter_by(id=json["id"]).update(json)
    db_session.commit()


def delete_camera(id):
    try:
        cam = Camera.query.filter_by(id=id).one()
        db_session.delete(cam)
        db_session.commit()
    except NoResultFound:
        print("no camera with id: " + id)
