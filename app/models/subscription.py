from datetime import datetime, timedelta, timezone

from models.base import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


# Модель подписки
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(30), ForeignKey("users.user_id"), nullable=False, index=True)
    start_sub = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    end_sub = Column(DateTime(timezone=True), nullable=False)  # Поле теперь всегда заполняется
    is_active = Column(Boolean, default=True)  # Флаг активности подписки
    duration_days = Column(Integer, nullable=False)  # Продолжительность подписки в днях

    # Связь с таблицей Users
    user = relationship("User", back_populates="subscriptions")

    def __init__(self, id: str, user_id: int, duration_days: int):
        self.id = id
        self.user_id = user_id
        self.start_sub = datetime.now(timezone.utc)
        self.end_sub = self.start_sub + timedelta(days=duration_days)
        self.is_active = True
        self.duration_days = duration_days

    def deactivate(self):
        """Метод для завершения подписки"""
        self.is_active = False

    def days_remaining(self):
        """Метод для получения количества оставшихся дней подписки, включая сегодняшний день"""
        if self.is_active:
            delta = self.end_sub - datetime.now(timezone.utc)
            return max(delta.days + 1, 0)  # Добавляем 1 день, чтобы включить сегодняшний день
        return 0

    def extend_subscription(self, extra_days: int):
        """Метод для продления подписки"""
        if self.is_active:
            self.end_sub += timedelta(days=extra_days)
        else:
            self.start_sub = datetime.now(timezone.utc)
            self.end_sub = self.start_sub + timedelta(days=extra_days)
            self.is_active = True
