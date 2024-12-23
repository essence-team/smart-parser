from sqlalchemy import Column, Float, ForeignKey, String
from sqlalchemy.orm import relationship

from .base import Base


class AggregatedPost(Base):
    __tablename__ = "aggregated_posts"

    post_link = Column(String, ForeignKey("posts.post_link"), primary_key=True, nullable=False)
    importance_score = Column(Float, nullable=False)
    cluster_label = Column(String, nullable=False)

    # Отношение к Post
    post = relationship("Post", back_populates="aggregated_posts")
