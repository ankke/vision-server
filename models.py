from sqlalchemy import Column, Integer, String, Boolean

from database import Base


class Camera(Base):
    __tablename__ = 'camera_camera'
    id = Column(Integer, primary_key=True)
    name = Column(String(25), default=' ')
    url = Column(String(100), default=' ')
    sub_stream = Column(String(40), default=' ')
    suffix = Column(String(40), default=' ')
    ip_address = Column(String(20), default=' ')
    udp_supported = Column(Boolean())
    ptz_app = Column(Boolean())
    enabled = Column(Boolean())


class Configuration(Base):
    __tablename__ = 'configurations'
    id = Column(Integer, primary_key=True)
    name = Column(String(25), default=' ')


class Camera_Configuration(Base):
    __tablename__ = 'cameras_configurations'
    camera_id = Column(Integer, primary_key=True)
    configuration_id = Column(Integer, primary_key=True)
