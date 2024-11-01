# authenticate.py
import asyncio

from telethon import TelegramClient


async def main():
    phone_number = input("Enter your phone number: ")
    api_id = input("Enter your API ID: ")
    api_hash = input("Enter your API hash: ")
    session_name = "fastapi_telethon_session"

    client = TelegramClient(session_name, api_id, api_hash)
    await client.start(phone=phone_number)

    print("Client connected and authenticated.")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
