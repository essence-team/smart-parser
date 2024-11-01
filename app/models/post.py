from datetime import datetime, timezone

from models.base import Base
from sqlalchemy import ARRAY, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship


# Модель постов
class Post(Base):
    __tablename__ = "posts"

    post_link = Column(String, primary_key=True, unique=True)
    channel_link = Column(String, ForeignKey("channels.channel_link"), nullable=False)
    title = Column(Text, nullable=True)  # Summarized title
    embedding = Column(ARRAY(Float), nullable=True)
    amount_reactions = Column(Integer, default=0)
    amount_comments = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Связь с таблицей Channels
    channel = relationship("Channel", back_populates="posts")
