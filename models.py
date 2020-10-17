from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import ARRAY
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
    configurations = relationship("Camera_Configuration", cascade="all,delete")


class Configuration(Base):
    __tablename__ = 'configurations'
    id = Column(Integer, primary_key=True)
    name = Column(String(25), default=' ')
    cameras = relationship("Camera_Configuration", cascade="all,delete")


class Camera_Configuration(Base):
    __tablename__ = 'cameras_configurations'
    camera_id = Column(Integer, ForeignKey('camera_camera.id'), primary_key=True)
    configuration_id = Column(Integer, ForeignKey('configurations.id'), primary_key=True)
