from core.config import main_config
from langchain_community.chat_models.gigachat import GigaChat


class GigaSummarizer:
    def __init__(self, api_key: str):
        self.chat_model = GigaChat(credentials=api_key, model="GigaChat", timeout=30, verify_ssl_certs=False)

    def summarize(self, text: str) -> str:
        from langchain_core.messages import HumanMessage, SystemMessage

        messages = [
            SystemMessage(
                content=(
                    "На входе — список телеграм-постов на любую тему (политика, финансы, ИИ, и т.д.). "
                    "Для каждого поста сформируйте однопредложное и максимально точное описание, которое:\n\n"
                    "1. Отражает уникальный инфоповод или ключевую мысль, упомянутую именно в данном тексте.\n"
                    "2. Чётко отличает этот пост от других (даже на смежные темы), избегая общей переформулировки.\n"
                    "3. Может включать вкрапления английских терминов (если релевантно тематике), "
                    "но остаётся в целом на русском языке.\n"
                    "4. Исключает избыточную детализацию — упоминайте только главное (что за технология, законопроект, "
                    "событие, результат и т.д.)."
                ),
            ),
            HumanMessage(content=text),
        ]
        response = self.chat_model.invoke(messages)
        return response.content


# Example usage
summarizer = GigaSummarizer(api_key=main_config.giga_key)
