from models.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


# Модель каналов
class Channel(Base):
    __tablename__ = "channels"

    channel_link = Column(String, primary_key=True, unique=True)
    subs_cnt = Column(Integer, default=0)

    # Связь с таблицей UserChannels и Posts
    user_channels = relationship("UserChannel", back_populates="channel")
    posts = relationship("Post", back_populates="channel")
