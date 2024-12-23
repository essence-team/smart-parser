from collections import Counter
from typing import Dict, List

import numpy as np
from crud.aggregated_posts import add_aggregated_post, clear_aggregated_posts
from crud.post import get_all_posts
from models.post import Post
from sklearn.cluster import AgglomerativeClustering
from sqlalchemy.ext.asyncio import AsyncSession


class Aggregator:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def compute_and_store_importance_scores(self) -> None:
        # Получаем все посты для оценки
        all_posts = await self._get_posts_data()

        if not all_posts:
            return

        # Выполняем кластеризацию постов
        self._perform_clustering(all_posts)

        # Вычисляем оценки важности для постов
        self._calculate_importance_scores(all_posts)

        # Очищаем текущие данные и сохраняем новые результаты
        await self._store_importance_scores(all_posts)

    async def _get_posts_data(self) -> List[Dict]:
        posts: List[Post] = await get_all_posts(self.session)
        if not posts:
            return []

        all_posts = []
        for post in posts:
            channel = post.channel

            subscribers = channel.subs_cnt or 0
            post_data = {
                "post": post,
                "embedding": post.embedding,
                "reactions": post.amount_reactions or 0,
                "comments": post.amount_comments or 0,
                "publication_date": post.published_at,
                "channel": channel,
                "subscribers": subscribers,
            }
            all_posts.append(post_data)

        return all_posts

    def _perform_clustering(self, all_posts: List[Dict]) -> None:
        embeddings = np.array([post_data["embedding"] for post_data in all_posts]).reshape(-1, 1024)

        # Кластеризация с помощью DBSCAN
        clustering = AgglomerativeClustering(
            metric="cosine",
            linkage="average",
            distance_threshold=0.11,
            n_clusters=None,
        ).fit(embeddings)
        cluster_labels = clustering.labels_

        # Добавляем метки кластеров к постам
        for idx, post_data in enumerate(all_posts):
            post_data["cluster_label"] = cluster_labels[idx]

    def _calculate_importance_scores(self, all_posts: List[Dict]) -> None:
        cluster_labels = [post_data["cluster_label"] for post_data in all_posts]
        cluster_counts = Counter(cluster_labels)

        # Получаем даты публикации
        publication_dates = [post_data["publication_date"] for post_data in all_posts]
        earliest_publication_date = min(publication_dates)
        latest_publication_date = max(publication_dates)
        total_time_range = (latest_publication_date - earliest_publication_date).total_seconds() or 1

        # Инициализация списков метрик
        cluster_importances = []
        engagement_scores = []
        recency_scores = []

        for post_data in all_posts:
            cluster_label = post_data["cluster_label"]
            cluster_size = cluster_counts[cluster_label]

            # Важность кластера пропорциональна его размеру
            cluster_importance = cluster_size
            cluster_importances.append(cluster_importance)

            # Вовлеченность, нормализованная на подписчиков
            engagement = post_data["reactions"] + post_data["comments"]
            subscribers = post_data["subscribers"]
            engagement_norm = np.log1p(engagement)
            subscribers_norm = np.log1p(subscribers)
            engagement_score = engagement_norm / subscribers_norm if subscribers_norm > 0 else 0
            engagement_scores.append(engagement_score)

            # Оценка новизны
            recency_seconds = (post_data["publication_date"] - earliest_publication_date).total_seconds()
            recency_score = recency_seconds / total_time_range
            recency_scores.append(recency_score)

        # Нормализация метрик
        cluster_importances_norm = self._normalize_metric(cluster_importances)
        engagement_scores_norm = self._normalize_metric(engagement_scores)
        recency_scores_norm = self._normalize_metric(recency_scores)

        # Весовые коэффициенты
        w_cluster = 1 / 3
        w_engagement = 1 / 3
        w_recency = 1 / 3

        # Вычисление итоговой оценки важности
        for idx, post_data in enumerate(all_posts):
            importance_score = (
                w_cluster * cluster_importances_norm[idx]
                + w_engagement * engagement_scores_norm[idx]
                + w_recency * recency_scores_norm[idx]
            )
            post_data["importance_score"] = importance_score

    def _normalize_metric(self, metric_array: List[float]) -> np.ndarray:
        metric_array = np.array(metric_array)
        min_val = metric_array.min()
        max_val = metric_array.max()
        if max_val > min_val:
            normalized = (metric_array - min_val) / (max_val - min_val)
        else:
            normalized = np.zeros_like(metric_array)
        return normalized

    async def _store_importance_scores(self, all_posts: List[Dict]) -> None:
        # Очищаем текущие данные по агрегированным постам
        await clear_aggregated_posts(self.session)

        # Пакетное добавление постов для повышения производительности
        for post_data in all_posts:
            await add_aggregated_post(
                db=self.session,
                post_link=post_data["post"].post_link,
                importance_score=post_data["importance_score"],
                cluster_label=str(post_data["cluster_label"]),
            )
        # Асинхронное выполнение добавления постов
        # await asyncio.gather(*tasks)
