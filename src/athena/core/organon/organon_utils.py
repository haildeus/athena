from .organon_schemas import PlatformType


def generate_global_message_id(
    platform: PlatformType, chat_id: str, message_id: str | int
) -> str:
    """Generates a globally unique message ID.

    Args:
        platform: The platform the message came from (e.g., "telegram").
        chat_id: The platform-specific chat ID.
        message_id: The platform-specific message ID.

    Returns:
        A globally unique message ID.
    """
    if not isinstance(platform, PlatformType):
        raise ValueError("Platform must be a valid PlatformType")

    return f"{platform.value}_{chat_id}_{message_id}"


def generate_global_cluster_id(
    platform: PlatformType, room_id: str, cluster_id: str
) -> str:
    """Generates a globally unique cluster ID.

    Args:
        platform: The platform the cluster belongs to (e.g., "telegram").
        room_id: The platform-specific room ID.
        cluster_id: The platform-specific cluster ID.

    Returns:
        A globally unique cluster ID.
    """
    if not isinstance(platform, PlatformType):
        raise ValueError("Platform must be a valid PlatformType")

    return f"{platform.value}_{room_id}_{cluster_id}"


def generate_global_user_id(platform: PlatformType, user_id: int) -> str:
    """Generates a globally unique user ID.

    Args:
        platform: The platform the user belongs to (e.g., "telegram").
        user_id: The platform-specific user ID.

    Returns:
        A globally unique user ID.
    """
    if not isinstance(platform, PlatformType):
        raise ValueError("Platform must be a valid PlatformType")
    if not isinstance(user_id, int):
        try:
            user_id = str(user_id)
        except ValueError:
            raise ValueError("User ID must be an integer or a string")

    return f"{platform.value}_{user_id}"
