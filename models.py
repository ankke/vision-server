from sqlalchemy import Column, Integer, String, Boolean

from database import Base


class Camera(Base):
    __tablename__ = 'cameras'
    id = Column(Integer, primary_key=True)
    name = Column(String(25), default=' ')
    url = Column(String(100), default=' ')
    sub_stream = Column(String(40), default=' ')
    suffix = Column(String(40), default=' ')
    ip_address = Column(String(20), default=' ')
    udp_supported = Column(Boolean())
    ptz_app = Column(Boolean())
    enabled = Column(Boolean())
