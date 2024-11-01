from core.config import main_config
from telethon import TelegramClient

telethon_cfg = main_config.telethon


class TelethonClient:
    def __init__(self):
        self.client = TelegramClient(telethon_cfg.session_name, telethon_cfg.api_id, telethon_cfg.api_hash)

    async def connect(self):
        await self.client.start(phone=telethon_cfg.phone_number)
        print("Telethon client connected as user")

    async def disconnect(self):
        await self.client.disconnect()
        print("Telethon client disconnected")

    async def get_entity_safe(self, channel_link: str):
        try:
            entity = await self.client.get_entity(channel_link)
            return entity
        except Exception as e:
            print(f"Error getting entity for {channel_link}: {e}")
            return None


client_instance = TelethonClient()


# Dependency
async def get_telethon_client():
    return client_instance.client
