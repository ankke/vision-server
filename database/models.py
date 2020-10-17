from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), default=" ")
    url = Column(String(100), default=" ")
    suffix = Column(String(40), default=" ")
    ip_address = Column(String(20), default=" ")
    udp_supported = Column(Boolean())
    ptz_app = Column(Boolean())
    enabled = Column(Boolean())
    configurations = relationship("Camera_Configuration", cascade="all,delete")
    sub_streams = relationship("CameraSubStream", cascade="all, delete")


class CameraSubStream(Base):
    __tablename__ = "camera_sub_streams"
    id = Column(Integer, primary_key=True)
    camera = Column(
        Integer,
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=True,
    )
    sub_stream = Column(String(40), default="")


class Configuration(Base):
    __tablename__ = "configurations"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), default=" ")
    cameras = relationship("Camera_Configuration", cascade="all,delete")


class Camera_Configuration(Base):
    __tablename__ = "cameras_configurations"
    camera_id = Column(Integer, ForeignKey("cameras.id"), primary_key=True)
    configuration_id = Column(
        Integer, ForeignKey("configurations.id"), primary_key=True
    )
