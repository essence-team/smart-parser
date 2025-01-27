from typing import List, Optional

import faiss
import numpy as np
from core.config import main_config
from langchain_community.chat_models.gigachat import GigaChat
from langchain_community.embeddings.gigachat import GigaChatEmbeddings


class QRAG:
    def __init__(self):
        self.index: Optional[faiss.Index] = None
        self.post_texts: List[str] = []
        self.post_clusters: List[int] = []
        self.post_importances: List[float] = []
        self.dim: int = 1024
        self.faiss_index_path = "faiss_index.bin"

        self.query_embedder = GigaChatEmbeddings(credentials=main_config.giga_key, verify_ssl_certs=False)
        self.llm = GigaChat(credentials=main_config.giga_key, model="GigaChat", verify_ssl_certs=False)

    def build_indexes(
        self,
        posts: List[str],
        embeddings: List[List[float]],
        clusters: List[int] = None,
        importances: List[float] = None,
    ) -> None:
        """
        Инициализирует Faiss-индекс и загружает эмбеддинги постов.
        Вызывать один раз — после обновления постов/кластеров.
        """
        if not posts or not embeddings:
            return

        # Метаданные постов
        self.post_texts = posts
        self.post_clusters = clusters if clusters else [0] * len(posts)
        self.post_importances = importances if importances else [0.0] * len(posts)

        embeddings_array = np.array(embeddings).astype(np.float32)

        # Faiss index
        self.index = faiss.IndexFlatL2(self.dim)

        # Если нужно кластерное разбиение в Faiss, можно использовать IVF, но для упрощения – IndexFlat
        # index = faiss.IndexIVFFlat(quantizer, self.dim, nlist, faiss.METRIC_L2)

        # Добавляем в индекс
        self.index.add(embeddings_array)

        faiss.write_index(self.index, self.faiss_index_path)

    def answer_question(
        self, clusters: List[int], digest_text: str, query_history: List[str], user_query: str, top_k: int = 3
    ) -> str:
        """
        Ищет в faiss-индексе топ-K постов из указанных кластеров с учётом эмбеддинга запроса.
        Потом формирует prompt и отправляет в GigaChat.
        """

        if not self.index:
            return "Индекс не построен. Сначала вызовите build_indexes."

        # Эмбеддинг запроса
        query_emb = self.query_embedder.embed_documents([user_query])
        query_vector = np.array(query_emb[0], dtype=np.float32).reshape(1, -1)

        # Поиск соседей в faiss-индексе
        distances, indices = self.index.search(query_vector, k=min(top_k * 3, len(self.post_texts)))
        candidates_idx = indices[0].tolist()

        # Фильтрация постов из нужных кластеров (сортировка по importance_score)
        filtered_posts = []
        for idx, dist in zip(candidates_idx, distances[0]):
            if self.post_clusters[idx] in clusters:
                filtered_posts.append((idx, dist))

        # Сортируем находки по importance_score (по убыванию)
        filtered_posts.sort(key=lambda pair: self.post_importances[pair[0]], reverse=True)
        # Берём топ-K
        top_posts = filtered_posts[:top_k]

        # Префикс для GigaChat
        context_snippets = []
        for idx, _ in top_posts:
            snippet = (
                f"Пост (cluster={self.post_clusters[idx]}, importance={self.post_importances[idx]:.3f}):\n"
                f"{self.post_texts[idx]}\n"
            )
            context_snippets.append(snippet)

        # Добавляем digest_text и историю
        full_context = (
            f"Вот дайджест: {digest_text}\n\n"
            "Ниже релевантные посты:\n\n" + "\n===\n".join(context_snippets) + "\n\n"
            "История предыдущих запросов:\n" + "\n".join(query_history) + "\n\n"
            "Пользователь спрашивает:\n"
            f"{user_query}\n\n"
            "Ответь, ссылаясь только на предоставленные посты. Если информации недостаточно, скажи об этом."
        )

        # Отправка в GigaChat
        from langchain_core.messages import HumanMessage, SystemMessage

        system_message = SystemMessage(
            content=(
                "Ты — помощник, который отвечает строго по контексту. " "Если в текстах нет ответа, сообщи об этом."
            )
        )
        human_message = HumanMessage(content=full_context)
        response = self.llm.invoke([system_message, human_message])
        answer = response.content

        return answer


qrag = QRAG()
