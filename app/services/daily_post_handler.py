import asyncio
import logging
from datetime import datetime, timedelta, timezone

from crud.channel import get_all_channels_with_subscribers, update_channel_subs_cnt
from crud.post import create_post, delete_old_posts, get_posts_by_channel, update_post
from database.db_session_maker import database
from services.aggregator import Aggregator
from services.channel_handler import get_channel_subscribers_count
from services.embedder import embedder
from services.telethon_client import TelethonClient
from services.title_composer import summarizer
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.errors import FloodWaitError
from telethon.types import Message


class DailyPostHandler:
    def __init__(self, telethon_client: TelethonClient, days_to_keep: int = 31):
        self.tg_client = telethon_client.client
        self.logger = logging.getLogger(__name__)
        self.days_to_keep = days_to_keep

    async def delete_old_posts(self, session: AsyncSession):
        deleted_count = await delete_old_posts(session, self.days_to_keep)
        print(f"Deleted {deleted_count} posts older than {self.days_to_keep} days")

    async def update_and_fetch_posts(self, session: AsyncSession, channels: list):
        date_to_keep_from = datetime.now(tz=timezone.utc) - timedelta(days=self.days_to_keep)

        for channel in channels:
            print(f"Processing channel: {channel.channel_link}")

            subs_count = await get_channel_subscribers_count(self.tg_client, channel.channel_link)
            await update_channel_subs_cnt(session, channel.channel_link, subs_count)
            print(f"Updated subscriber count for channel {channel.channel_link} to {subs_count}")

            try:
                # Fetch all messages in one API call within the date range
                messages = await self._fetch_messages(channel.channel_link, date_to_keep_from)
                print(f"Fetched {len(messages)} messages from Telegram for channel {channel.channel_link}")

                # Get all existing posts from the database for this channel within the date range
                existing_posts = await get_posts_by_channel(session=session, channel_link=channel.channel_link)
                existing_post_links = set(post.post_link for post in existing_posts)
                print(f"Found {len(existing_posts)} existing posts in the database for channel {channel.channel_link}")

                for message in messages:
                    post_link = f"t.me/{channel.channel_link}/{message.id}"
                    if len(message.text) < 300:
                        continue
                    if post_link in existing_post_links:
                        amount_reactions = await self.get_reactions(message)
                        amount_comments = await self.get_comments(message)
                        await update_post(
                            session,
                            post_link=post_link,
                            amount_reactions=amount_reactions,
                            amount_comments=amount_comments,
                        )
                    else:
                        # Create a new post
                        summary = summarizer.summarize(message.text) if message.text else "No Title"
                        embedding = embedder.get_embeddings(summary)  # TODO: раскоментить для прода
                        await create_post(
                            session=session,
                            post_link=post_link,
                            channel_link=channel.channel_link,
                            title=summary,
                            published_at=message.date,
                            amount_reactions=await self.get_reactions(message),
                            amount_comments=await self.get_comments(message),
                            embedding=embedding,  # TODO: поменять на embedder
                            text=message.text,  # TODO: убрать для продакшена
                        )
                print(f"Processed messages for channel {channel.channel_link}")
            except FloodWaitError as e:
                print(f"Flood wait error for {channel.channel_link}: {e}")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"Error processing channel {channel.channel_link}: {e}")

        await session.commit()
        print("All posts updated and new posts fetched")

    async def _fetch_messages(self, channel_link: str, date_to_keep_from: datetime):
        messages = []
        try:
            # Fetch messages using iter_messages and collect them into a list
            async for message in self.tg_client.iter_messages(
                channel_link,
                reverse=True,
                offset_date=date_to_keep_from,
            ):
                messages.append(message)
        except Exception as e:
            print(f"Error fetching messages for {channel_link}: {e}")
        return messages

    async def collect_channels(self, session: AsyncSession):
        channels = await get_all_channels_with_subscribers(session)
        print(f"Collected {len(channels)} channels with subscribers")
        return channels

    async def get_reactions(self, message: Message) -> int:
        if message.reactions:
            return sum(reaction.count for reaction in message.reactions.results)
        return 0

    async def get_comments(self, message: Message) -> int:
        if message.replies:
            return message.replies.replies
        return 0

    async def run_daily_tasks(self):
        async with database.get_session() as session:
            await self.delete_old_posts(session)
            channels = await self.collect_channels(session)
            await self.update_and_fetch_posts(session, channels)
            aggregator = Aggregator(session)
            await aggregator.compute_and_store_importance_scores()  # TODO: раскоментить для прода
        print("Daily tasks completed")
