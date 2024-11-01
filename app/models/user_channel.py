from models.base import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship


# Модель каналов пользователя
class UserChannel(Base):
    __tablename__ = "user_channels"

    user_id = Column(String(30), ForeignKey("users.user_id"), primary_key=True)
    channel_link = Column(String, ForeignKey("channels.channel_link"), primary_key=True)

    # Связь с таблицами Users и Channels
    user = relationship("User", back_populates="user_channels")
    channel = relationship("Channel", back_populates="user_channels")
