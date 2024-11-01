import re


def extract_channel_username(link: str) -> str:
    """
    Extracts the username from a Telegram channel link.
    Args:
        link (str): The Telegram channel link or username.
    Returns:
        str: The extracted username or the original link if no username is found.
    """

    link = link.strip()
    if link.startswith("@"):
        return link[1:]

    pattern = r"^(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/(?P<username>[^/?#]+)"
    match = re.match(pattern, link)
    if match:
        return match.group("username")

    return link
