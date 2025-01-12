from typing import List


class QRAG:
    def __init__(self):
        pass

    def build_indexes(self, posts: List[str], embeddings: List[List[float]]):
        pass

    def answer_question(
        self,
        clusters: List[int],
        digest_text: str,
        query_history: List[str],
    ) -> str:

        return "Lorem Ipsum"


qrag = QRAG()
