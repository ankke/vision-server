from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Camera(Base):
    __tablename__ = "cameras"
    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(128))
    url = Column(VARCHAR(128))
    suffix = Column(VARCHAR(128), default=" ")
    ip_address = Column(VARCHAR(128))
    udp_supported = Column(BOOLEAN)
    ptz_app = Column(BOOLEAN)
    enabled = Column(BOOLEAN)
    configurations = relationship("CameraConfiguration", cascade="all,delete")
    sub_streams = relationship("CameraSubStream", cascade="all, delete")


class CameraSubStream(Base):
    __tablename__ = "camera_sub_streams"
    id = Column(INTEGER, primary_key=True)
    camera = Column(
        INTEGER,
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=True,
    )
    sub_stream = Column(VARCHAR(128), default="")


class Configuration(Base):
    __tablename__ = "configurations"
    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(128))
    subnet = Column(VARCHAR(128))
    cameras = relationship("CameraConfiguration", cascade="all,delete")


class CameraConfiguration(Base):
    __tablename__ = "cameras_configurations"
    camera_id = Column(INTEGER, ForeignKey("cameras.id"), primary_key=True)
    configuration_id = Column(
        INTEGER, ForeignKey("configurations.id"), primary_key=True
    )


class Setting(Base):
    __tablename__ = "settings"
    id = Column(INTEGER, primary_key=True)
    path = Column(VARCHAR(256), default="")
    udp_preferred = Column(BOOLEAN, default="true")
