from fastapi import APIRouter, Depends, HTTPException
from routers import check_api_key_access
from services.telethon_client import get_telethon_client
from telethon.errors import ChannelInvalidError, ChannelPrivateError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel

channel_router = APIRouter(prefix="/channels", tags=["channels"])


@channel_router.get("/check/{channel_link}")
async def check_channel(
    channel_link: str,
    telethon_client=Depends(get_telethon_client),
    api_key: str = Depends(check_api_key_access),
):
    try:
        # Получаем базовую информацию о канале
        entity = await telethon_client.get_entity(channel_link)

        if isinstance(entity, Channel):
            # Получаем полную информацию о канале
            full_channel = await telethon_client(GetFullChannelRequest(channel=entity))

            # Извлекаем количество участников
            subscribers_count = full_channel.full_chat.participants_count

            return {"exists": True, "channel_title": entity.title, "subscribers_count": subscribers_count}
        else:
            # Если сущность не является каналом
            return {"exists": False, "detail": "Entity is not a channel"}

    except (ChannelInvalidError, ChannelPrivateError):
        raise HTTPException(status_code=404, detail="Channel not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"exists": False}
