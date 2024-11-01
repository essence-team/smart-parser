import logging

from crud.channel import create_channel, get_channel
from database.db_session_maker import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status
from routers import check_api_key_access
from routers.utils import extract_channel_username
from schemas.channel import ChannelAddRequest, ChannelAddResponse
from services.channel_handler import get_channel_subscribers_count
from services.telethon_client import get_telethon_client
from sqlalchemy.ext.asyncio import AsyncSession

channel_router = APIRouter(prefix="/channel", tags=["channels"])


@channel_router.post(
    "/add",
    status_code=status.HTTP_200_OK,
    response_model=list[ChannelAddResponse],
)
async def add_channels_for_user(
    data: ChannelAddRequest,
    db: AsyncSession = Depends(get_db_session),
    telethon_client=Depends(get_telethon_client),
    api_key=Depends(check_api_key_access),
):
    result = []
    for channel_link in data.channel_links:
        channel_name = extract_channel_username(channel_link)
        channel_info = ChannelAddResponse(channel_link=channel_name, exists=False)
        try:
            # Проверяем, есть ли канал уже в базе данных
            channel = await get_channel(db, channel_link=channel_name)
            if channel:
                channel_info.exists = True
            else:
                # Получаем количество подписчиков через отдельную функцию
                subs_cnt = await get_channel_subscribers_count(telethon_client, channel_name)
                if subs_cnt is not None:
                    # Создаем канал в базе данных
                    await create_channel(db, channel_link=channel_name, subs_cnt=subs_cnt)
                    channel_info.exists = True
        except Exception as e:
            logging.exception(f"Unexpected error processing channel {channel_name}: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

        result.append(channel_info)

    return result
