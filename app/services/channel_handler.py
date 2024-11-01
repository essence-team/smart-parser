import logging

from fastapi import HTTPException
from telethon.errors import ChannelInvalidError, ChannelPrivateError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel

logger = logging.getLogger(__name__)


# Вынесенная функция для получения количества подписчиков канала
async def get_channel_subscribers_count(telethon_client, channel_name: str) -> int:
    try:
        entity = await telethon_client.get_entity(channel_name)
        if isinstance(entity, Channel):
            full_channel = await telethon_client(GetFullChannelRequest(channel=entity))
            return full_channel.full_chat.participants_count
    except (ChannelInvalidError, ChannelPrivateError, ValueError):
        return None
    except Exception as e:
        logger.exception(f"Unexpected error getting subscribers count for channel {channel_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
