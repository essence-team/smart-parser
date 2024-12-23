from typing import List

import numpy as np
from core.config import main_config
from langchain_community.embeddings.gigachat import GigaChatEmbeddings


class GigaEmbedder:
    def __init__(self, api_key: str):
        self.embedder = GigaChatEmbeddings(credentials=api_key, verify_ssl_certs=False)

    def get_embeddings(self, texts: str | List[str]) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]

        texts = [text[:512] for text in texts]
        return np.array(self.embedder.embed_documents(texts=texts))


embedder = GigaEmbedder(api_key=main_config.giga_key)
