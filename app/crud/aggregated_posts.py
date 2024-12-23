from typing import List

from models.aggregated_posts import AggregatedPost
from models.post import Post
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def clear_aggregated_posts(db: AsyncSession) -> None:
    await db.execute(text("DELETE FROM aggregated_posts"))
    await db.commit()


async def add_aggregated_post(
    db: AsyncSession,
    post_link: str,
    importance_score: float,
    cluster_label: str,
) -> AggregatedPost:
    post_data = AggregatedPost(
        post_link=post_link,
        importance_score=importance_score,
        cluster_label=cluster_label,
    )

    db.add(post_data)
    await db.commit()
    await db.refresh(post_data)
    return post_data


async def get_aggregated_posts_by_channel(db: AsyncSession, channel_link: int) -> List[AggregatedPost]:
    result = await db.execute(
        select(AggregatedPost)
        .join(Post, AggregatedPost.post_link == Post.link)
        .filter(Post.channel_link == channel_link)
    )
    return result.scalars().all()
