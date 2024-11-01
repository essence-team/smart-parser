from typing import List

from models.channel import Channel
from models.user_channel import UserChannel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_all_channels_with_subscribers(session: AsyncSession) -> List[Channel]:
    # Получаем все каналы, на которые подписан хотя бы один пользователь
    query = select(Channel).join(UserChannel).filter(UserChannel.channel_link.isnot(None)).distinct()
    result = await session.execute(query)
    return result.scalars().all()  # Возвращаем все уникальные каналы
