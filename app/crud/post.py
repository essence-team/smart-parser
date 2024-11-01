# crud/crud_post.py
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from models.post import Post
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def create_post(
    session: AsyncSession,
    post_link: str,
    channel_link: str,
    title: Optional[str] = None,
    embedding: Optional[List[float]] = None,
    amount_reactions: int = 0,
    amount_comments: int = 0,
    published_at: Optional[datetime] = None,
) -> Post:
    post = Post(
        post_link=post_link,
        channel_link=channel_link,
        title=title,
        embedding=embedding,
        amount_reactions=amount_reactions,
        amount_comments=amount_comments,
        published_at=published_at,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


async def get_post_by_link(session: AsyncSession, post_link: str):
    result = await session.execute(select(Post).where(Post.post_link == post_link))
    return result.scalar_one_or_none()


async def get_all_posts(session: AsyncSession, days_to_keep: int) -> List[Post]:
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
    query = select(Post).where(Post.published_at >= cutoff_date)
    result = await session.execute(query)
    return result.scalars().all()


async def update_post(
    session: AsyncSession,
    post_link: str,
    title: Optional[str] = None,
    embedding: Optional[List[float]] = None,
    amount_reactions: Optional[int] = None,
    amount_comments: Optional[int] = None,
    published_at: Optional[datetime] = None,
) -> Optional[Post]:
    """
    Обновляет данные поста с использованием метода `update()`.
    """
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if embedding is not None:
        update_data["embedding"] = embedding
    if amount_reactions is not None:
        update_data["amount_reactions"] = amount_reactions
    if amount_comments is not None:
        update_data["amount_comments"] = amount_comments
    if published_at is not None:
        update_data["published_at"] = published_at

    if not update_data:
        # Нет данных для обновления
        return await get_post_by_link(session, post_link)

    stmt = update(Post).where(Post.post_link == post_link).values(**update_data).returning(Post)
    result = await session.execute(stmt)
    updated_post = result.scalars().first()

    if updated_post:
        await session.commit()
        await session.refresh(updated_post)

    return updated_post


async def delete_old_posts(session: AsyncSession, days_to_keep: int) -> int:
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
    stmt = delete(Post).where(Post.published_at < cutoff_date)
    result = await session.execute(stmt)
    await session.commit()

    # Возвращаем количество удалённых строк
    return result.rowcount


async def get_latest_post_by_channel(session: AsyncSession, channel_link: str) -> Optional[Post]:
    query = select(Post).where(Post.channel_link == channel_link).order_by(Post.published_at.desc()).limit(1)
    result = await session.execute(query)
    return result.scalars().first()


# In crud/post.py, add this function
async def get_posts_by_channel(session, channel_link):
    result = await session.execute(select(Post).where(Post.channel_link == channel_link))
    return result.scalars().all()
