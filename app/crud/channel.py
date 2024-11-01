from typing import List

from models.channel import Channel
from models.user_channel import UserChannel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_channel(session: AsyncSession, channel_link: str) -> Channel | None:
    query = select(Channel).filter(Channel.channel_link == channel_link)
    result = await session.execute(query)
    return result.scalars().first()  # Получаем первый результат или None


async def create_channel(session: AsyncSession, channel_link: str, subs_cnt: int) -> Channel:
    # Проверяем, существует ли уже канал с данным channel_link
    channel = await get_channel(session, channel_link)
    if not channel:
        channel = Channel(channel_link=channel_link, subs_cnt=subs_cnt)
        session.add(channel)
        await session.commit()
        await session.refresh(channel)  # Обновляем объект после добавления
    return channel


async def update_channel_subs_cnt(session: AsyncSession, channel_link: str, new_subs_cnt: int) -> Channel | None:
    # Получаем канал по ссылке
    channel = await get_channel(session, channel_link)
    if channel:
        channel.subs_cnt = new_subs_cnt
        await session.commit()
        await session.refresh(channel)  # Обновляем объект после изменения
    return channel


async def get_all_channels_with_subscribers(session: AsyncSession) -> List[Channel]:
    # Получаем все каналы, на которые подписан хотя бы один пользователь
    query = select(Channel).join(UserChannel).filter(UserChannel.channel_link.isnot(None)).distinct()
    result = await session.execute(query)
    return result.scalars().all()  # Возвращаем все уникальные каналы
